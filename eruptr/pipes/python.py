# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only

import logging
import tempfile
import os

from eruptr.executors.unixpipe import UnixPipeProcess


log = logging.getLogger()


__virtualname__ = 'pipes.python'


def runcode(run=None, python='python', env=None, **kwargs):
    class PipesPythonRuncode:
        def __init__(self, run, python):
            self._run = run
            self._python = python
            self._script_file = None

        def __call__(self):
            if not self._script_file:
                self.on_start()
            return [self._python, self._script_file]

        def on_start(self):
            fd, script_file = tempfile.mkstemp()
            with open(fd, 'w') as f:
                f.write(self._run)
            self._script_file = script_file

        def on_end(self):
            if self._script_file:
                os.remove(self._script_file)

    return UnixPipeProcess(
        PipesPythonRuncode(run, python),
        env=env,
        on_start=cmd.on_start,
        on_end=cmd.on_end
    )


def runscript(run=None, python='python', env=None, **kwargs):
    return UnixPipeProcess([python, run], env=env)
