# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only

import sys
import subprocess
import functools
import logging

import eruptr.utils.path
from eruptr.executors.unixpipe import UnixPipeProcess


log = logging.getLogger()


__virtualname__ = 'io.file'


@functools.lru_cache(maxsize=None)
def __virtual__():
    bins = ['cat', 'dd', 'tee']
    for binary in bins:
        if not eruptr.utils.path.which(binary):
            return(False, f'The {binary} binary could not be found')
    return __virtualname__


def read(run=None, env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess(['cat', run], env=env, stdin=None)
    return (proc, __context__)


def write(run=None, env=None, __context__=None, **kwargs):
    cmd = ['dd', 'status=none', f'of={run}']
    proc = UnixPipeProcess(cmd, env=env, stdout=None)
    return (proc, __context__)


def stdin(run=None, env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess(['cat'], env=env, stdin=sys.stdin)
    return (proc, __context__)


def stdout(run=None, env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess(['tee'], env=env, stdout=sys.stdout)
    return (proc, __context__)
