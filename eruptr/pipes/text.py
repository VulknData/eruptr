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


def awk(run=None, env=None, **kwargs):
    return UnixPipeProcess(['awk', run], env=env)


def grep(run=None, env=None, **kwargs):
    return UnixPipeProcess(['grep', run], env=env)


def head(run=None, env=None, **kwargs):
    return UnixPipeProcess(['head', '-n{run}'], env=env)


def match(run=None, env=None, **kwargs):
    return UnixPipeProcess(['awk', f'/{run}/'], env=env)


def replace(run=None, search='\\n', replace='\\n', env=None, **kwargs):
    cmd = f"awk 'BEGIN {{ RS=\"{search}\"; ORS=\"{replace}\" }} 1'"
    return UnixPipeProcess(shlex.split(cmd), env=env)


def sed(run=None, env=None, **kwargs):
    return UnixPipeProcess(['sed', run], env=env)


def tail(run=None, env=None, **kwargs):
    return UnixPipeProcess(['tail', '-n{run}'], env=env)