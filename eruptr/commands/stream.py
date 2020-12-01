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


log = logging.getLogger()


def cli_args(subparsers, parent_parsers):
    return subparsers.add_parser(
        'stream', 
        help='Start a stream processing microservice for your transformation'
    )