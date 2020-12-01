import os
import shutil
import logging


import eruptr.utils


log = logging.getLogger()


@eruptr.utils.timer
def copy(run=None, tag=None, src=None, dst=None, **kwargs):
    if not src:
        log.error('No source file provided')
        return eruptr.utils.default_returner(retcode=1)
    if not dst:
        log.error('No destination file provided')
        return eruptr.utils.default_returner(retcode=1)
    shutil.copy(src, dst)
    return eruptr.utils.default_returner(retcode=0)


@eruptr.utils.timer
def move(run=None, tag=None, src=None, dst=None, **kwargs):
    cp = copy(src=src, dst=dst)
    if cp.retcode != 0:
        return cp
    rm = delete(run=src)
    return rm


@eruptr.utils.timer
def delete(run=None, tag=None, **kwargs):
    filename = run
    if not filename:
        log.error('No filename provided')
        return eruptr.utils.default_returner(retcode=1)
    if os.path.exists(filename) and os.path.isfile(filename):
        os.remove(filename)
    return eruptr.utils.default_returner(retcode=0)


@eruptr.utils.timer
def write(run=None, tag=None, path=None, data=None, **kwargs):
    if not path:
        log.error('No filename provided')
        return eruptr.utils.default_returner(retcode=1)
    if not data:
        log.error('No file content provided')
        return eruptr.utils.default_returner(retcode=1)
    with open(path, 'w+') as fd:
        fd.write(data)
    return eruptr.utils.default_returner(retcode=0)
