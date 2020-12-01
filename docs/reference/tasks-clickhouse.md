# tasks.clickhouse

## tasks.clickhouse.execute

Executes the command returning the retcode only and discards the results.

* Parameters
    * `run: str=None` - the SQL query to execute
    * `tag: str=None` - optional user-defined tag for the resource.
    * `connection: str=None` - the string to evaluate
        * Valid formats are:
            * `None` - execute the SELECT query using clickhouse-local
            * `http|https://user:password@host:port/database` - execute the query using the http interface
            * `clickhouse://user:password@host:port/database` - execute the query using the clickhouse-client CLI
    * `insecure: bool=True` - the string to evaluate

* Python

```python
create_success = __tasks__['clickhouse.execute']("""
    CREATE TABLE metrics (,
       dt DateTime, key String, value UInt32',
    ) ENGINE=Log""",
    connection='http://localhost:8123/testdb'
).retcode
```

* YAML:

```yaml
transform:
    - tasks.clickhouse.execute:
        run: |
            CREATE TABLE metrics (
                dt DateTime,
                key String,
                value UInt32
            ) ENGINE=Log
        connection: http://localhost:8123/testdb
    - tasks.clickhouse.execute:
        run: |
            INSERT INTO metrics SELECT * FROM staging_table
        connection: http://localhost:8123/testdb
```

## tasks.clickhouse.export

Exports data into a flat file.

* Parameters
    * `run: str=None` - the SQL query to execute.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `connection: str=None` - the string to evaluate.
        * Valid formats are:
            * `None` - execute the SELECT query using clickhouse-local
            * `http|https://user:password@host:port/database` - execute the query using the http interface
            * `clickhouse://user:password@host:port/database` - execute the query using the clickhouse-client CLI
    * `output_format: str=formats.clickhouse.CSV` - the output format.
    * `path: str=None` - the filename to dump to.
    * `overwrite: bool=False` - overwrite the file if it exists
    * `insecure: bool=True` - the string to evaluate

* YAML

```yaml
transform:
    - tasks.clickhouse.export:
        run: SELECT toStartOfMonth(dt), sum(summary_values) FROM summary
        output_format: formats.clickhouse.CSV
        path: /data/dumps/export.csv
        connection: clickhouse://user:password@host:port/database
```

## tasks.clickhouse.import_file

Imports data from a flat file.

* Parameters
    * `run: str=None` - the SQL query to execute.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `connection: str=None` - the string to evaluate.
        * Valid formats are:
            * `None` - execute the SELECT query using clickhouse-local
            * `http|https://user:password@host:port/database` - execute the query using the http interface
            * `clickhouse://user:password@host:port/database` - execute the query using the clickhouse-client CLI
    * `table: str=None` - the table to write data to.
    * `input_format: str=formats.clickhouse.CSV` - the output format.
    * `path: str=None` - the filename to dump to.
    * `insecure: bool=True` - the string to evaluate

* YAML

```yaml
transform:
    - tasks.clickhouse.import_file:
        table: mydatabase.daily_data
        input_format: formats.clickhouse.CSV
        path: /data/dumps/import.csv
        connection: clickhouse://user:password@host:port/database
```

## tasks.clickhouse.local

Executes the command using clickhouse-local returning retcode, data and value.

* Parameters
    * `run: str` - the SQL query to execute.
    * `tag: str=None` - optional user-defined tag for the resource.
* Python

```python
current_dt = __tasks__['clickhouse.local']('SELECT now()').value
```

* YAML (redundant example but you get the idea):

```yaml
transform:
    - |
        INSERT INTO metrics_agg 
        SELECT
            now(),
            count()
        FROM mytable
        WHERE dt > {{ tasks['clickhouse.local']('SELECT now()').value }}
```

## tasks.clickhouse.select

As per tasks.clickhouse.execute however return data is not discarded.

* Parameters
    * `run: str=None` - the SQL query to execute.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `connection: str=None` - the string to evaluate.
        * Valid formats are:
            * `None` - execute the SELECT query using clickhouse-local
            * `http|https://user:password@host:port/database` - execute the query using the http interface
            * `clickhouse://user:password@host:port/database` - execute the query using the clickhouse-client CLI
    * `insecure: bool=True` - the string to evaluate

* Python

```python
max_value = __tasks__['clickhouse.select'](
    'SELECT max(value) FROM metrics WHERE dt > now() - INTERVAL 7 DAY',
    connection='http://localhost:8123/testdb'
).value
```

* YAML:

```yaml
vars:
    max_value:
        tasks.clickhouse.select:
            run: SELECT max(value) FROM metrics WHERE dt > now()-INTERVAL 7 DAY
            connection: http://localhost:8123/testdb
```
