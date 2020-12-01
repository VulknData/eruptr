# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import logging


from eruptr.commands import EruptrCommand
from eruptr.executors.step import StepExecutor
from eruptr.config import render_config


log = logging.getLogger()


def cli_args(subparsers, parent_parsers):
    p = subparsers.add_parser(
        'admin', 
        parents=parent_parsers,
        help='Manage objects within your database'
    )
    g = p.add_argument_group('Administrative options')
    g.add_argument(
        '--create',
        dest='create',
        action='store_true', 
        help="Execute the 'create' section in the YAML configuration (default - no create)"
    )
    g.add_argument(
        '--drop',
        dest='drop',
        action='store_true', 
        help="Execute the 'drop' section in the YAML configuration (default - no drop)"
    )
    g.add_argument(
        '--reset',
        dest='reset',
        action='store_true', 
        help="Execute the 'reset' section in the YAML configuration (default - no reset)"
    )
    g.add_argument(
        '--distributed',
        dest='distributed',
        action='store_true', 
        help="Execute the 'distributed' section in the YAML configuration (default - no distributed statements)"
    )
    g.set_defaults(cls=EruptrAdmin)


class EruptrAdmin(EruptrCommand):
    def _execute_admin_stages(self, **kwargs):
        for stage in ['drop', 'create', 'reset', 'distributed']:
            if self.__dict__.get(f'_{stage}', False):
                self._execute_step_stage(stage, **kwargs)

    def _execute_step_stage(self, stage, **kwargs):
        log.info(f'Executing {stage} section')
        s = StepExecutor(self._cfg.get(stage, []), **kwargs)
        s.execute()

    def run(self):
        log.info('Rendering configuration')
        self._cfg = render_config(self._opts, self._vars, self._library)
        kwargs = {
            **self._cfg.get('params', {}),
            **{'connection': self._cfg['shard']}
        }
        log.debug(f'Default parameters: {kwargs}')
        log.info(f'Running admin for "{self._cfg["name"]}"')
        self._execute_admin_stages(**kwargs)
        log.info(f'Successfully completed "{self._cfg["name"]}"')
        return 0
