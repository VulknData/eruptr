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
import jinja2
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


def render_kwargs(funcargs, opts, variables, cfg, context):
    j2env = jinja2.Environment(
        loader=jinja2.BaseLoader(),
        block_start_string='$%',
        block_end_string='%$',
        variable_start_string='$$',
        variable_end_string='$$'
    )
    kwargs = {}
    for k, v in funcargs.items():
        t = None
        if v:
            t = j2env.from_string(v).render(
                opts=opts or {},
                vars=variables or {},
                cfg=cfg or {},
                engines=eruptr.modules.__engines__,
                tasks=eruptr.modules.__tasks__,
                context=context
            )
        kwargs[k] = t
    return kwargs


class StepExecutor:
    def __init__(
        self,
        flow,
        steps,
        opts=None,
        variables=None,
        config=None,
        **kwargs
    ):
        self._flow = flow
        self._steps = steps
        self._opts = opts
        self._vars = variables
        self._cfg = config
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
                    pre_kwargs = self._kwargs
                    __context__.next(self._flow, task, pre_kwargs)
                    kwargs = render_kwargs(
                        pre_kwargs,
                        opts=self._opts,
                        variables=self._vars,
                        cfg=self._cfg,
                        context=__context__
                    )
                    __context__.current._kwargs = kwargs
                    ret = __eruptr__[task](**kwargs)
                else:
                    log.debug(f"{__handlers__[task]}({step}, {self._kwargs})")
                    pre_kwargs = {**{'run': step}, **self._kwargs}
                    __context__.next(self._flow, __handlers__[task], pre_kwargs)
                    kwargs = render_kwargs(
                        pre_kwargs,
                        opts=self._opts,
                        variables=self._vars,
                        cfg=self._cfg,
                        context=__context__
                    )
                    __context__.current._kwargs = kwargs
                    ret = __eruptr__[__handlers__[task]](step, **kwargs)
                continue
            task_module = list(step.keys())[0]
            task_args = step[task_module]
            if isinstance(task_args, dict) or isinstance(task_args, list):
                if (
                    isinstance(task_args, list) or
                    isinstance(task_args.get('run'), list)
                ):
                    run_args = []
                    if isinstance(task_args, list):
                        run_args = task_args
                        task_args = {}
                    else:
                        run_args = task_args.pop('run')
                    for t in run_args:
                        log.debug(
                            f"{task_module}({t}, { {**self._kwargs, **task_args} })"
                        )
                        pre_kwargs = {**{'run': t}, **{**self._kwargs, **task_args}}
                        __context__.next(self._flow, task_module, pre_kwargs)
                        kwargs = render_kwargs(
                            pre_kwargs,
                            opts=self._opts,
                            variables=self._vars,
                            cfg=self._cfg,
                            context=__context__
                        )
                        __context__.current._kwargs = kwargs
                        ret = __eruptr__[task_module](**kwargs)
                else:
                    log.debug(
                        f"{task_module}({ {**self._kwargs, **task_args} })"
                    )
                    pre_kwargs = {**self._kwargs, **task_args}
                    __context__.next(self._flow, task_module, pre_kwargs)
                    kwargs = render_kwargs(
                        {**self._kwargs, **task_args},
                        opts=self._opts,
                        variables=self._vars,
                        cfg=self._cfg,
                        context=__context__
                    )
                    __context__.current._kwargs = kwargs
                    ret = __eruptr__[task_module](**kwargs)
            else:
                log.debug(f"{task_module}({task_args} {self._kwargs})")
                pre_kwargs = self._kwargs
                __context__.next(self._flow, task_module, pre_kwargs)
                kwargs = render_kwargs(
                    self._kwargs,
                    opts=self._opts,
                    variables=self._vars,
                    cfg=self._cfg,
                    context=__context__
                )
                __context__.current._kwargs = kwargs
                ret = __eruptr__[task_module](task_args, **kwargs)
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
