# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import argparse
import random
import logging
import textwrap
import json
from types import SimpleNamespace

import eruptr.commands.load
import eruptr.commands.convert
import eruptr.commands.init
import eruptr.commands.admin
import eruptr.commands.project
from eruptr.utils import LogLevels


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
log = logging.getLogger()
log.setLevel('INFO')
logging.addLevelName(LogLevels.SQL, 'SQL')


def _build_docs_subparser(subparsers):
    return subparsers.add_parser(
        'docs',
        help='Generate and/or serve the documentation for your project'
    )


def _build_render_base_subparser(subparsers, parent_parsers):
    p = argparse.ArgumentParser(add_help=False, parents=parent_parsers)
    p.add_argument(
        '--conf',
        dest='conf',
        action='store', 
        metavar='CONFIG_FILE',
        default=None,
        type=str,
        required=True,
        help='Optional. The configuration file for the stream, transformation or let operation'
    )
    p.add_argument(
        '--cluster',
        dest='cluster',
        action='store',
        metavar='CLUSTER',
        type=str,
        help='Optional. Override the cluster setting in the YAML configuration.'
    )
    p.add_argument(
        '--shard',
        dest='shard',
        action='store',
        metavar='SHARD',
        type=str,
        help='Optional. Override the shard setting in the YAML configuration.'
    )
    p.add_argument(
        '--var',
        dest='vars',
        action='append',
        metavar='VARS',
        help='Dynamic options that are passed to the template '
            'engine. Multiple --var options in key=value format '
            'may be provided on the command line.'
    )
    p.add_argument(
        '--timing',
        dest='timing',
        action='store_true',
        default=False,
        help='Enable logging timing information'
    )
    return p


def parse_args():
    tags = [
        "Don't ETL or ELT. LET your data be free.",
        "Data needs a Makefile"
    ]

    parser = argparse.ArgumentParser(
        prog='eruptr',
        description=tags[random.randint(0, len(tags)-1)],
        allow_abbrev=False
    )
    parser.add_argument(
        '--log-level',
        dest='log_level',
        action='store',
        metavar='LOG_LEVEL',
        default='WARNING',
        type=str,
        help='Optional. The log level (try INFO, WARNING, DEBUG etc..). (default WARNING)'
    )
    subparsers = parser.add_subparsers(title="Available sub-commands")
    base = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    base.add_argument(
        '--log-level',
        dest='log_level',
        action='store',
        metavar='LOG_LEVEL',
        default='WARNING',
        type=str,
        help='Optional. The log level (try INFO, WARNING, DEBUG etc..). (default WARNING)'
    )
    render_base = _build_render_base_subparser(subparsers, [base])

    #eruptr.commands.init.cli_args(subparsers, [base])
    #eruptr.commands.admin.cli_args(subparsers, [render_base])
    eruptr.commands.load.cli_args(subparsers, [render_base])
    eruptr.commands.convert.cli_args(subparsers, [base])
    #eruptr.commands.project.cli_args(subparsers, [base])

    return parser.parse_args()