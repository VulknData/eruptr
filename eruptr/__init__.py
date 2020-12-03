# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import sys
import json
import os
import logging
from types import SimpleNamespace


from eruptr.utils import LogLevels
import eruptr.modules
import eruptr.config
import eruptr.args


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)
log = logging.getLogger()
log.setLevel('INFO')
logging.addLevelName(LogLevels.SQL, 'SQL')


def main():
    sys.stderr.write('VulknData Eruptr (C) 2020 VulknData\n\n')
    sys.stderr.write('GPLv3 - see https://github.com/VulknData/eruptr/COPYING\n\n')
    eruptr.config.__opts__ = eruptr.args.parse_args()
    __opts__ = eruptr.config.__opts__
    log.setLevel(__opts__.log_level)
    log.debug(f'Options: {__opts__}')
    if hasattr(__opts__, 'timing'):
        eruptr.config.timing = __opts__.timing

    __eruptr__ = eruptr.modules.__eruptr__
    eruptr.modules.load_modules()

    if hasattr(__opts__, 'cls'):
        eruptr.config.__vars__ = SimpleNamespace()
        if hasattr(__opts__, 'vars') and __opts__.vars:
            l = [k.split('=',1) for k in __opts__.vars]
            eruptr.config.__vars__ = SimpleNamespace(
                **dict((f'{k[0]}', json.loads(k[1])) for k in l)
            )
            log.debug(f'User variables: {eruptr.config.__vars__.__dict__}')
        eruptr_cmd = __opts__.cls(__opts__, eruptr.config.__vars__, __eruptr__)
        sys.exit(eruptr_cmd.run())
    
    log.error('No valid command found or specified')
    sys.exit(1)
