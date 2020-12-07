# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import logging
import yaml
import itertools
import functools

import eruptr.utils
import eruptr.config
from eruptr.utils import LogLevels
from eruptr.commands import EruptrCommand
from eruptr.executors.step import StepExecutor
from eruptr.executors.unixpipe import UnixPipeExecutor
from eruptr.config import render_config


log = logging.getLogger()


def cli_args(subparsers, parent_parsers):
    p = subparsers.add_parser(
        'load',
        parents=parent_parsers,
        help='Execute a batch data processing/load task'
    )
    g = p.add_argument_group('Load mode options')
    g.add_argument(
        '--input',
        dest='input',
        action='store',
        type=str, 
        help="Specify the input type (default - file)"
    )
    g.add_argument(
        '--source',
        dest='source',
        action='store',
        type=str, 
        help="The source object, path or query (default - empty string)")
    g.add_argument(
        '--name',
        dest='name',
        action='store',
        type=str, 
        help="Optional. A name to provide for the data source (default - SOURCE)"
    )
    g.add_argument(
        '--enable',
        dest='enable',
        action='store',
        type=str, 
        help="Comma delimited list of flows to enable"
    )
    g.add_argument(
        '--disable',
        dest='disable',
        action='store',
        type=str, 
        help="Comma delimited list of flows to disable"
    )
    g.add_argument(
        '--flows',
        dest='flows',
        action='store',
        type=str, 
        help="Comma delimited list of flows to execute - ignores enable/disable flags"
    )
    g.add_argument(
        '--retry',
        dest='retry',
        action='store',
        type=str,
        help="Comma delimited list of flows to retry or run on failure"
    )
    g.add_argument(
        '--test',
        dest='test',
        action='store_true',
        default=False,
        help="""Test mode - render the configuration and setup executors skipping 
            the actual execution. Note that although no execution takes place
            there may be side-effects during rendering."""
    )
    g.add_argument(
        '--render',
        dest='render',
        action='store_true',
        default=False,
        help="""Like test mode but outputs the rendered configuration only.
            Executors are not setup."""
    )
    g.add_argument(
        '--docs',
        dest='docs',
        action='store_true',
        default=False,
        help="""Print the load task documentation to the console and exit."""
    )
    g.set_defaults(cls=EruptrLoad)


class EruptrLoad(EruptrCommand):
    def _execute_step_stage(self, stage, **kwargs):
        log.info(f'Executing {stage} section')
        s = StepExecutor(stage, self._cfg.get(stage, []), **kwargs)
        if not self._opts.test:
            s.execute()

    def _execute_stream_stage(self, stage, **kwargs):
        log.info(f'Executing {stage} section')
        stages = self._cfg.get(stage, [])
        if self._input:
            task = {self._input: {'run': self._source}}
            stages = [task] + stages[1:]
        s = UnixPipeExecutor(stage, stages, **kwargs)
        if not self._opts.test:
            s.execute()

    def _unlock(self):
        for l in self._locks:
            if not self._opts.test:
                l.unlock()

    def _lock(self):
        __eruptr__ = eruptr.modules.__eruptr__
        if len(self._cfg.get('locks', [])) > 0 and not self._opts.test:
            for lockmod in self._cfg.get('locks'):
                klass = __eruptr__[lockmod['module']]
                l = klass(lockmod['locks'])
                l.lock()
                self._locks.append(l)

    @functools.lru_cache(maxsize=None)
    def _plan_flows(self):
        cli_retry = self._retry.split(',') if self._retry else []
        cli_enabled = self._enable.split(',') if self._enable else []
        cli_disabled = self._disable.split(',') if self._disable else []
        cli_flows = self._flows.split(',') if self._flows else []

        workflows = [list(f.keys())[0] for f in self._cfg['workflow']]

        for flow in itertools.chain(
            cli_retry,
            cli_enabled,
            cli_disabled,
            cli_flows
        ):
            if flow not in workflows:
                raise Exception(f'Unknown flow {flow} specified.')

        flows = []
        retry_flows = []

        for flow in self._cfg['workflow']:
            flow_name = list(flow.keys())[0]
            if len(cli_flows) > 0:
                if flow_name in cli_flows:
                    flows.append({'flow': flow_name, **flow[flow_name]})
                continue
            if (
                flow_name in cli_retry or 
                '*' in cli_retry or
                flow[flow_name].get('retry', False)
            ):
                retry_flows.append({'flow': flow_name, **flow[flow_name]})
            if (
                (flow_name in cli_disabled or '*' in cli_disabled) 
                and flow_name not in cli_enabled
            ):
                continue
            if (
                flow[flow_name].get('enabled', False) 
                or flow_name in cli_enabled 
                or '*' in cli_enabled
            ):
                flows.append({'flow': flow_name, **flow[flow_name]})

        return (flows, retry_flows)

    @eruptr.utils.timer
    def run(self):
        def _run(retry=False, **kwargs):
            flows, retry_flows = self._plan_flows()

            log.debug(f'Enabled flows: {flows}')
            log.debug(f'Default parameters: {kwargs}')
            log.info(f'Running "{self._cfg["name"]}"')

            if retry:
                log.debug(f'Retry flows: {retry_flows}')
                for flow in retry_flows:
                    if flow['executor'] == 'StepExecutor':
                        self._execute_step_stage(flow['flow'], **kwargs)
                    elif flow['executor'] == 'UnixPipeExecutor':
                        self._execute_stream_stage(flow['flow'], **kwargs)

            for flow in flows:
                if flow['executor'] == 'StepExecutor':
                    self._execute_step_stage(flow['flow'], **kwargs)
                elif flow['executor'] == 'UnixPipeExecutor':
                    self._execute_stream_stage(flow['flow'], **kwargs)

            log.info(f'Successfully completed "{self._cfg["name"]}"')
            print(f'\nOK - {self._cfg["name"]} - SUCCESS\n')
            return 0

        log.info('Rendering configuration')
        self._cfg = eruptr.config.render_config(
            self._opts,
            self._vars,
            self._library
        )
        if self._opts.render:
            print(
                yaml.safe_dump(
                    self._cfg,
                    indent=4,
                    default_flow_style=False,
                    sort_keys=False
                ).strip()
            )
            return 0
        if self._opts.docs:
            if 'help' in self._cfg:
                print(f"\n{self._cfg['help']}")
            return 0
        kwargs = {
            **self._cfg.get('params', {}),
            **{'connection': self._cfg.get('shard', None)}
        }
        flows, retry_flows = self._plan_flows()
        self._locks = []
        r = 1
        try:
            self._lock()
            r = _run(**kwargs)
        except:
            if self._retry or len(retry_flows) > 0:
                log.error('BatchCommand failed - retrying...')
                try:
                    r = _run(retry=True, **kwargs)
                except:
                    log.error('BatchCommand retry failed')
                    raise
            else:
                log.error('BatchCommand failed')
                raise
        finally:
            self._unlock()
        return r
