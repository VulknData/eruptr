import subprocess
import tempfile
import shlex
import os
import shutil
import logging


import eruptr.utils


log = logging.getLogger()


@eruptr.utils.timer
def cmd(run=None, tag=None, env=None):
    if not run:
        log.error('No system command provided')
        return eruptr.utils.default_returner(retcode=1)
    cmd = shlex.split(run)
    ret = subprocess.run(cmd, env=env)
    return eruptr.utils.default_returner(retcode=ret.returncode)


@eruptr.utils.timer
def shell(run=None, tag=None, shell='/bin/sh', env=None):
    if not run:
        log.error('No shell command provided')
        return eruptr.utils.default_returner(retcode=1)
    ret = subprocess.run(run, shell=True, env=env)
    return eruptr.utils.default_returner(retcode=ret.returncode)


@eruptr.utils.timer
def script(run=None, tag=None, shell='/bin/sh', env=None):
    ret = None
    if not run:
        log.error('No script data provided')
        return eruptr.utils.default_returner(retcode=1)
    fd, script_file = tempfile.mkstemp()
    try:
        with open(fd, 'w') as f:
            f.write(run)
        cmd = [shell, script_file]
        ret = subprocess.run(cmd, env=env)
    except Exception as e:
        log.error(e)
    finally:
        os.remove(script_file)
    return eruptr.utils.default_returner(retcode=ret.returncode)
