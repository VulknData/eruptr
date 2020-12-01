# Data Ingestion

For batch data loading the processing is centred around a predefined workflow
captured within the logic of the `EruptrLoad` command/task.

By default certain assumptions are made with respect to the modules used in 
each section. When the module is not explicitly specified introspection is often
used to determine if a command is a query, shell, python or other command.

## Command Line Interface

```shell
VulknData Eruptr (C) 2020 VulknData, Jason Godden

GPLv3 - see https://github.com/VulknData/eruptr/COPYING

usage: eruptr load [-h] [--log-level LOG_LEVEL] --conf CONFIG_FILE
                   [--cluster CLUSTER] [--shard SHARD] [--var VARS] [--timing]
                   [--input INPUT] [--source SOURCE] [--name NAME]
                   [--enable ENABLE] [--disable DISABLE] [--flows FLOWS]
                   [--retry RETRY] [--test] [--render]

optional arguments:
  -h, --help            show this help message and exit
  --log-level LOG_LEVEL
                        Optional. The log level (try INFO, WARNING, DEBUG
                        etc..). (default WARNING)
  --conf CONFIG_FILE    Optional. The configuration file for the stream,
                        transformation or let operation
  --cluster CLUSTER     Optional. Override the cluster setting in the YAML
                        configuration.
  --shard SHARD         Optional. Override the shard setting in the YAML
                        configuration.
  --var VARS            Dynamic options that are passed to the template
                        engine. Multiple --var options in key=value format may
                        be provided on the command line.
  --timing              Enable logging timing information

Load mode options:
  --input INPUT         Specify the input type (default - file)
  --source SOURCE       The source object, path or query (default - empty
                        string)
  --name NAME           Optional. A name to provide for the data source
                        (default - SOURCE)
  --enable ENABLE       Comma delimited list of flows to enable
  --disable DISABLE     Comma delimited list of flows to disable
  --flows FLOWS         Comma delimited list of flows to execute - ignores
                        enable/disable flags
  --retry RETRY         Comma delimited list of flows to retry or run on
                        failure
  --test                Test mode - render the configuration and setup
                        executors skipping the actual execution. Note that
                        although no execution takes place there may be side-
                        effects during rendering.
  --render              Like test mode but outputs the rendered configuration
                        only. Executors are not setup.
```

## Configuration Format

In this mode the following file format is used.

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
cluster: <cluster IP address or hostname or SELECT query>
shard: <shard IP address or hostname or SELECT query>
vars:
    my_variable_name: <The variable value>
    ...
workflow:
    - list of flow configurations
    ...
user_defined_flow1:
    ...
user_defined_flow2:
    ...
user_defined_flowN:
    ...
```

## Options

### --log-level LOG_LEVEL

Optional. The log level (try INFO, WARNING, DEBUG etc..). SQL can also be used
to print the SQL queries issued by eruptr. The default is WARNING.

```shell
eruptr load --log-level SQL .. <other options>
```

### --conf CONFIG_FILE

The path to the YAML configuration file for the stream, transformation or load 
operation.

```shell
eruptr load --conf ./myloaders/myjob.yaml
```

### --cluster CLUSTER

Optional. Override the cluster setting in the YAML configuration. Note that this
can be an SQL statement. It will be evaluated using the default or configured
evaluator.

```shell
eruptr load --conf ./myloaders/myjob.yaml \
--cluster clickhouse://user:password@myhost:9000
```

```shell
eruptr load --conf ./myloaders/myjob.yaml \
--cluster "
    SELECT 
        'clickhouse://' || currentUser() || 
        '@myhost-' || toString(cityHash64({{ opts.name }})%3) || 
        ':9000'
    "
```

### --shard SHARD

Optional. Override the shard setting in the YAML configuration. Note that this
can be an SQL statement. It will be evaluated using the default or configured
evaluator.

```shell
eruptr load --conf ./myloaders/myjob.yaml \
--shard clickhouse://user:password@myhost:9000
```

```shell
eruptr load --conf ./myloaders/myjob.yaml \
--shard "
    SELECT 
        'clickhouse://' || currentUser() || 
        '@myhost-' || toString(cityHash64({{ opts.name }})%3) || 
        ':9000'
    "
