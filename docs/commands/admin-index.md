# Database Administration

For batch data loading the processing is centred around a predefined workflow
captured within the logic of the `EruptrBatch` command/task.

By default certain assumptions are made with respect to the modules used in 
each section. When the module is not explicitly specified introspection is often
used to determine if a command is a query, shell, python or other command.

## Command Line Interface

```shell
usage: eruptr admin [-h] [--log-level LOG_LEVEL] --conf CONFIG_FILE
                    [--shard SHARD] [--var VARS] [--timing] [--create]
                    [--drop] [--reset] [--distributed]

optional arguments:
  -h, --help            show this help message and exit
  --log-level LOG_LEVEL
                        Optional. The log level (try INFO, WARNING, DEBUG
                        etc..). (default WARNING)
  --conf CONFIG_FILE    Optional. The configuration file for the stream,
                        transformation or let operation
  --shard SHARD         Optional. Override the shard setting in the YAML
                        configuration.
  --var VARS            Dynamic options that are passed to the template
                        engine. Multiple --var options in key=value format may
                        be provided on the command line.
  --timing              Enable logging timing information

Administrative options:
  --create              Execute the 'create' section in the YAML configuration
                        (default - no create)
  --drop                Execute the 'drop' section in the YAML configuration
                        (default - no drop)
  --reset               Execute the 'reset' section in the YAML configuration
                        (default - no reset)
  --distributed         Execute the 'distributed' section in the YAML
                        configuration (default - no distributed statements)
```                        

## Configuration Format

In batch processing mode the following file format is used.

```yaml
name: <The name of the workflow>
defaults:
    handlers:
        predefined_action_1: module.default.name
        predefined_action_2: module.default.name
        ...
    params:
        key: <parameter default to apply to each section or module>
        ...
shard: <shard IP address or hostname>
vars:
    my_variable_name: <The variable value>
    ...
create:
    - <List of SQL CREATE commands>
    - ...
drop:
    - <List of SQL DROP commands>
    - ...
reset:
    - <List of SQL reset commands (typically DROP, TRUNCATE or DELETE)>
    - ...
distributed:
    - <List of distributed SQL commands to run on all shards>
    - ...
```

