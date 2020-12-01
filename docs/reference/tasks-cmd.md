# tasks.cmd

## tasks.cmd.cmd

Execute a command on the local system.

* Parameters:
    * `run: str=None` - the command to execute.
    * `tag: str=None` - optional user-defined tag for the resource
    * `env: dict` - key/value environment variables to pass to the command.
* YAML

```yaml
vars:
    output_dir: SELECT '/data/output/' || toString(toDate(now()))
transform:
    - INSERT INTO summary SELECT dt, sum(value) FROM mydatabase.mytable
    - tasks.cmd.cmd: mkdir -p {{ vars.output_dir }}
    - tasks.clickhouse.export:
        run: SELECT toStartOfMonth(dt), sum(summary_values) FROM summary
        format: formats.clickhouse.CSV
        filename: {{ vars.output_dir }}/export.csv
    ...
```

## tasks.cmd.shell

As per tasks.shell.cmd however starts a shell and executes the given shell 
pipeline within the shell.

* Parameters:
    * `run: str=None` - the shell pipeline to execute.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `shell: str='/bin/sh'` - the shell to execute the command with.
    * `env: dict` - key/value environment variables to pass to the shell.

```yaml
transform:
    - tasks.cmd.shell:
        run: cat /proc/devices/foo-device | grep -v 'DEVICE=3' > device3.list 
        shell: /bin/bash
        env:
            PATH: /opt/mybins:$PATH
    ...
```

## tasks.cmd.script

Execute the given script.

* Parameters:
    * `run: str=None` - the shell script content to execute.
    * `tag: str=None` - optional user-defined tag for the resource
    * `shell: str='/bin/sh'` - the shell to execute the script with.
    * `env: dict` - key/value environment variables to pass to the shell.

* YAML (*thanks https://tldp.org/LDP/abs/html/procref1.html for the shell example)

```yaml
tasks:
    - tasks.cmd.script:
        run: |
            #!/bin/bash

            devfile="/proc/bus/usb/devices"
            text="Spd"
            USB1="Spd=12"
            USB2="Spd=480"

            bus_speed=$(fgrep -m 1 "$text" $devfile | awk '{print $9}')

            if [ "$bus_speed" = "$USB1" ]
            then
                echo "USB 1.1 port found."
            fi

            exit 0
        shell: /bin/bash
        env:
            PATH=/opt/mybins:$PATH
    ...
```