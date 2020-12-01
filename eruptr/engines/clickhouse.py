# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import subprocess
import json
import requests
import urllib3
import pprint
import urllib.parse
import logging
import re
import functools
import collections


import eruptr.modules
import eruptr.utils
import eruptr.utils.path
from eruptr.exceptions import EruptrSQLException
from eruptr.utils import flatten, LogLevels, default_returner


log = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)


__virtualname__ = 'engines.clickhouse'


_VALID_ARGS = {}


@functools.lru_cache(maxsize=None)
def __virtual__():
    bins = ['clickhouse-local', 'clickhouse-client']
    for binary in bins:
        if not eruptr.utils.path.which(binary):
            return(False, f'The {binary} binary could not be found')
    return __virtualname__


@functools.lru_cache(maxsize=None)
def _clickhouse_version():
    try:
        r = subprocess.check_output(['clickhouse-local', '--version'])
        version = (
            r.strip().decode().split('version ')[1].split(' ')[0].split('.')
        )
        return {
            'version': '.'.join(version),
            'major': version[0],
            'minor': version[1],
            'revision': version[2],
            'build': version[3]
        }
    except:
        log.error('Could not determine ClickHouse version')
        return None


@functools.lru_cache(maxsize=None)
def _valid_args(client='clickhouse-client'):
    opts = []
    flags = []
    try:
        r = subprocess.check_output([client, '--help'])
        l = (
            filter(
                lambda s: s.startswith('-') and '--help' not in s, 
                map(
                    lambda s: s.strip(),
                    r.strip().decode().split('Main options:')[1].split('\n')
                )
            )
        )
        c = re.compile(r'.*?(--(?P<option>[^\s]*))')
        for o in l:
            m = c.match(o)
            if m:
                if 'arg' in o:
                    opts.append(m.group('option'))
                else:
                    flags.append(m.group('option'))
    except:
        log.error('Could not determine ClickHouse flags')
    flags = sorted(flags)
    opts = sorted(opts)
    log.debug(f'Discovered {client} flags: {flags}')
    log.debug(f'Discovered {client} options: {opts}')
    return (flags, opts)


@functools.lru_cache(maxsize=None)
def _parse_clickhouse_uri(uri):
    try:
        m = re.match(
            r"^((?P<scheme>https?|clickhouse)://)?"
            r"((?P<username>.*):(?P<password>.*)@)?"
            r"(?P<host>[^:/]*)(:(?P<port>.*))?(/(?P<database>.*))?$",
            uri
        )
        conn_args = {
            'scheme': m.group('scheme') or 'clickhouse',
            'user': m.group('username') or 'default',
            'password': m.group('password'),
            'host': m.group('host') or 'localhost',
            'database': m.group('database') or 'default'
        }
        conn_args['port'] = (
            m.group('port') or 
            ('9000' if conn_args['scheme'] == 'clickhouse' else '8123')
        )
        log.debug(
            'Parsed URI: {} -> {}'.format(uri, _pformat_uri(**conn_args))
        )
        return conn_args
    except:
        log.error(f'Unable to parse clickhouse URI - {uri}')
    return None


