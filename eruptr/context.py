# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only

import logging


log = logging.getLogger()


class TaskInfo:
    def __init__(self, flow, func, kwargs):
        self._flow = flow
        self._func = func
        self._kwargs = kwargs

    def __getitem__(self, key):
        if key in self._kwargs:
            return self._kwargs[key]
        else:
            raise AttributeError

    def __setitem__(self, key, value):
        self._kwargs[key] = value

    def __str__(self):
        return f"TaskInfo('{self._flow}', '{self._func}', {self._kwargs})"


class ContextManager:
    def __init__(self):
        self.current = None
        self.previous = None
        self.tasks = []
        self.tags = {}

    def next(self, flow, func, kwargs):
        if self.current:
            tag = None
            try:
                tag = self.current['tag']
            except:
                tag = f'{len(self.tasks)}-{self.current._func}'
                self.current['tag'] = tag
            self.previous = self.current
            self.tasks.append(self.current)
            if tag in self.tags:
                log.warning(f'Overwriting existing tag - {tag}')
            self.tags[tag] = self.current
        self.current = TaskInfo(flow, func, kwargs)
