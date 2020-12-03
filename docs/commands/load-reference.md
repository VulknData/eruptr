# Data Ingestion YAML Reference

## name

Simple attribute providing the name of the workflow.

```yaml
name: My Batch Processing Task
```

## defaults

The defaults section allows for defining default variables and modules/handlers
for use throughout the configuration.

```yaml
defaults:
    handlers:
        io_sql_write: io.clickhouse.write
        evaluator: tasks.clickhouse.local
    params:
        connection: clickhouse://user:password@host.name.com:9000/testdatabase
```

## cluster

```yaml
cluster: http://user:password@hostname:8123/mydatabase
```

The cluster can also be dynamically selected based on an SQL query or module. For
example - if datafiles are being delivered from specific devices or IPs and the 
IP is embedded in the filename or other CLI variable you can use the default SQL
evaluator to calculate the cluster.

## shard

```yaml
shard: http://user:password@hostname:8123/mydatabase
```

The shard can also be dynamically selected based on an SQL query or module. For
example - if datafiles are being delivered from specific devices or IPs and the 
IP is embedded in the filename or other CLI variable you can use the default SQL
evaluator to calculate the shard.

```yaml
shard: SELECT 'http://user:password@shard-' || toString(cityHash64(extract('[0-9]*.', {{ opts.name }}))) || ':8123/mydatabase'
```

## vars

Variables can be used to provide file/job wide values into all parts of the 
configuration.

```yaml
vars:
    batch_job: MyCorpBatchJob
```

For instance - this may be used in the insert section as a Jinja variable:

```yaml
input:
    - INSERT INTO ... SELECT <fields> .., {{ vars.batch_job }}
```

You can also specify variables with templated values or via SQL evaluation. 
The configuration file is evaluated twice to allow for injecting
any variables into the Jinja and Mako templating processes.

```yaml
vars:
    dt_now: SELECT now()
    filename: SELECT basename('{{ opts.source }}') 
```

```yaml
input:
    - INSERT INTO ... SELECT <fields> .., '{{ vars.filename }}', toDateTime('{{ vars.dt_now }}')
```

## workflow

Defines the flows and execution/scheduling methods used for each flow in a list.
The order of the flows is important as eruptr will process the flows sequentially.
This allows you define composable pipelines using different executors.

Each flow may also be marked as enabled (`enabled`) - the default is not to run 
the flow. This will automatically run the flow when the configuration is called
without any parameters. 

Flows can also be enabled automatically on retry. If a task fails Eruptr will
retry the flow with any flows marked `retry`. In the flow example, if the 
execution fails, the flow will be retried with the 'create' flow enabled. This 
can come in handy if you want eruptr to automatically deploy your database objects.

```yaml
workflow:
    - testdata:
        executor: StepExecutor
    - create:
        executor: StepExecutor
        retry: true
    - input:
        executor: UnixPipeExecutor
        enabled: true
    - transform:
        executor: StepExecutor
        enabled: true
    - clean:
        executor: StepExecutor
```

The format for a flow definition is:

```yaml
    - flow:
        executor: StepExecutor|UnixPipeExecutor
        enabled: true|false (default false)
        retry: true|false (default false)
```

You can also omit the workflow clause. In this case eruptr will use the following
default workflow:

```yaml
workflow:
    - drop:
        executor: StepExecutor
        enabled: False
    - create:
        executor: StepExecutor
        enabled: False
    - distributed:
        executor: StepExecutor
        enabled: False
    - reset:
        executor: StepExecutor
        enabled: False
    - pre:
        executor: StepExecutor
        enabled: True
    - input:
        executor: UnixPipeExecutor
        enabled: True
    - transform:
        executor: StepExecutor
        enabled: True
```

This tells the load process to evaluate the configuration in this order:

1. Admin mode DROP tables (if enabled) using a task based StepExecutor on the `drop` YAML node.
2. Admin mode CREATE tables (if enabled) using a task based StepExecutor on the `create` YAML node.
3. Admin mode CREATE DISTRIBUTED tables (if enabled) using a task based StepExecutor on the `distributed` YAML node.
4. Admin mode execute any reset commands (if enabled) using a task based StepExecutor on the `reset` YAML node.
5. `pre` - Execute a task based workflow prior to data ingestion using a task based StepExecutor on the `pre` YAML node.
6. `input` - Execute a pipes based workflow after any pre section using a pipes based UnixPipeExecutor on the `input` YAML node.
7. `transform` - Execute a task based workflow after any input section using a task based StepExecutor on the `transform` YAML node.

## "user_defined_flow"

The remainder of the configuration is for user defined flows. Flows are lists of
modules/functions and their associated parameters to execute. See the Module 
Reference section for examples.