@functools.lru_cache(maxsize=None)
def _parse_clickhouse_insert(sql=None, target_table=None, input_format=None):
    __eruptr__ = eruptr.modules.__eruptr__
    query = None
    if input_format:
        input_format = __eruptr__[input_format].format
    select = ''
    try:
        if sql is None and target_table is None:
            raise EruptrModuleArgumentError(
                'Parameters query and target_table cannot both be None'
            )
        if sql:
            query = flatten(sql)
            m = re.match(
                r"^(\s*?INSERT\s*INTO\s*(?P<target_table>\S*)\s*)?"
                r"(?P<select_query>.*?)(\s*FORMAT\s*(?P<input_format>\S*)\s*?)?$",
                query,
                re.IGNORECASE
            )
            if m.group('select_query'):
                select = m.group('select_query').strip()
            else:
                raise EruptrModuleArgumentError(
                    'Unable to determine SELECT query'
                )
            if not target_table:
                if m.group('target_table'):
                    target_table = m.group('target_table').strip()
                else:
                    raise EruptrModuleArgumentError(
                        'Unable to determine destination table for insert'
                    )
            if not re.match(
                r"^\s?INSERT\sINTO\s([\S]*).*",
                query,
                re.IGNORECASE
            ):
                query = f'INSERT INTO {target_table} {sql}'
            if not input_format:
                if m.group('input_format'):
                    input_format = m.group('input_format').strip()
                else:
                    raise EruptrModuleArgumentError(
                        'Unable to determine input format for insert'
                    )
            if not re.match(r".*?\sFORMAT\s*([\S]*).*", query, re.IGNORECASE):
                query = f'{sql} FORMAT {input_format}'
    except:
        raise EruptrModuleArgumentError(
            'Unable to extract query parameters. This may be a bug - please report so it can be fixed'
        )
    return {
        'query': query,
        'select': select,
        'target_table': target_table,
        'input_format': input_format
    }


@functools.lru_cache(maxsize=None)
def _pformat_uri(scheme, user, host, port, database, **kwargs):
    return f'{scheme}://{user}@{host}:{port}/{database}'


