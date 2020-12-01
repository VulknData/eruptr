# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import os
import yaml
import json
import logging
import pprint
import argparse
from types import SimpleNamespace
from jinja2 import Environment, FileSystemLoader, select_autoescape
from mako.template import Template


import eruptr.modules
from eruptr.exceptions import EruptrConfigException


log = logging.getLogger()


VERSION_MAJOR = 20
VERSION_MINOR = 12
VERSION_PATCH = 1
VERSION_TEST = None
VERSION = '.'.join([str(VERSION_MAJOR), str(VERSION_MINOR), str(VERSION_PATCH)])

if VERSION_TEST:
    VERSION += '.' + VERSION_TEST

__handlers__ = {
    'locks': 'locks.filesystem',
    'io_sql_read': 'io.clickhouse.local',
    'io_sql_write': 'io.clickhouse.write',
    'streams_sql_transform': 'pipes.clickhouse.local',
    'streams_command': 'pipes.cmd.shell',
    'task_sql_execute': 'tasks.clickhouse.execute',
    'task_sql_select': 'tasks.clickhouse.select',
    'task_command': 'tasks.cmd.shell',
    'evaluator': 'tasks.clickhouse.local'
}

timing = False

__vars__ = SimpleNamespace()
__opts__ = None

workflow = [
    {'drop': {'executor': 'StepExecutor', 'enabled': False, 'max_tasks': 1}},
    {'create': {'executor': 'StepExecutor', 'enabled': False, 'max_tasks': 1}},
    {'distributed': {'executor': 'StepExecutor', 'enabled': False, 'max_tasks': 1}},
    {'reset': {'executor': 'StepExecutor', 'enabled': False, 'max_tasks': 1}},
    {'pre': {'executor': 'StepExecutor', 'enabled': True, 'max_tasks': 1}},
    {'input': {'executor': 'UnixPipeExecutor', 'enabled': True, 'max_tasks': 1}},
    {'transform': {'executor': 'StepExecutor', 'enabled': True, 'max_tasks': 1}}
]

def render_templates(config_file, opts, variables, cfg={}):
    global __handlers__
    __eruptr__ = eruptr.modules.__eruptr__
    jinja_cfg_template_file = os.path.basename(config_file)
    jinja_env = Environment(
        loader=FileSystemLoader(os.path.dirname(config_file)),
        autoescape=select_autoescape(['yaml']) 
    )
    jinja_template = jinja_env.get_template(jinja_cfg_template_file)
    jinja_rendered_template = jinja_template.render(
        opts=opts,
        vars=variables,
        cfg=cfg,
        engines=eruptr.modules.__engines__,
        tasks=eruptr.modules.__tasks__
    )
    mako_template = Template(jinja_rendered_template)
    mako_rendered_template = mako_template.render(
        opts=opts,
        vars=variables,
        cfg=cfg,
        engines=eruptr.modules.__engines__,
        tasks=eruptr.modules.__tasks__
    )
    ret = yaml.safe_load(mako_rendered_template)
    if ret is None:
        raise EruptrConfigException(
            'Could not render configuration. Is the file empty?'
        )
    if ret.get('defaults'):
        if ret['defaults'].get('handlers'):
            __handlers__.update(ret['defaults']['handlers'])
            ret['defaults']['handlers'] = __handlers__
    else:
        ret['defaults'] = {'handlers': __handlers__}
    if not ret['defaults'].get('params'):
        ret['defaults']['params'] = {}
    if opts.cluster:
        ret['cluster'] = opts.cluster
    if opts.shard:
        ret['shard'] = opts.shard
    if isinstance(ret.get('cluster'), str):
        if ret['cluster'].strip().lower().startswith('select'):
            ret['cluster'] = __eruptr__[__handlers__['evaluator']](ret['cluster'])
    if isinstance(ret.get('shard'), str):
        if ret['shard'].strip().lower().startswith('select'):
            ret['shard'] = __eruptr__[__handlers__['evaluator']](ret['shard'])
    if ret.get('vars'):
        ret['vars'].update(variables)
    else:
        ret['vars'] = variables
    if not ret.get('workflow'):
        ret['workflow'] = workflow
    if ret.get('vars'):
        for k, task_args in ret['vars'].items():
            if isinstance(task_args, str):
                if task_args.strip().lower().startswith('select'):
                    ret['vars'][k] = __eruptr__[__handlers__['evaluator']](
                        task_args
                    )
                continue
            task_args = task_args
            [task_args.pop(key) for key in ['module']]
            ret['vars'][k] = __eruptr__[__handlers__['evaluator']](**task_args)
    return ret


def render_config(opts, variables, library):
    cfg = render_templates(opts.conf, opts, variables.__dict__)
    ret =  render_templates(opts.conf, opts, cfg['vars'], cfg)
    if 'name' not in ret:
        ret['name'] = os.path.basename(opts.conf)
    yaml_cfg = yaml.safe_dump(
        ret,
        indent=4,
        default_flow_style=False,
        sort_keys=False
    ).strip()
    log.debug(f'Rendered config:\n{yaml_cfg}')
    return ret