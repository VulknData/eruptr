# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import logging


log = logging.getLogger()


class EruptrCommand:
    def __init__(self, opts, variables, library):
        self._opts = opts
        self._vars = variables
        self._library = library
        for k, v in self._opts.__dict__.items():
            if k not in ('cls', 'vars'):
                setattr(self, f'_{k}', v)

    def __repr__(self):
        _opts = self._opts.__dict__ if self._opts else {}
        _vars = self._vars.__dict__ if self._vars else {}
        _library = self._library if self._library else {}
        return f'{self.__class__.__name__}(opts={_opts}, variables={_vars}, library={_library})'