class ClickHouseModel:
    def __init__(self, sql):
        self._sql = sql
        self._parse_definition()

    @staticmethod
    def _parse_indexes(object_def):
        indexes = collections.OrderedDict()
        index_raw = [i for i in object_def if i.startswith('INDEX ')]
        for k in index_raw:
            if k.startswith('INDEX'):
                key = k.split(' ')[1]
                indexes[key] = ' '.join(k.split(' ')[2:])
        return indexes

    @staticmethod
    def _parse_columns(object_def):
        re_column_def = (
            r'(?P<column_name>`[^`]*`|"[^"]*"|[^` ()"]*)\s*'
            r'(?P<data_type>.*?)(\s*)?'
            r'(?P<expression>(DEFAULT|MATERIALIZED|ALIAS).*?)?(\s*)?'
            r'(?P<codec>CODEC.*?)?(\s*)?'
            r'(?P<comment>COMMENT.*?)?(\s*)?'
            r'$'
        )
        columns = collections.OrderedDict()
        object_def = [c for c in object_def if not c.startswith('INDEX')]
        for k in object_def:
            try:
                n = re.match(re_column_def, k, re.IGNORECASE | re.DOTALL)
                c = n.group('column_name')
                columns[c] = {
                    'data_type': n.group('data_type'),
                    'comment': n.groupdict().get('comment'),
                    'codec': n.groupdict().get('codec'),
                    'expression': n.groupdict().get('expression')
                }
                columns[c]['has_default'] = False
                if not columns[c]['expression']:
                    columns[c]['storage'] = 'NORMAL'
                else:
                    if columns[c]['expression'].lower().startswith('alias '):
                        columns[c]['storage'] = 'ALIAS'
                    elif columns[c]['expression'].lower().startswith('materialized '):
                        columns[c]['storage'] = 'MATERIALIZED'
                    elif columns[c]['expression'].lower().startswith('default '):
                        columns[c]['storage'] = 'NORMAL'
                        columns[c]['has_default'] = True
                    else:
                        columns[c]['storage'] = 'OTHER'
            except:
                pass
        return columns

    @staticmethod
    def _parse_settings(settings):
        ret = collections.OrderedDict()
        if settings:
            ret = collections.OrderedDict(
                s.strip().split(' = ') 
                for s in settings.strip().split(',\n')
            )
        return ret

    def _parse_definition(self):
        re_object_def = (
            r'^(?P<statement_type>CREATE)\s*'
            r'(?P<object_type>TABLE|VIEW|LIVE\s*VIEW|MATERIALIZED\s*VIEW|DICTIONARY)\s*'
            r'(?P<if_not_exists>IF\s*NOT\s*EXISTS)?(\s*)?'
            r'(?P<database>`[^`]*`|"[^"]*"|[^` ()"]*)\..*?'
            r'(?P<table>`[^`]*`|"[^"]*"|[^` ()"]*)(\s*?)'
            r'(?P<definition>.*)$'
        )
        m = re.match(re_object_def, self._sql, re.IGNORECASE | re.DOTALL)
        obj_type = m.group('object_type').strip()
        obj = {
            'database': m.group('database').strip(),
            'name': m.group('table').strip(),
            'type': obj_type,
            'if_not_exists': m.group('if_not_exists') is not None
        }
        if obj_type == 'TABLE':
            detail = ClickHouseModel._parse_table_definition(
                m.group('definition')
            )
        elif obj_type in ('VIEW', 'MATERIALIZED VIEW'):
            detail = ClickHouseModel._parse_view_definition(
                m.group('definition')
            )
            detail['engine'] = (
                'View' if obj_type == 'VIEW' else 'MaterializedView'
            )
        obj.update(detail)
        obj['object'] = obj['database'] + '.' + obj['name']
        self.obj = obj

    @staticmethod
    def _parse_table_definition(sql):
        re_table_def = (
            r'(\s*?)'
            r'\((?P<object_definition>.*)\)\s*(?=ENGINE)'
            r'ENGINE\s*?=\s*?(?P<engine>.*?)(?=SETTINGS|$)'
            r'(SETTINGS\s*(?P<settings>.*?))?(\s*?)'
            r'$'
        )
        m = re.match(re_table_def, sql, re.IGNORECASE | re.DOTALL)
        object_def = [
            c.strip() for c in m.group('object_definition').strip().split(',\n')
        ]
        indexes = ClickHouseModel._parse_indexes(object_def)
        columns = ClickHouseModel._parse_columns(object_def)
        settings = ClickHouseModel._parse_settings(m.group('settings'))
        obj = {
            'columns': columns,
            'indexes': indexes,
            'engine': m.group('engine').strip(),
            'requires': [],
            'settings': settings
        }
        return obj

    def __str__(self):
        return pprint.pformat(self.obj, width=100, compact=True)

    @staticmethod
    def _parse_view_definition(sql):
        re_view_def = (
            r'(\s*?)'
            r'\((?P<object_definition>.*?)\)\s*(?=AS)'
            r'AS\s*(?P<query>.*?)(\s*)?'
            r'(SETTINGS\s*(?P<settings>.*?))?(\s*)?'
            r'$'
        )
        m = re.match(re_view_def, sql, re.IGNORECASE | re.DOTALL)
        object_def = [
            c.strip() for c in m.group('object_definition').strip().split(',\n')
        ]
        columns = ClickHouseModel._parse_columns(object_def)
        settings = ClickHouseModel._parse_settings(m.group('settings'))
        obj = {
            'columns': columns,
            'requires': [],
            'query': m.group('query'),
            'settings': settings
        }
        return obj

    def render(self):
        obj = self.obj
        ret = f"CREATE {obj['type']} IF NOT EXISTS {obj['object']}"
        columns = None
        if len(obj['columns']) > 0:
            columns = []
            for k,v in obj['columns'].items():
                c = f"    {k} {v['data_type']}"
                if v['expression']:
                    c += ' ' + v['expression']
                if v['codec']:
                    c += ' ' + v['codec']
                if v['comment']:
                    c += ' ' + v['comment']
                columns.append(c)
            ret += '\n(\n' + f',\n'.join(columns) + '\n)'
        if obj['engine'] and obj['engine'] not in ('View', 'MaterializedView'):
            ret += f"\nENGINE = {obj['engine']}"
        if obj['settings']:
            settings = [f'{k} = {v}' for k, v in obj['settings'].items()]
            ret += f"\nSETTINGS {','.join(settings)}"
        return ret

    def diff(self, other):
        d = {}
        for k in self.obj.keys():
            if k not in other.obj.keys():
                d[k] = (self.obj[k], None)
            else:
                if self.obj[k] != other.obj[k]:
                    if k not in ('columns', 'settings', 'indexes'):
                        d[k] = (self.obj[k], other.obj[k])
                    else:
                        for i, v in self.obj[k].items():
                            if i not in other.obj[k]:
                                if k not in d:
                                    d[k] = collections.OrderedDict()
                                d[k][i] = (self.obj[k][i], None)
                            else:
                                if other.obj[k][i] != v:
                                    if k not in d:
                                        d[k] = collections.OrderedDict()
                                    d[k][i] = (v, other.obj[k][i])
        for k in other.obj.keys():
            if k not in self.obj.keys():
                d[k] = (None, other.obj[k])
            else:
                if k in ('columns', 'settings', 'indexes'):
                    if self.obj[k] != other.obj[k]:
                        for i, (j, v) in enumerate(other.obj[k].items()):
                            if j not in self.obj[k]:
                                if k not in d:
                                    d[k] = collections.OrderedDict()
                                iloc = 'FIRST'
                                if i > 0:
                                    iloc = 'AFTER ' + list(other.obj[k])[i-1]
                                d[k][j] = (None, v, iloc)
        return d

    def migrate(self, other):
        sql = []
        d = self.diff(other)
        if 'engine' in d:
            log.warning('Unable to migrate changes to ENGINE')
        if 'type' in d:
            log.warning('Unable to migrate changes to object type')
        if 'columns' in d:
            for c, v in d['columns'].items():
                s = f"ALTER TABLE {self.obj['object']} "
                if v[1] is None:
                    s += f"DROP COLUMN IF EXISTS {c}"
                else:
                    s += (
                        'ADD COLUMN IF NOT EXISTS' 
                        if v[0] is None else 'MODIFY COLUMN'
                    )
                    s += f" {c} {v[1]['data_type']}"
                    if v[0] is None:
                        s += f' {v[2]}'
                    if v[1]['expression']:
                        s += f" {v[1]['expression']}"
                    if v[1]['codec']:
                        s += f" {v[1]['codec']}"
                    if v[1]['comment']:
                        s += f" {v[1]['comment']}"
                sql.append(s)
        if 'indexes' in d:
            for c, v in d['indexes'].items():
                if v[0] is not None:
                    s = f"ALTER TABLE {self.obj['object']} DROP INDEX {c}"
                    sql.append(s)
                if v[1] is not None:
                    s = f"ALTER TABLE {self.obj['object']} ADD INDEX {c} {v[1]}"
                    sql.append(s)
        if 'settings' in d:
            for c, v in d['settings'].items():
                if v[1] is not None:
                    s = f"ALTER TABLE {self.obj['object']} MODIFY SETTING "
                    s += f"{c} = {v[1]}"
                    sql.append(s)
        return sql

