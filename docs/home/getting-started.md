# Getting Started

Let's use one of the provided examples. This assumes you have a ClickHouse 
server running on your local system listening on standard ports with no default
credentials (default/empty password).

simple1.yaml:

```yaml
name: Simple1 Batch Job
shard: clickhouse://localhost/test
workflow:
  - drop:
      executor: StepExecutor
  - create:
      executor: StepExecutor
      enabled: true
  - data:
      executor: StepExecutor
  - pre:
      executor: StepExecutor
      enabled: true
  - input:
      executor: UnixPipeExecutor
      enabled: true
  - post:
      executor: StepExecutor
  - clean:
      executor: StepExecutor
data:
  - tasks.file.write:
      path: system_metrics.csv
      data: |
        "device1","1970-04-27 03:46:40",32.3,"temperature"
        "device1","1970-04-27 03:46:40",10.2,"watts"
  - tasks.pack.gz:
      input_file: system_metrics.csv
      output_file: system_metrics.csv.gz
pre:
  - TRUNCATE TABLE simple1.system_metrics
input:
  - io.file.read: system_metrics.csv.gz
  - pipes.unpack.gz
  - io.clickhouse.write:
      table: simple1.system_metrics
      format: formats.clickhouse.CSV
post:
  - tasks.file.delete: system_metrics.csv.gz
create:
  - CREATE DATABASE IF NOT EXISTS simple1
  - |
    CREATE TABLE IF NOT EXISTS simple1.system_metrics
    (
      device String,
      epoch_dt DateTime,
      value Float32,
      tag String
    ) ENGINE = Log
clean:
  - DROP TABLE IF EXISTS simple1.system_metrics
  - DROP DATABASE IF EXISTS simple1
```

First lets generate some test data:

```bash
eruptr load --conf ../examples/simple1/simple1.yaml \
--log-level INFO --flows data

VulknData Eruptr (C) 2020 VulknData, Jason Godden

GPLv3 - see https://github.com/VulknData/eruptr/COPYING

12/01/2020 09:14:40 PM - INFO - Rendering configuration
12/01/2020 09:14:40 PM - INFO - Running "Simple1 Batch Job"
12/01/2020 09:14:40 PM - INFO - Executing data section
12/01/2020 09:14:40 PM - INFO - StepExecutor: tasks.file.write(
    {'path': 'system_metrics.csv', 'data': '"device1","1970-04-27 03:46:40",
    32.3,"temperature"\n"device1","1970-04-27 03:46:40",10.2,"watts"\n'}) ->
     tasks.pack.gz({'input_file': 'system_metrics.csv', 'output_file': 
     'system_metrics.csv.gz'})
12/01/2020 09:14:40 PM - INFO - Successfully completed "Simple1 Batch Job"

OK - Simple1 Batch Job - SUCCESS
```

Using the --flows option we've told eruptr to execute the `data` flow only.

Great. This has provided us with a simple dataset we can import. If we don't 
specify any flows eruptr automatically runs only the enabled workflows in the
order they're defined (create, pre and input).

```bash
eruptr load --conf ../examples/simple1/simple1.yaml --log-level INFO

VulknData Eruptr (C) 2020 VulknData, Jason Godden

GPLv3 - see https://github.com/VulknData/eruptr/COPYING

12/01/2020 09:24:04 PM - INFO - Rendering configuration
12/01/2020 09:24:04 PM - INFO - Running "Simple1 Batch Job"
12/01/2020 09:24:04 PM - INFO - Executing create section
12/01/2020 09:24:04 PM - INFO - StepExecutor: tasks.clickhouse.execute(
    CREATE DATABASE IF NOT EXISTS simple1) -> tasks.clickhouse.execute(
        CREATE TABLE IF NOT EXISTS simple1.system_metrics ( device String, 
        epoch_dt DateTime, value Float32, tag String ) ENGINE = Log )
12/01/2020 09:24:04 PM - INFO - Executing pre section
12/01/2020 09:24:04 PM - INFO - StepExecutor: tasks.clickhouse.execute(
    TRUNCATE TABLE simple1.system_metrics)
12/01/2020 09:24:04 PM - INFO - Executing input section
12/01/2020 09:24:04 PM - INFO - UnixPipeExecutor: <function read at 
0x7f9e0d61ed90>(run='system_metrics.csv.gz', 
connection='clickhouse://localhost/test' | <function <lambda> at 
0x7f9e0d62bd08>(run='None', connection='clickhouse://localhost/test' | 
<function write at 0x7f9e0d61ed08>(connection='clickhouse://localhost/test', 
table='simple1.system_metrics', format='formats.clickhouse.CSV'
12/01/2020 09:24:04 PM - INFO - Successfully completed "Simple1 Batch Job"

OK - Simple1 Batch Job - SUCCESS
```

And what can we see in ClickHouse?

```sql
hulk :) SELECT * FROM simple1.system_metrics FORMAT CSV;

SELECT *
FROM simple1.system_metrics
FORMAT CSV

Query id: f4c471b1-f32a-4636-8e62-d923e5dc10c4

"device1","1970-04-27 03:46:40",32.3,"temperature"
"device1","1970-04-27 03:46:40",10.2,"watts"

2 rows in set. Elapsed: 0.005 sec. 
```

Perfect. So eruptr has created the necessary database, then table(s) and then
extracted and loaded our data.

This is a trivial example though. Explore the documentation further to see how 
you can create complex workflows with everything from custom shell commands to
embedded Python all driven by simple YAML. Or combine Mako and Jinja to create
re-usable macros for processing your data.