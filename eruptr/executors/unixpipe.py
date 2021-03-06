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
import jinja2
from importlib import util

import eruptr.config
import eruptr.modules
from eruptr.utils import flatten
from eruptr.executors import Context


log = logging.getLogger()


class UnixPipeProcess:
    def __init__(
        self,
        cmd,
        env=None,
        on_start=None,
        on_end=None,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        context=None
    ):
        self._cmd = cmd
        self.env = env
        self._on_start = on_start
        self._on_end = on_end
        self.stdin = stdin
        self.stdout = stdout
        self.context = context or {}

    @property
    def cmd(self):
        if isinstance(self._cmd, str):
            return [self._cmd]
        elif isinstance(self._cmd, list):
            return self._cmd
        else:
            return self._cmd()

    def on_start_hook(self):
        if self._on_start:
            return self._on_start()

    def on_end_hook(self):
        if self._on_end:
            return self._on_end()

    def __str__(self):
        return (
            f'UnixPipeProcess({self.cmd}, {self.env}, {self.on_start_hook}, '
            f'{self.on_end_hook}, {self.stdin}, {self.stdout}, {self.context})'
        )


def build_dag_task(process, **kwargs):
    stages = []

    __eruptr__ = eruptr.modules.__eruptr__
    __handlers__ = eruptr.config.__handlers__

    if isinstance(process, str):
        task_args = {**{'run': process}, **kwargs}
        task = None
        if process in __eruptr__.keys():
            task = process
            task_args = {**{'run': None}, **kwargs}
        elif process.strip().lower().startswith('select'):
            task = __handlers__['io_sql_read']
        elif process.strip().lower().startswith('insert'):
            task = __handlers__['io_sql_write']
        else:
            task = __handlers__['pipes_command']
        stages.append((task, task_args))
    else:
        module = list(process.keys())[0]
        task = module
        task_args = process[module]
        run_args = None
        if isinstance(task_args, dict):
            if isinstance(task_args.get('run'), list):
                run_args = task_args.pop('run')
                if run_args:
                    for t in run_args:
                        stages.append(
                            (task, {**{'run': t}, **kwargs, **task_args})
                        )
            else:
                stages.append((task, {**kwargs, **task_args}))
        elif isinstance(task_args, str):
            task_args = {**{'run': task_args}, **kwargs}
            stages.append((task, task_args))
        else:      
            stages.append((task, {**kwargs, **task_args}))
    return stages


def build_dag_config(pipeline, **kwargs):    
    dag_config = []
    for process in pipeline:
        for task in build_dag_task(process, **kwargs):
            log.debug(f'DAG config: Added task {task}')
            dag_config.append(task)
    return dag_config


def assemble_pipeline(flow, dag, opts=None, variables=None, config=None):
    pipeline = []
    end_hooks = []
    __eruptr__ = eruptr.modules.__eruptr__
    __context__ = eruptr.modules.__context__
    j2env = jinja2.Environment(
        loader=jinja2.BaseLoader(),
        block_start_string='$%',
        block_end_string='%$',
        variable_start_string='$$',
        variable_end_string='$$'
    )
    for i, task in enumerate(dag):
        __context__.next(flow, task[0], task[1])
        kwargs = {}
        for k, v in task[1].items():
            t = None
            if v:
                t = j2env.from_string(v).render(
                    opts=opts or {},
                    vars=variables or {},
                    cfg=config or {},
                    engines=eruptr.modules.__engines__,
                    tasks=eruptr.modules.__tasks__,
                    context=__context__
                )
            kwargs[k] = t
        log.debug(f'Rendered kwargs: {kwargs}')
        proc = __eruptr__[task[0]](**kwargs)
        __context__.current._kwargs = kwargs
        proc.on_start_hook()
        end_hooks.append(proc.on_end_hook)
        stdin = proc.stdin if i == 0 else pipeline[i-1].stdout
        sub = subprocess.Popen(
            proc.cmd,
            env=proc.env or {'LC_ALL': 'C'},
            stdin=stdin,
            stdout=proc.stdout or subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        pipeline.append(sub)
        if i > 0:
            pipeline[i-1].stdout.close()
    return (pipeline, end_hooks)


def execute_pipeline(pipeline):
    try:
        log.debug(f'Executing pipeline {pipeline}')
        ret = pipeline[-1].communicate()
    except KeyboardInterrupt:
        pipeline[-1].terminate()
        sys.exit(1)
    for r in pipeline[0:-1]:
        if r.returncode is None:
            r.wait()
        if r.returncode != 0:
            raise Exception(r.stderr.read().decode().strip())
    if pipeline[-1].returncode != 0:
        raise Exception(ret[1].decode().strip())
    return pipeline[-1].returncode


class UnixPipeExecutor:
    def __init__(
        self,
        flow,
        pipes,
        opts=None,
        variables=None,
        config=None,
        **kwargs
    ):
        self._flow = flow
        self._pipes = pipes
        self._opts = opts
        self._variables = variables
        self._config = config
        self._kwargs = kwargs

    @eruptr.utils.timer
    def execute(self):
        dag_config = build_dag_config(self._pipes, **self._kwargs)
        log.info(UnixPipeExecutor.print_config(dag_config))
        pipeline, end_hooks = assemble_pipeline(
            self._flow,
            dag_config,
            opts=self._opts,
            variables=self._variables,
            config=self._config
        )
        ret = execute_pipeline(pipeline)
        for fn in end_hooks:
            fn()
        return ret

    @staticmethod
    def print_config(dag_config):
        if not dag_config:
            return 'UnixPipeExecutor: Nothing to do'
        d = []
        for p in dag_config:
            args = ', '.join([f"{k}='{v}'" for k, v in p[1].items()])
            d.append(f'{p[0]}({args}')
        return 'UnixPipeExecutor: ' + ' | '.join(d)
