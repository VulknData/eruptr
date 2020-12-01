# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import os
import yaml
import logging
import collections


import eruptr.config
from eruptr.commands import EruptrCommand


log = logging.getLogger()


def cli_args(subparsers, parent_parsers):
    p = subparsers.add_parser(
        'init', 
        parents=parent_parsers,
        help='Initialise a project directory, optionally from an existing database'
    )
    g = p.add_argument_group('Initialization options')
    g.add_argument(
        '--path',
        action='store',
        dest='project_path',
        type=str, 
        required=True,
        help="Path to store project files"
    )
    g.add_argument(
        '--name',
        action='store',
        dest='project_name',
        type=str,
        required=True,
        help="Name for the project")
    g.set_defaults(cls=EruptrInit)


class EruptrInit(EruptrCommand):
    def _init_dir(self):
        paths = [
            'extensions/commands',
            'extensions/executors',
            'extensions/engines',
            'extensions/formats',
            'extensions/io',
            'extensions/locks',
            'extensions/tasks',
            'extensions/streams',
            'eruptr/db',
            'eruptr/packages',
            'eruptr/data',
            'macros',
            'data',
            'objects',
            'models',
            'conversions',
            'tests',
            'eruptr',
            'build',
            'hooks',
            'sql',
            'docs']
        if os.path.exists(self._project_path):
            log.error(f'Path {self._project_path} already exists. Aborting.')
            raise Exception(
                    f'Path {self._project_path} already exists. Aborting.')
        else:
            log.debug(
                f'Creating project ({self._project_name}) path in {self._project_path}.'
            )
            os.mkdir(self._project_path)
            for p in paths:
                os.makedirs(f'{self._project_path}/{p}', exist_ok=True)

    def _init_config(self):
        cfg = {
            'project': self._project_name,
            'handlers': eruptr.config.__handlers__,
            'cluster': 'http://localhost'
        }
        with open(f'{self._project_path}/eruptr.yaml', 'w') as project_file:
            log.debug(
                f'Creating project configuration at {self._project_path}/eruptr.yaml.'
            )
            log.debug(cfg)
            yaml.safe_dump(cfg,
                           project_file,
                           indent=4,
                           default_flow_style=False,
                           sort_keys=False)

    def run(self):
        log.debug(self)
        self._init_dir()
        self._init_config()
        print(
            f'Initialised project {self._project_name} at path {self._project_path}.\n'
        )
        return 0
        