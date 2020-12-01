## Templating

Templating is a very powerful feature. By default Eruptr makes two template 
engines - Jinja and Mako templates - available during configuration pre-processing.
You can also use Jinja templates *during* execution. Here Eruptr adds a third
layer of templating that can refer to any of the following objects as well as
any inter-task shared variables, results and data.

The following objects are available to both engines:

- `opts` - the CLI options passed in.
- `vars` - the processed variables following first pass. Variables can also be 
overridden via the command line.
- `cfg` - the rendered configuration following first pass.
- `context` - inter-task shared variables. Only available during execution.

#### Example

In the example below Mako templates are used to import direct Python modules into
the configuration and evaluate the filename variable using the `os.path` module.

The `filename` variable is then made available within the `vars` dictionary and
Jinja templating is used to render the final value into the create and insert
sections. This is for demonstration purposes only. There is no reason to use 
Jinja over Mako or mix the two (unless required). Likewise there is also no 
computational cost involved in mixing the two engines.

```yaml
<% import os %>
vars:
    filename: ${os.path.basename(opts.source)}
create:
    - |
        CREATE TABLE mydatabase.`{{ vars.filename }}`
        (
        ...
insert:
    - INSERT INTO mydatabase.`{{ vars.filename }}` ..
```

You can also use the default SQL evaluator if you require features from the SQL 
engine. In this case this is `tasks.clickhouse.local`:

```yaml
vars:
    filename: SELECT basename('{{ opts.source }}')
create:
    - |
        CREATE TABLE mydatabase.`{{ vars.filename }}`
        (
        ...
insert:
    - INSERT INTO mydatabase.`{{ vars.filename }}` ..
```

Test mode with log-level DEBUG can be used to view the rendered configuration
without executing any ETL processes.

```yaml
11/08/2020 09:38:22 PM - DEBUG - Rendered config:
name: Zabbix Data
defaults:
    handlers:
        locks: locks.filesystem
        input_sql_insert: io.clickhouse.write
        input_sql_stream: pipes.clickhouse.local
        input_io_stream: pipes.shell.pipeline
        transform_sql_query: tasks.clickhouse.execute
        transform_sql_select: tasks.clickhouse.select
        transform_shell: tasks.shell.run
        evaluator: tasks.clickhouse.local
    params:
        connection: http://localhost/test
shard: localhost
locks:
-   locks.filesystem:
        locks:
        -   exclusive: zabbix_data
vars:
    dt: '2020-11-08 21:38:22'
input:
-   pipes.shell.cmd:
        run:
        - pigz -d
        - grep '.*,.*,.*,.*'
-   io.clickhouse.write:
        connection: clickhouse://localhost/test
        table: test.zabbix_data
        format: formats.clickhouse.CSV
        run: "SELECT\n    device,\n    toDateTime(epoch_dt) AS t_dt,\n    value,\n   \
            \ tag,\n    'file' AS sys_source_type,\n    basename('../tests/zabbix_data.csv.gz')\
            \ AS sys_source,\n    now() AS sys_dt_created\nFROM input('device String,\
            \ epoch_dt DateTime, value Float32, tag String')\n"
transform:
-   tasks.clickhouse.execute:
        run:
        - OPTIMIZE TABLE test.zabbix_data
        - DROP TABLE IF EXISTS test.tmp_zabbix_data_summary
        - CREATE TABLE IF NOT EXISTS test.zabbix_data_summary ENGINE = MergeTree ORDER
            BY t_dt AS SELECT * FROM test.zabbix_data
        - CREATE TABLE IF NOT EXISTS test.tmp_zabbix_data_summary ENGINE = MergeTree ORDER
            BY t_dt AS SELECT * FROM test.zabbix_data
        - EXCHANGE TABLES test.zabbix_data_summary AND test.tmp_zabbix_data_summary
        - DROP TABLE IF EXISTS test.tmp_zabbix_data_summary
        connection: http://localhost/test
        insecure: true
create:
- "CREATE TABLE IF NOT EXISTS test.zabbix_data\n(\n    device String COMMENT '@dimension:\
    \ Zabbix monitored device name',\n    t_dt DateTime COMMENT '@timeseries: Series\
    \ key',\n    value Float32 COMMENT '@metric: Metric value',\n    tag String COMMENT\
    \ '@dimension: Column name',\n    sys_source_type String COMMENT '@system: Source\
    \ type (file/table/stream)',\n    sys_source String COMMENT '@system: Source filename',\n\
    \    sys_dt_created DateTime COMMENT '@system: Record creation timestamp'\n)\n\
    ENGINE = MergeTree\nORDER BY t_dt\n"
drop:
- DROP TABLE IF EXISTS test.zabbix_data
```

### `vars`

The `vars` template dictionary is populated from the `vars` section within the
YAML file in the first pass. They can be used anywhere within the configuration
file.

```yaml
vars:
    cutoff_dt: 2020-10-15
    dataset: daily_extract
insert:
    - INSERT INTO mydatabase.mytable SELECT *, '{{ vars.dataset }}' ...
```

The default `evaluator` handler (`tasks.clickhouse.local`) is used when 
evaluating variables - this can be overridden through the `defaults` section.

In minimal blocks the evaluator will activate only if the variable begins with `SELECT`:

```yaml
vars:
    dt_cutoff: 2020-10-15 # <-- This will be interpreted as text
    dt_current: SELECT now() # <-- This will be evaluated using (engines.clickhouse.evaluator) clickhouse-local
    dataset: daily_extract # <-- This will be interpreted as text
```

You can use standard blocks as well and provide the full name of the module on 
a variable by variable basis.

!!! Note
    The `engines.sqlserver` module does not exist and is used as an example only. Would you like to contribute?

```yaml
vars:
    dt_cutoff:
        engines.sqlserver.execute:
            connection: sqlserver://sa:password@mysqlserverhost.local/accounts
            run: SELECT min(date) FROM bitcoin_accounts_cutoff
    dt_current:
        tasks.clickhouse.local:
            run: SELECT now()
    dataset: daily_extract
    ...
```

`vars` may also be overridden or created via the CLI:

```bash
./eruptr --var shard=http://myshard.host.local --var dataset=user_provided ... <other options>
```

This can be useful for once off task configuration or increasing flexibility.

### `opts`

The `opts` template dictionary is populated from the CLI options when eruptr is 
called in. You can see the set options by specifying the DEBUG log level. It is 
usually the first line printed to STDERR during a run.

Use this to populate the filename (use name or source), customise the shard/connection
or apply templating logic driven by other CLI options.

```shell
./eruptr batch --log-level DEBUG --conf ../tests/zabbix_data_full.yaml \
--source ../tests/zabbix_data.csv.gz --input io.file.read

11/08/2020 12:18:33 AM - DEBUG - Options: Namespace(
    cls=<class 'eruptr.commands.batch.EruptrBatch'>,
    conf='../tests/zabbix_data_full.yaml',
    create=False,
    distributed=False,
    drop=False,
    input='io.file.read',
    log_level='DEBUG',
    name=None,
    reset=False,
    retry_create=False,
    shard=None,
    source='../tests/zabbix_data.csv.gz',
    timing=False,
    vars=None)
```

### cfg

The `cfg` template dictionary contains the entire configuration following the 
first pass. This could be used to make more complex decisions based on the entire 
workflow.
