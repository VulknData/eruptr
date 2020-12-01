# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import os
import fcntl
import logging
import time
import copy


import eruptr.utils


log = logging.getLogger()


class Lock:
    def __init__(self, locks=None, lockdir='/tmp', prefix=None, timeout=1800):
        self._locks = locks
        self._lockdir = lockdir
        self._prefix = prefix
        self._timeout = 1800
        self._held_locks = {}

    @eruptr.utils.timer
    def lock(self):
        if not os.path.exists(self._lockdir):
            os.mkdir(self._lockdir)
        for l in self._locks:
            ltype, lname = list(list(l.items())[0])
            fd_lock_mode = (
                os.O_CREAT|os.O_WRONLY|os.O_EXCL if ltype == 'exclusive' 
                else os.O_CREAT|os.O_WRONLY
            )
            fc_lock_mode = (
                fcntl.LOCK_EX if ltype == 'exclusive' else fcntl.LOCK_SH
            )
            lock_path = f'{self._lockdir}/{lname}.eruptr.lock'
            for i in range(0, self._timeout):
                log.debug(
                    f'locks.filesystem: Trying for {ltype} lock {lock_path} (attempt {i+1})'
                )
                if i > 0:
                    log.warning(
                        f'locks.filesystem: Trying for {ltype} lock {lock_path} (attempt {i+1})'
                    )
                try:
                    lock = os.open(lock_path, fd_lock_mode)
                    fcntl.flock(lock, fc_lock_mode)
                    self._held_locks[lock_path] = (lock, ltype)
                    log.info(
                        f'locks.filesystem: Got lock {lock_path} with fd {lock}'
                    )
                    break
                except:
                    log.warn(
                        f'locks.filesystem: Failed for {lock_path} - retrying'
                    )
                    pass
                time.sleep(1)
            else:
                return False
        return True

    @eruptr.utils.timer
    def unlock(self):
        held_locks = copy.deepcopy(self._held_locks)
        for lock_path, lock in held_locks.items():
            remove_lock = True if lock[1] == 'exclusive' else False
            if lock[1] == 'shared':
                try:
                    log.debug(
                        f'locks.filesystem: Attempting to upgrade LOCK_SH to LOCK_EX for {lock[0]}'
                    )
                    fcntl.flock(lock_path, fcntl.LOCK_EX|fcntl.LOCK_NB)
                    remove_lock = True
                    log.debug(
                        f'locks.filesystem: Upgrade succeeded for {lock[0]}'
                    )
                except:
                    log.warning(
                        f'locks.filesystem: Upgrade failed for {lock[0]}'
                    )
            if remove_lock:
                log.debug(
                    f'locks.filesystem: Attempting to remove LOCK_EX for {lock[0]}'
                )
                os.remove(lock_path)
            log.info(
                f'locks.filesystem: Removed lock {lock_path} with fd {lock[0]}'
            )
            os.close(lock[0])
            del self._held_locks[lock_path]
        return True
