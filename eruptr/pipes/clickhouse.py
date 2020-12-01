# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import functools
import logging

import eruptr.utils.path
from eruptr.executors.unixpipe import UnixPipeProcess


log = logging.getLogger()


__virtualname__ = 'pipes.clickhouse'


@functools.lru_cache(maxsize=None)
def __virtual__():
    bins = ['clickhouse-local', 'clickhouse-client']
    for binary in bins:
        if not eruptr.utils.path.which(binary):
            return(False, f'The {binary} binary could not be found')
    return __virtualname__


def local(
    run,
    structure=None,
    input_format=None,
    output_format=None,
    env=None,
    __context__=None,
    **kwargs
):
    cmd = ['clickhouse-local', '--query', run]
    if structure:
        if isinstance(structure, list):
            cmd += ['--structure', ','.join(structure)]
        else:
            cmd += ['--structure', structure]
    if input_format:
        cmd += ['--input-format', input_format]
    if output_format:
        cmd += ['--output-format', output_format]
    proc = UnixPipeProcess(cmd, env=env)
    return (proc, __context__)