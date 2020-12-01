# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import functools
import logging
import subprocess
import re
import sys

import eruptr.utils.path
from eruptr.utils import flatten
from eruptr.exceptions import EruptrModuleArgumentError
from eruptr.executors.unixpipe import UnixPipeProcess
from eruptr.engines.clickhouse import (
    _parse_clickhouse_uri,
    _parse_clickhouse_insert
)


log = logging.getLogger()


__virtualname__ = 'io.clickhouse'


@functools.lru_cache(maxsize=None)
def __virtual__():
    bins = ['clickhouse-client', 'clickhouse-local']
    for binary in bins:
        if not eruptr.utils.path.which(binary):
            return(False, f'The {binary} binary could not be found')
    return __virtualname__


def local(
    run=None,
    format=None,
    env=None,
    __context__=None,
    **kwargs
):
    if run is None:
        raise Exception('run parameter cannot be None')
    cmd = ['clickhouse-local', '--query', run]
    if format:
        cmd += ['--output-format', format]
    proc = UnixPipeProcess(cmd, env=env, stdout=subprocess.PIPE, stdin=None)
    return (proc, __context__)


def select(
    run=None,
    connection=None,
    format=None,
    env=None,
    __context__=[],
    **kwargs
):
    options = {k:v for k,v in kwargs.items()}
    _conn = _parse_clickhouse_uri(connection)
    cmd = ['clickhouse-client', '-q', run]
    if format:
        cmd += ['--output-format', format]
    for k, v in _conn.items():
        if v and k != 'scheme':
            if k == 'port':
                v = '9000'
            cmd += [f'--{k}', v]
    for k, v in options.items():
        cmd += [f'--{k}', str(v)]
    proc = UnixPipeProcess(cmd, env=env, stdout=subprocess.PIPE, stdin=None)
    return (proc, __context__)


def write(
    run=None,
    connection=None,
    table=None,
    format=None,
    columns=None,
    env=None,
    __context__=[],
    **kwargs
):
    query = run
    if not run and columns:
        if isinstance(columns, list):
            query = f"SELECT * FROM input('{', '.join(columns)}')"
        else:
            query = f"SELECT * FROM input('{columns}')"
    options = {k:v for k,v in kwargs.items()}
    unpacked_args = _parse_clickhouse_insert(query, table, format)
    _conn = _parse_clickhouse_uri(connection)
    sql = "INSERT INTO {} {} FORMAT {}".format(
        unpacked_args['target_table'],
        unpacked_args['select'],
        unpacked_args['input_format']
    )
    cmd = ['clickhouse-client', '-q', sql]
    for k, v in _conn.items():
        if v and k != 'scheme':
            if k == 'port':
                v = '9000'
            cmd += [f'--{k}', str(v)]
    for k, v in options.items():
        cmd += [f'--{k}', str(v)]

    proc = UnixPipeProcess(cmd, env=env, stdout=None)
    return (proc, __context__)
