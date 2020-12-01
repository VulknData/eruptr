# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import os
import logging
import hashlib
import tempfile
import random
import importlib
import sys
import textwrap
from importlib import util


import eruptr.utils


log = logging.getLogger()


__virtualname__ = 'tasks.python'


@eruptr.utils.timer
def run(run=None, tag=None, **kwargs):
    func_name = 'run_' + hashlib.sha256(run).hexdigest()
    func_code = f'def {func_name}(**kwargs):\n' + textwrap.indent(run, 4*' ')
    mod_name = 'tasks_python_' + str(random.randint(1,1000000))
    spec = util.spec_from_loader(mod_name, loader=None)
    this_module = util.module_from_spec(spec)
    exec(func_code, this_module.__dict__)
    sys.modules[mod_name] = this_module
    ret = this_module.__dict__[func_name](**kwargs)
    return eruptr.utils.default_returner(retcode=ret)
