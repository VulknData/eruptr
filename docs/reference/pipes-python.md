# pipes.python

## pipes.python.run

Creates a temporary script and deploys the block of Python code in the run parameter
to the script for execution. Note you can also provide your own pipes modules in 
Python and execute them using `pipes.python.script`. In most cases this is the 
preferred method however `pipes.python.run` may be useful for small blocks of code.

* Parameters:
    * `run: str` - the code to execute. Note this should use sys.exit and return 
    a valid exit code. All data should be read from stdin and written to stdout.
    * `python: str` - Python binary to use. Must either be the path or the fully 
    qualified path to the binary.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args

* YAML

```yaml
input:
    - io.file.read: /data/incoming/semicolon-delimited-format.dat
    - pipes.python.run:
        python: python3.7
        run: |
            import json
            import sys

            for line in sys.stdin:
                l = line.strip().split(';')
                data = dict(v.replace('"', '').split(':')[0:2] for v in l)
                sys.stdout.write(f'{{ opts.source }}: {json.dumps(data)}\n')

            sys.exit(0)
    - io.file.write: /data/clean-format.json
```

## pipes.python.script

Executes the Python script.

* Parameters:
    * `run: str` - the script to execute. Note this should use sys.exit and 
    return a valid exit code. All data should be read from stdin and written 
    to stdout.
    * `python: str` - Python binary to use. Must either be the path or the fully 
    qualified path to the binary.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args

* YAML

```yaml
input:
    - io.file.read: /data/incoming/semicolon-delimited-format.dat
    - pipes.python.script:
        python: python3.7
        run: /data/scripts/transform.py
    - io.file.write: /data/clean-format.json
```