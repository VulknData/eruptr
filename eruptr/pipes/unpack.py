# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import functools
import logging
import itertools


import eruptr.utils.path
from eruptr.executors.unixpipe import UnixPipeProcess


log = logging.getLogger()


__virtualname__ = 'pipes.unpack'


@functools.lru_cache(maxsize=None)
def __virtual__():
    bins = list(
        itertools.chain.from_iterable(
            [[v[0]] for v in list(_MAPPINGS.values())]
        )
    )
    for binary in bins:
        if not eruptr.utils.path.which(binary):
            return(False, f'The {binary} binary could not be found')
    return __virtualname__


_MAPPINGS = {
    'gz': ['zcat', None],
    'bz2': ['bzcat', None],
    'lz': ['xz', ['--format=lzma', '--decompress', '--stdout']],
    'xz': ['xz', ['--decompress', '--stdout']]
}


def unpack(run=None, flags=None, env=None, __context__=None, **kwargs):
    method = _MAPPINGS[run or 'gz'][0]
    cmd = [method]
    if flags:
        cmd += flags
    proc = UnixPipeProcess(cmd, env=env)
    return (proc, __context__)


gz = lambda run, **kwargs: unpack(run='gz', **kwargs)
bz2 = lambda run, **kwargs: unpack(run='bz2', **kwargs)
lz = lambda run, **kwargs: unpack(run='lz', **kwargs)
xz = lambda run, **kwargs: unpack(run='xz', **kwargs)