@functools.lru_cache(maxsize=None)
def _clickhouse_cli(
    query,
    client='clickhouse-client',
    context='execute',
    **kwargs
):
    global _VALID_ARGS
    if 'output_format' in kwargs:
        kwargs['format'] = kwargs['output_format']    
        del kwargs['output_format']
    if 'scheme' in kwargs:
        del kwargs['scheme']
    if client not in ('clickhouse-client', 'clickhouse-local'):
        raise Exception('Invalid ClickHouse client program specified')
    if client not in _VALID_ARGS:
        _VALID_ARGS[client] = _valid_args(client)
    if not (set(kwargs.keys()).issubset(set(_VALID_ARGS[client][1]))):
        log.debug(kwargs)
        raise Exception('Invalid kwargs option provided')
    cmd = [client, '-q', query]
    for k, v in kwargs.items():
        if v:
            cmd += [f'--{k}', v]
    log.debug('Built CLI: ' + flatten((' '.join(cmd))))
    return cmd


def _clickhouse_http(query, insecure=True, context='execute', **kwargs):
    @functools.lru_cache(maxsize=None)
    def _build_http_client(insecure=True):
        http_kwargs = {}
        if insecure:
            http_kwargs['cert_reqs'] = 'CERT_NONE'
            requests.packages.urllib3.disable_warnings()
        return urllib3.PoolManager(**http_kwargs)

    http_client = _build_http_client(insecure)
    host = '{}://{}'.format(kwargs['scheme'], kwargs['host'])
    port = kwargs['port'] or '8123'
    headers = {}
    if kwargs['user'] and kwargs['password']:
        headers = {
            'X-ClickHouse-User': kwargs['user'],
            'X-ClickHouse-Key': kwargs['password']
        }
    body = f'{query}'
    if (
        query.strip().lower().startswith('select') or 
        query.strip().lower().startswith('with') or
        query.strip().lower().startswith('show')
    ):
        body = f'{body} FORMAT JSON'
    log.log(
        LogLevels.SQL,
        f'Executing ({context} @ {_pformat_uri(**kwargs)}): {flatten(body)}'
    )
    masked_urlparams = ['scheme','user','password','host','database','port']
    urlparams = {k: v for k, v in kwargs.items() if k not in masked_urlparams}
    r = http_client.request(
        'POST',
        f'{host}:{port}/?' + urllib.parse.urlencode(urlparams),
        headers=headers,
        body=body
    )
    if r.status != 200:
        raise Exception(r.data.decode('UTF8'))
    return eruptr.utils.default_returner(
        retcode=(not int(r.status == 200)),
        data=r.data.decode('UTF8')
    )


