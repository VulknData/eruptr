# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import os
import subprocess
import logging
import functools


log = logging.getLogger()


@functools.lru_cache(maxsize=None)
def which(binary):
    path = subprocess.check_output(['which', binary]).strip().decode()
    if os.path.isfile(path) and os.access(path, os.X_OK):
        log.debug(f"Discovered {binary} at '{path}'")
        return True
    return None
