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


__virtualname__ = 'pipes.cmd'


@functools.lru_cache(maxsize=None)
def __virtual__():
    bins = ['gawk', 'sed']
    for binary in bins:
        if not eruptr.utils.path.which(binary):
            return(False, f'The {binary} binary could not be found')
    return __virtualname__


def cmd(run=None, env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess(shlex.split(run), env=env)
    return (proc, __context__)


def shell(run=None, shell='/bin/sh', env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess([shell, '-c', run], env=env)
    return (proc, __context__)


def script(run=None, shell='/bin/sh', env=None, __context__=None, **kwargs):
    proc = UnixPipeProcess([shell, '-c', run], env=env)
    return (proc, __context__)