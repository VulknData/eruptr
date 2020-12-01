# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import os
import sys
import logging
import subprocess
import json
import yaml
import pprint
import re
import shutil


from tabulate import tabulate


import eruptr.modules
from eruptr.engines.clickhouse import ClickHouseModel
from eruptr.utils import LogLevels
from eruptr.commands import EruptrCommand
from eruptr.objects import SQLObject


log = logging.getLogger()


def print_table(data, headers=None):
    print(tabulate(data, headers=headers or "keys"))


def cli_args(subparsers, parent_parsers):
    p = subparsers.add_parser(
        'project',
        parents=parent_parsers,
        allow_abbrev=False,
        help='Eruptr project operations'
    )
    g = p.add_argument_group('Management options')
    g.add_argument(
        '--conf',
        dest='conf',
        action='store',
        type=str,
        metavar='CONFIG_FILE',
        help="The path to the Eruptr project file."
    )
    g.add_argument(
        '--list-objects',
        dest='list_objects',
        action='store_true',
        help="List the objects found within the primary datasource."
    )
    g.add_argument(
        '--refresh-objects',
        dest='refresh_objects',
        action='store_true',
        help="Refresh the existing objects within the project path."
    )
    g.add_argument(
        '--show-object',
        dest='show_object',
        action='store',
        default=None,
        metavar='DATABASE.NAME',
        help="Examine and display the project object."
    )
    g.add_argument(
        '--diff',
        dest='diff',
        action='store',
        default=None,
        metavar='DATABASE.NAME',
        help="Display the diff between the project object and the database object"
    )
    g.add_argument(
        '--show-migration',
        dest='show_migration',
        action='store',
        default=None,
        metavar='DATABASE.NAME',
        help="Display the migration SQL between the project object and the database object"
    )
    g.set_defaults(cls=EruptrProject)


class EruptrProject(EruptrCommand):
    @eruptr.utils.timer
    def show_object(self):
        model_path = f"{self._project_path}/objects/{self._show_object.replace('.', '/')}.sql"
        sql = str(SQLObject(model_path))
        print(f'SQL Definition\n--------------\n\n{sql}\n')
        obj = ClickHouseModel(sql)
        print(f'Object Representation\n---------------------\n\n{obj}\n')

    @eruptr.utils.timer
    def diff(self):
        model_path = f"{self._project_path}/objects/{self._diff.replace('.', '/')}.sql"
        file_model = ClickHouseModel(str(SQLObject(model_path)))
        db_model = ClickHouseModel(self._get_object(self._diff))
        pprint.pprint(db_model.diff(file_model))

    @eruptr.utils.timer
    def show_migration(self):
        model_path = f"{self._project_path}/objects/{self._show_migration.replace('.', '/')}.sql"
        file_model = ClickHouseModel(str(SQLObject(model_path)))
        db_model = ClickHouseModel(self._get_object(self._show_migration))
        pprint.pprint(db_model.migrate(file_model))

    def _get_object(self, obj):
        __eruptr__ = eruptr.modules.__eruptr__
        r = __eruptr__['tasks.clickhouse.select'](
            f'SHOW CREATE {obj}',
            connection=self._project['cluster']
        )
        return json.loads(r.data)['data'][0]['statement']

    @eruptr.utils.timer
    def refresh_objects(self):
        __eruptr__ = eruptr.modules.__eruptr__
        sql = """
            SELECT
                database,
                name
            FROM system.tables
            WHERE database NOT IN ('system', 'vulkn')
            ORDER BY 
                database, engine, name
        """
        ret = __eruptr__['tasks.clickhouse.select'](
            sql,
            connection=self._project['cluster']
        )
        shutil.rmtree(f'{self._project_path}/objects')
        os.mkdir(f'{self._project_path}/objects')
        for i in json.loads(ret.data)['data']:
            database = i['database']
            name = i['name']
            print(f'Getting definition for "{database}"."{name}"')
            obj = self._get_object(f'"{database}"."{name}"')
            if not os.path.isdir(f'{self._project_path}/objects/{database}'):
                os.makedirs(f'{self._project_path}/objects/{database}')
            with open(
                f'{self._project_path}/objects/{database}/{name}.sql',
                'w'
            ) as fd:
                fd.write(obj)

    @eruptr.utils.timer
    def list_objects(self, enabled=False):
        __eruptr__ = eruptr.modules.__eruptr__
        sql = """
            SELECT
                format('`{0}`.`{1}`', database, name) AS Object,
                engine AS Engine
            FROM system.tables
            WHERE database != 'system'
            ORDER BY 
                database, engine, name
        """
        ret = __eruptr__['tasks.clickhouse.select'](
            sql,
            connection=self._project['cluster']
        )
        return json.loads(ret.data)['data']

    @eruptr.utils.timer
    def run(self):
        with open(self._conf, 'r') as fd:
            self._project = yaml.safe_load(fd.read())
        self._project_path = os.path.dirname(self._conf)
        if self._list_objects:
            print_table(self.list_objects())
        if self._refresh_objects:
            self.refresh_objects()
        if self._show_object:
            self.show_object()
        if self._diff:
            self.diff()
        if self._show_migration:
            self.show_migration()
        return 0
