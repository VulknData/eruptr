# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import os
import sys
import logging
import subprocess


import eruptr.utils
import eruptr.config
import eruptr.modules
from eruptr.utils import LogLevels
from eruptr.commands import EruptrCommand
from eruptr.executors.unixpipe import UnixPipeExecutor


log = logging.getLogger()


def cli_args(subparsers, parent_parsers):
    p = subparsers.add_parser(
        'convert',
        parents=parent_parsers,
        allow_abbrev=False,
        help='Convert from one data source/format to another'
    )
    g = p.add_argument_group('Conversion mode options')
    g.add_argument(
        '--input',
        dest='input',
        action='store',
        type=str,
        default='io.file.stdin',
        help="Specify the input type (default - io.file.stdin)"
    )
    g.add_argument(
        '--output',
        dest='output',
        action='store',
        type=str,
        default='io.file.stdout',
        help="Specify the output type (default - io.file.stdout)"
    )
    g.add_argument(
        '--input-schema',
        action='store',
        dest='input_schema',
        type=str,
        default='data String',
        required=True,
        help="Comma delimited input schema"
    )                
    g.add_argument(
        '--input-format',
        action='store',
        dest='input_format',
        type=str,
        default='data String',
        required=True,
        help="Input format (see --list-formats for available input formats)"
    )
    g.add_argument(
        '--output-format',
        action='store',
        dest='output_format',
        type=str,
        default='data String',
        required=True,
        help="Optional. Output format (see --list-formats for available output formats). (default --input-format)"
    )     
    g.add_argument(
        '--transform',
        action='store',
        dest='transform',
        default='SELECT * FROM table', 
        metavar='TRANSFORM',
        required=False,
        help="Optional. SQL queries to transform data between formats"
    )
    g.add_argument(
        '--timing',
        dest='timing',
        action='store_true',
        default=False,
        help='Enable logging timing information'
    )
    g.set_defaults(cls=EruptrConvert)


def _create_stream_from_cmdline(cli_arg):
    stream_chain = []
    __eruptr__ = eruptr.modules.__eruptr__
    for stream_cli in cli_arg.split(','):
        args = stream_cli.split(':')
        func = args[0]
        func_args = {'run': None}
        if len(args[1:]) > 0:
            func_args = dict(a.split('=', 1) for a in args[1:])
        stream_chain.append(__eruptr__[func](**func_args))
    return stream_chain


class EruptrConvert(EruptrCommand):
    @eruptr.utils.timer
    def run(self):
        __eruptr__ = eruptr.modules.__eruptr__
        if not __eruptr__[self._input_format].is_input:
            raise Exception(
                f'Input format not supported - {self._input_format}'
            )
        if not __eruptr__[self._output_format].is_output:
            raise Exception(
                f'Output format not supported - {self._output_format}'
            )
        input_format = __eruptr__[self._input_format].format
        output_format = __eruptr__[self._output_format].format
        convert_stream = _create_stream_from_cmdline(self._input)
        convert_stream.append(
            __eruptr__['pipes.clickhouse.local'](
                run=self._transform,
                structure=self._input_schema,
                input_format=input_format,
                output_format=output_format
            )
        )
        convert_stream += _create_stream_from_cmdline(self._output)
        e = UnixPipeExecutor(convert_stream)
        e.execute()
        return 0