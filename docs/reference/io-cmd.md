# io.cmd

## io.cmd.cmd
## io.cmd.readcmd
## io.cmd.writecmd

Use a command as the initiating IO

Pass the data through a single Linux/Unix command. Note that in most cases
using SQL via the pipes.clickhouse.local command, even on unstructured text,
is better for processing text/data if possible.

* Parameters:
    * `run: str=None` - the command to pipe the data through
    * `mode: str='read'` - the mode for the command (read/write)
    * `tag: str=None` - optional user-defined tag for the resource
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.cmd.cmd:
        run: grep -v 'DEVICE=3'
        mode: read
    ...
```

```yaml
input:
    - io.cmd.readcmd: grep -v 'DEVICE=3'
    ...
```

## io.cmd.shell
## io.cmd.readshell
## io.cmd.writeshell

As per pipes.shell.cmd however starts a shell and executes the given pipeline 
within the shell.

* Parameters:
    * `run: str=None` - the pipeline to pipe the data through.
    * `mode: str='read'` - the mode for the command (read/write)
    * `tag: str=None` - optional user-defined tag for the resource.
    * `shell: str='/bin/sh'` - the shell to execute the pipeline in.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args

```yaml
input:
    - io.cmd.readshell:
        run: cat inputfile.dat | grep -v 'DEVICE=3' | cut -d, -f3
        shell: /bin/bash
        env:
            PATH: /opt/mybins:$PATH
    ...
```

## io.cmd.script
## io.cmd.readscript
## io.cmd.writescript

Execute the given script. The script should read the data from stdin and echo
back to stdout. Only data from stdout will be fed back through the pipeline.

* Parameters:
    * `run: str=None` - the shell script content to pipe the data through.
    * `mode: str='read'` - the mode for the command (read/write)
    * `tag: str=None` - optional user-defined tag for the resource
    * `shell: str='/bin/sh'` - the shell to execute the pipeline in.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args

```yaml
input:
    - io.cmd.readscript:
        run: |
            #!/bin/bash

            wget {{ vars.input_url }} -

            exit $?
        shell: /bin/bash
        env:
            PATH: /opt/mybins:$PATH
    ...
```