@eruptr.utils.timer
def local(query, output_format='JSON', context='local', **kwargs):
    if 'output-format' not in kwargs:
        kwargs['format'] = output_format
    cli = _clickhouse_cli(query, 'clickhouse-local', **kwargs)
    log.log(
        LogLevels.SQL,
        f'Executing ({context} @ local): {flatten(query)}'
    )
    p = subprocess.run(
        cli,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    if p.returncode != 0:
        raise EruptrSQLException(p.stderr.strip())
    return eruptr.utils.default_returner(
        retcode=p.returncode,
        data=json.loads(p.stdout)['data'] if output_format == 'JSON' else p.stdout
    )


def execute(
    query,
    connection=None,
    output_format='JSONEachRow',
    insecure=True,
    context='execute',
    **kwargs
):
    if not connection and 'connection' in kwargs:
        connection = kwargs.pop('connection')
    if not connection:
        return local(
            query,
            output_format=output_format,
            context=context,
            **kwargs
        )
    conn_args = _parse_clickhouse_uri(connection)
    if conn_args['scheme'] == 'clickhouse':
        kwargs.update(conn_args)
        cli = _clickhouse_cli(
            query,
            'clickhouse-client',
            output_format=output_format,
            **kwargs
        )
        log.log(
            LogLevels.SQL,
            f'Executing ({context} @ {_pformat_uri(**kwargs)}): {flatten(query)}'
        )
        p = subprocess.run(
            cli,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        if p.returncode != 0:
            raise EruptrSQLException(p.stderr.strip())
        return eruptr.utils.default_returner(
            retcode=p.returncode,
            data=p.stdout
        )
    elif conn_args['scheme'] in ('http', 'https'):
        kwargs.update(conn_args)
        return _clickhouse_http(query, insecure, **kwargs)
    raise Exception('Invalid connection scheme specified')


def select(query, connection=None, insecure=True, **kwargs):
    p = execute(
        query,
        connection=connection,
        insecure=insecure,
        context='select',
        **kwargs
    )
    return p['ret']


def evaluate(run, connection=None):
    if isinstance(run, str) and run.strip().lower()[0:6] == 'select':
        raw = execute(
            query=run,
            connection=connection,
            output_format='TSV',
            context='evaluate'
        )
        if raw['retcode'] != 0:
            raise Exception('Could not evaluate args')
        r = [x.split('\t') for x in raw['ret'].strip().split('\n')]
        if len(r) > 1:
            return r
        else:
            if len(r[0]) > 1:
                return r[0]
            else:
                return r[0][0]
    else:
        return run
