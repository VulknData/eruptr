# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import os
import sys
import importlib
import inspect
import glob
import subprocess
import logging
from importlib import util


import eruptr.utils


log = logging.getLogger()


MODULES = ['engines','io', 'locks', 'pipes', 'streams', 'macros', 'formats', 'tasks']

__eruptr__ = {
    'utils.noop': lambda run: eruptr.utils.default_returner(
        retcode=0, data=run, value=run
    )
}

__engines__ = {}
__tasks__ = {}


def load_modules():
    global MODULES, __eruptr__, __engines__, __tasks__
    mod_funcs = {}
    mod_libs = []
    for module in MODULES:
        mod_funcs[module], _mod_libs = _load_module_from_path(
            module, os.path.dirname(os.path.abspath(__file__))
        )
        __eruptr__.update(mod_funcs[module])
        mod_libs += _mod_libs
    for k in sorted(list(mod_funcs.keys())):
        log.debug(
            f'Discovered library {k}: {sorted(list(mod_funcs[k].keys()))}')
    __engines__ = dict(
        (k.split('.', 1)[1], v) for k, v in mod_funcs.get('engines', {}).items()
    )
    __tasks__ = dict(
        (k.split('.', 1)[1], v) for k, v in mod_funcs.get('tasks', {}).items()
    )
    for module in mod_libs:
        module.__eruptr__ = __eruptr__
        module.__engines__ = __engines__
        module.__tasks__ = __tasks__


def _load_module_from_path(ltype, basepath, use_module_name=False):
    mod_funcs = {}
    mod_libs = []
    global __eruptr__, __engines__, __tasks__
    if ltype == 'locks':
        use_module_name = True
    if not os.path.exists(basepath):
        log.error(f'Base path {basepath} does not exist')
        return (mod_funcs, mod_libs)
    mod_path = os.path.join(basepath, ltype)
    if not os.path.exists(mod_path):
        log.error(f'Module path {mod_path} does not exist')
        return (mod_funcs, mod_libs)
    for f in filter(
        lambda x: not x.endswith('/__init__.py'),
        glob.glob(f'{mod_path}/*.py')
    ):
        module_name = f'{ltype}.' + os.path.basename(f)[0:-3]
        virtualname = module_name
        module_spec = importlib.util.spec_from_file_location(module_name, f)
        module = util.module_from_spec(module_spec)
        mod_libs.append(module)
        module_spec.loader.exec_module(module)
        for o in inspect.getmembers(module):
            if o[0] == '__virtual__':
                virtualname = o[1]()
        if not isinstance(virtualname, str):
            log.error(f'Disabling module {module_name} - {virtualname[1]}')
            continue
        for o in inspect.getmembers(module):
            if ((inspect.isfunction(o[1]) or inspect.isclass(o[1])) and 
                o[1].__module__ == module_name and
                not o[0].startswith('_')
            ):
                if use_module_name:
                    mod_funcs[(virtualname or module_name)] = o[1]
                else:
                    mod_funcs[f'{(virtualname or module_name)}.{o[0]}'] = o[1]
    return (mod_funcs, mod_libs)
    