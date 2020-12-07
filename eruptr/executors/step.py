# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import os
import importlib
import inspect
import glob
import subprocess
import logging
from importlib import util


import eruptr.config
import eruptr.modules
from eruptr.utils import flatten


log = logging.getLogger()


def _default_str_task(step):
    __eruptr__ = eruptr.modules.__eruptr__
    s = step.strip()
    if s in __eruptr__.keys():
        return s
    elif (
        s.lower().startswith('insert') or
        s.lower().startswith('delete') or
        s.lower().startswith('update') or
        s.lower().startswith('alter') or
        s.lower().startswith('truncate') or
        s.lower().startswith('create') or
        s.lower().startswith('drop')
    ):
        return 'task_sql_execute'
    elif s.lower().startswith('select'):
        return 'task_sql_select'
    return 'task_command'


class StepExecutor:
    def __init__(self, flow, steps, **kwargs):
        self._flow = flow
        self._steps = steps
        self._kwargs = kwargs

    def execute(self):
        log.info(str(self))
        __eruptr__ = eruptr.modules.__eruptr__
        __handlers__ = eruptr.config.__handlers__
        __context__ = eruptr.modules.__context__
        task = None
        for step in self._steps:
            if isinstance(step, str):
                task = _default_str_task(step)
                if task == step:
                    log.debug(f"{task}({self._kwargs})")
                    __context__.next(self._flow, task, self._kwargs)
                    ret = __eruptr__[task](**self._kwargs)
                else:
                    log.debug(f"{__handlers__[task]}({step}, {self._kwargs})")
                    __context__.next(
                        self._flow,
                        __handlers__[task],
                        {**{'run': step}, **self._kwargs}
                    )
                    ret = __eruptr__[__handlers__[task]](step, **self._kwargs)
                continue
            task_module = list(step.keys())[0]
            task_args = step[task_module]
            if isinstance(task_args, dict):
                if isinstance(task_args.get('run'), list):
                    run_args = task_args.pop('run')
                    for t in run_args:
                        log.debug(
                            f"{task_module}({t}, { {**self._kwargs, **task_args} })"
                        )
                        __context__.next(
                            self._flow,
                            task_module,
                            {**{'run': t}, **{**self._kwargs, **task_args}}
                        )
                        ret = __eruptr__[task_module](
                            t,
                            **{**self._kwargs, **task_args}
                        )
                else:
                    log.debug(
                        f"{task_module}({ {**self._kwargs, **task_args} })"
                    )
                    __context__.next(
                        self._flow,
                        task_module,
                        {**self._kwargs, **task_args}
                    )
                    ret = __eruptr__[task_module](
                        **{**self._kwargs, **task_args}
                    )
            else:
                log.debug(f"{task_module}({task_args} {self._kwargs})")
                __context__.next(self._flow, task_module, self._kwargs)
                ret = __eruptr__[task_module](task_args, **self._kwargs)
            if ret.retcode != 0:
                print(ret)
                raise Exception('Failed')
        return 0

    def __str__(self):
        __handlers__ = eruptr.config.__handlers__
        if not self._steps:
            return 'StepExecutor: Nothing to do'
        d = []
        for s in self._steps:
            if isinstance(s, str):
                task = _default_str_task(s)
                if s == task:
                    d.append(f'{s}()')
                else:
                    d.append(f"{__handlers__[task]}({flatten(s)})")
            elif isinstance(s, dict):
                func = list(s.keys())[0]
                if isinstance(s[func], str):
                    d.append(f'{func}({flatten(s[func])})')
                elif isinstance(s[func], dict):
                    if isinstance(s[func].get('run'), list):
                        for r in s[func]['run']:
                            d.append(f'{func}({flatten(r)})')
                    else:
                        d.append(f'{func}({s[func]})')
        return 'StepExecutor: ' + ' -> '.join(d)
