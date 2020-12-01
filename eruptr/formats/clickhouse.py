# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import sys
import functools
import logging


import eruptr.utils.path
import eruptr.engines.clickhouse


log = logging.getLogger()


__virtualname__ = 'formats.clickhouse'


def _get_formats():
    sql = f"SELECT name, is_input, is_output FROM system.formats"
    r = eruptr.engines.clickhouse.local(sql, output_format='JSON')
    if r.retcode != 0:
        raise Exception('Unable to discover {format_type} formats')
    return r.data


def _build_format_class(format_class):
    clickhouse_formatter = type(
        format_class['name'],
        (object, ), 
        {
            '__procname__': f"{__virtualname__}.{format_class['name']}",
            'format': format_class['name'],
            'is_input': format_class['is_input'] == 1,
            'is_output': format_class['is_output'] == 1
        })
    return clickhouse_formatter


for format_class in _get_formats():
    globals()[format_class['name']] = _build_format_class(format_class)