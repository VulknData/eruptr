# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import types


class Context:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._current = types.SimpleNamespace

    @property
    def current(self):
        return self._current