# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import subprocess
import functools
import logging
import shlex

import eruptr.utils.path
from eruptr.executors.unixpipe import UnixPipeProcess


log = logging.getLogger()


__virtualname__ = 'io.cmd'


@functools.lru_cache(maxsize=None)
def __virtual__():
    bins = ['gawk', 'sed']
    for binary in bins:
        if not eruptr.utils.path.which(binary):
            return(False, f'The {binary} binary could not be found')
    return __virtualname__


def cmd(
    run=None,
    mode='read',
    env=None,
    __context__=None,
    **kwargs
):
    if mode not in ('read', 'write'):
        raise Exception('Unknown input/output mode specified.')
    proc = UnixPipeProcess(
        shlex.split(run),
        env=env,
        stdin=subprocess.PIPE if mode == 'write' else None,
        stdout=subprocess.PIPE if mode == 'read' else None
    )
    return (proc, __context__)


def shell(
    run=None,
    mode='read',
    shell='/bin/sh',
    env=None,
    __context__=None,
    **kwargs
):
    if mode not in ('read', 'write'):
        raise Exception('Unknown input/output mode specified.')
    proc = UnixPipeProcess(
        [shell, '-c', run],
        env=env,
        stdin=subprocess.PIPE if mode == 'write' else None,
        stdout=subprocess.PIPE if mode == 'read' else None
    )
    return (proc, __context__)


def script(
    run=None,
    mode='read',
    shell='/bin/sh',
    env=None,
    __context__=None,
    **kwargs
):
    if mode not in ('read', 'write'):
        raise Exception('Unknown input/output mode specified.')
    proc = UnixPipeProcess(
        [shell, '-c', run],
        env=env,
        stdin=subprocess.PIPE if mode == 'write' else None,
        stdout=subprocess.PIPE if mode == 'read' else None
    )
    return (proc, __context__)


readcmd = cmd
readshell = shell
readscript = script

writecmd = functools.partial(cmd, mode='write')
writeshell = functools.partial(shell, mode='write')
writescript = functools.partial(script, mode='write')