# locks.filesystem

## locks.filesystem

Use simple file based locking. This is very effective, even up to thousands of 
files per minute however it only satisfies local execution where all tasks in 
a given lock space are running on a single machine.

* Parameters:
    * `locks: list(dict)` - list of key/value pairs being the lock-type:lock-name.
    * `lockdir: str='/tmp'` - directory where locks are created.
    * `prefix: str=None` - prefix to prepend to the lock-name.
    * `timeout: int=1800` - timeout in seconds to fail the lock.
    * `retry: int=1` - retry every retry seconds (default - 1 second)
* YAML:

```yaml
locks:
    locks.filesystem:
        lockdir: /tmp/locks
        prefix: eruptr-locks-
        timeout: 60
        locks:
            - shared: mybatchrun
            - exclusive: mybatchrun.{{ opts.source }}
```