```

### --var VARS

Dynamic options that are passed to the template engine. Multiple --var options 
in key=value format may be provided on the command line.

```shell
eruptr load --conf ./myloaders/myjob.yaml \
--var somevariable=foo \
--var someothervariable=bar
```

### --timing

Enables logging timing information.

### --input INPUT

Specify the input type (default - file). This allows you to 'wire up' inputs 
dynamically.

In your workflow section you can nominate an 'input' flow. Only one 'input'
flow will be used (the first found in the workflow list).

Set the input property on one of your flows in the configuration:

```yaml
workflows:
    - pre:
        executor: StepExecutor
    - input:
        executor: UnixPipeExecutor
        input: true
    - transform:
        ...
input:
    - io.file.read: myfile.csv.gz
    - pipes.unpack.unpack
    ...
```

When you run the load operation as-is it will execute io.file.read and on 
myfile.csv.gz as per the configuration.

However you can override the input, say for testing different files, to use 
io.file.stdin dynamically as follows:

```shell
cat myotherdata.csv.gz | \
eruptr load --conf myconf.yaml --input io.file.stdin
```

This will rewrite the input dynamically:

```yaml
input:
    - io.file.stdin
    - pipes.unpack.unpack
    ...
```

### --source SOURCE

The source object, path or query (default - empty string)

### --name NAME

Optional. A name to provide for the data source (default - SOURCE)

### --enable ENABLE

A comma delimited list of flows to enable. By default only flows with `enable=true`
specified in their workflow configuration will execute. To enable other flows
you can provide a comma delimited list of flows here. Note the order of the flow
is never changed - this is set by the order you specify in the workflow section
in the configuration file.

In the example below only the input and transform flows are enabled by default.

```yaml
workflow:
    - testdata:
        executor: StepExecutor
    - create:
        executor: StepExecutor
    - input:
        executor: UnixPipeExecutor
        enable: true
    - transform:
        executor: StepExecutor
        enable: true
    - clean:
        executor: StepExecutor
```

To generate testdata and create database objects in the example above you can 
use enable:

```shell
eruptr load --conf myconf.yaml --enable testdata,create
```

This will run the testdata, input and transform flows in that order.

### --disable DISABLE

Comma delimited list of flows to disable. Opposite of `--enable`. For example,
using the configuration above you could disable the transform part of the workflow
using the following:

```shell
eruptr load --conf myconf.yaml --enable testdata --disable transform
```

This will now only execute the testdata and input flows. Any combination of 
enable/disable may be used.

### --flows FLOWS

Comma delimited list of flows to execute - ignores enable/disable flags. This is
an explicit list of flows to execute (in the order you defined in your workflow).

For example - using the workflow defined defined in the `--enable` example - you 
could opt to run the clean flow only:

```shell
eruptr load --conf myconf.yaml --flows clean
```

### --retry RETRY

Comma delimited list of flows to retry or run on failure. This can provide 
some benefits for deployments or in cases where retries may be required.

Using the workflow defined in `--enable` example. A load job may be deployed
to a new database instance and the necessary table objects defined in the 
`create` flow may not exist. Without the `--retry` flag the `create` flow will 
never be executed and the task will fail. With the `--retry` option you can 
tell eruptr to retry the job, with the specified flows enabled.

```shell
eruptr load --conf myconf.yaml --retry create

.. ERROR: Load task failed. Retrying...
.. SQL: CREATE TABLE IF NOT EXISTS... 

OK!
```

### --test

Test mode - render the configuration and initialise the flow execution pipelines
skipping the actual execution. Note that although no execution takes place there 
may be side-effects during rendering and initialisation.

### --render

Like test mode but outputs the rendered configuration only. Executors are not 
initialised.
