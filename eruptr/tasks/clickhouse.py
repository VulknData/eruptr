import os
import logging
import subprocess


try:
    from shlex import join as shlex_join
except ImportError:
    def shlex_join(cmd):
        return ' '.join([f'"{c}"' if ' ' in c else c for c in cmd])


import eruptr.utils
from eruptr.engines.clickhouse import _parse_clickhouse_uri
from eruptr.engines.clickhouse import _parse_clickhouse_insert


log = logging.getLogger()


@eruptr.utils.timer
def execute(run, tag=None, connection=None, insecure=True, **kwargs):
    raw = __engines__['clickhouse.execute'](
        query=run,
        connection=connection,
        output_format='TSV',
        insecure=insecure,
        **kwargs
    )
    if raw.retcode != 0:
        raise Exception('Could not evaluate args')
    return raw


@eruptr.utils.timer
def export(
    run,
    tag=None,
    connection=None,
    output_format='formats.clickhouse.CSV',
    path=None,
    overwrite=False,
    insecure=True
):
    if os.path.exists(path):
        if overwrite:
            os.remove(path)
        else:
            raise Exception(f'{path} exists and overwrite=False')
    q = f"{run} INTO OUTFILE '{path}' FORMAT {__eruptr__[output_format].format}"
    raw = __engines__['clickhouse.execute'](query=q, connection=connection)
    if raw.retcode != 0:
        raise Exception('Could not evaluate args')
    return raw


@eruptr.utils.timer
def import_file(
    run=None,
    tag=None,
    connection=None,
    table=None,
    input_format='formats.clickhouse.CSV',
    path=None,
    insecure=True
):
    unpacked_args = _parse_clickhouse_insert(
        sql=run,
        target_table=table,
        input_format=input_format
    )
    uri = _parse_clickhouse_uri(connection)
    sql = 'INSERT INTO {} {} FORMAT {}'.format(
        unpacked_args['target_table'],
        unpacked_args['select'],
        unpacked_args['input_format']
    )
    cmd = ['cat', path, '|', 'clickhouse-client', '-q', sql]
    for k, v in uri.items():
        if v and k != 'scheme':
            if k == 'port':
                v = '9000'
            cmd += [f'--{k}', v]
    ret = subprocess.run(shlex_join(cmd), stdout=subprocess.PIPE, shell=True)
    return eruptr.utils.default_returner(retcode=ret.returncode) 


@eruptr.utils.timer
def local(run, tag=None):
    raw = __engines__['clickhouse.local'](query=run, output_format='TSV')
    if raw.retcode != 0:
        raise Exception('Could not evaluate args')
    return raw


@eruptr.utils.timer
def select(run, tag=None, connection=None, insecure=True):
    raw = __engines__['clickhouse.execute'](
        query=run,
        connection=connection,
        output_format='TSV',
        insecure=insecure
    )
    if raw.retcode != 0:
        raise Exception('Could not evaluate args')
    return raw
