# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import subprocess
import functools
import itertools
import logging
import os


import eruptr.utils
import eruptr.utils.path


__virtualname__ = 'tasks.pack'


log = logging.getLogger()


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
    'gz': ['gzip', ['-f', '-c']],
    'bz2': ['bzip2', None],
    'lz': ['lz', None],
    'xz': ['xz', None],
}


@eruptr.utils.timer
def pack(
    run,
    connection=None,
    input_file=None,
    output_file=None,
    keep_original=False
):
    method = _MAPPINGS[run][0]
    flags = _MAPPINGS[run][1]
    if output_file is None:
        output_file = input_file  + '.' + run
    cmd = [method]
    if flags:
        cmd += flags
    cmd += [input_file, '>', output_file]
    ret = subprocess.run(' '.join(cmd), stdout=subprocess.PIPE, shell=True)
    if ret.returncode == 0:
        if not keep_original:
            os.remove(input_file)
    return eruptr.utils.default_returner(retcode=ret.returncode) 


gz = lambda **kwargs: pack(run='gz', **kwargs)
bz2 = lambda **kwargs: pack(run='bz2', **kwargs)
lz = lambda **kwargs: pack(run='lz', **kwargs)
xz = lambda **kwargs: pack(run='xz', **kwargs)