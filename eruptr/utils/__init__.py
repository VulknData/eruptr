# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import random
import sys
import logging
import functools
import importlib
from types import SimpleNamespace
from timeit import default_timer
from importlib import util


from eruptr.exceptions import EruptrPythonException


log = logging.getLogger()


class LogLevels:
    SQL = 11


def load_python(code):
    if code.strip() == '':
        raise EruptrPythonException(
            'Invalid Python block provided - cannot be an empty string'
        )
    try:
        mod_name = 'python' + str(random.randint(1,1000000))
        spec = util.spec_from_loader(mod_name, loader=None)
        this_module = util.module_from_spec(spec)
        exec(code.strip(), this_module.__dict__)
        sys.modules[mod_name] = this_module
    except:
        raise EruptrPythonException(
            'Invalid Python block provided - unable to dynamically load'
        )
    return this_module


@functools.lru_cache(maxsize=None)
def flatten(string):
    return ' '.join(map(str.strip, string.split('\n')))


def timer(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        import eruptr.config
        if eruptr.config.timing:
            start = default_timer()
        r = f(*args, **kwargs)
        if eruptr.config.timing:
            call = f'({f}, {args}, {kwargs})'[0:87]
            print(
                'Timing: {}... took {:0.3f} ms'.format(
                    call,
                    abs(default_timer() - start)*1000
                )
            )
        return r
    return wrap


def default_returner(retcode=0, data=None, value=None):
    v = None
    if value is None and data is not None:
        if isinstance(data, str):
            v = [x.split('\t') for x in data.strip().split('\n')]
        else:
            v = data
        if len(v) > 1:
            value = v
        else:
            if len(v[0]) > 1:
                value = v[0]
            else:
                value = v[0][0]
    return SimpleNamespace(retcode=retcode, data=data, value=value)