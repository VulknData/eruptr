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


class SQLObject:
    def __init__(self, path):
        self._path = path

    def __str__(self):
        jinja_template_file = os.path.basename(self._path)
        jinja_env = Environment(
            loader=FileSystemLoader(os.path.dirname(self._path))
        )
        jinja_template = jinja_env.get_template(jinja_template_file)
        jinja_rendered_template = jinja_template.render()
        mako_template = Template(jinja_rendered_template)
        mako_rendered_template = mako_template.render()
        return mako_rendered_template
