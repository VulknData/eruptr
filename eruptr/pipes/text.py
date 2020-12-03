# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import functools
import logging
import shlex

import eruptr.utils.path
from eruptr.executors.unixpipe import UnixPipeProcess


log = logging.getLogger()


__virtualname__ = 'pipes.text'


@functools.lru_cache(maxsize=None)
def __virtual__():
    bins = ['gawk', 'awk', 'sed', 'grep', 'head', 'tail']
    for binary in bins:
        if not eruptr.utils.path.which(binary):
            return(False, f'The {binary} binary could not be found')
    return __virtualname__


def awk(run=None, env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess(['awk', run], env=env)
    return (proc, __context__)


def grep(run=None, env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess(['grep', run], env=env)
    return (proc, __context__)


def head(run=None, env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess(['head', '-n{run}'], env=env)
    return (proc, __context__)


def match(run=None, env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess(['awk', f'/{run}/'], env=env)
    return (proc, __context__)


def replace(
    run=None,
    search='\\n',
    replace='\\n',
    env=None,
    __context__=None,
    **kwargs
):
    cmd = f"awk 'BEGIN {{ RS=\"{search}\"; ORS=\"{replace}\" }} 1'"
    proc = UnixPipeProcess(shlex.split(cmd), env=env)
    return (proc, __context__)


def sed(run=None, env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess(['sed', run], env=env)
    return (proc, __context__)


def tail(run=None, env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess(['tail', '-n{run}'], env=env)
    return (proc, __context__)