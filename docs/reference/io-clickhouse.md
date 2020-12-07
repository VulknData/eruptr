# io.clickhouse

## io.clickhouse.local

Run a query using clickhouse.local.

* Parameters:
    * `run: str=None` - the query to execute
    * `tag: str=None` - optional user-defined tag for the resource
    * `format: str=formats.clickhouse.CSV` - the output format for the query
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.clickhouse.local:
        run: SELECT number FROM system.numbers(1000)
        format: formats.clickhouse.CSV
    - io.file.write: /tmp/1000numbers.csv
```

## io.clickhouse.select

Run a query against the ClickHouse datasource.

* Parameters:
    * `run: str=None` - the query to execute.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `format: str=None` - the input data format.
    * `connection: str=None` - the connection string for the database.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.clickhouse.select:
        run: SELECT id, tags, max(value) FROM mydatabase.mytable
        format: formats.clickhouse.JSON
        connection: clickhouse://user:password@myhost:9000/mydatabase
    - io.file.write: /tmp/json-data.json
```

## io.clickhouse.write

* Parameters:
    * `run: str=None` - the query to execute.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `columns: str|list` - optional input columns/schema definition as comma delimited or a list
    * `table: str=None` - the table to write data to.
    * `format: str=None` - the input data format.
    * `connection: str=None` - the connection string for the database.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args
* YAML - simple file load

```yaml
input:
    - io.file.stdin
    - io.clickhouse.write:
        table: mydatabase.mytable
        format: formats.clickhouse.CSV
        connection: clickhouse://user:password@myhost:9000/mydatabase
```

* YAML - specific columns only

```yaml
input:
    - io.file.stdin
    - io.clickhouse.write:
        columns:
            - id String
            - tag String
            - value UInt32
        table: mydatabase.mytable
        format: formats.clickhouse.CSV
        connection: clickhouse://user:password@myhost:9000/mydatabase
```

* YAML - specify the columns with optional transformation

```yaml
input:
    - io.file.stdin
    - io.clickhouse.write:
        run: |
            SELECT id, tag, max(value)
            FROM input('id String, tag String, value UInt32')
            GROUP BY id, tag
        table: mydatabase.mytable
        format: formats.clickhouse.CSV
        connection: clickhouse://user:password@myhost:9000/mydatabase
```

* YAML - raw - specify the columns and table with optional transformation and 
format via SQL

```yaml
input:
    - io.file.stdin
    - io.clickhouse.write:
        run: |
            INSERT INTO mydatabase.mytable 
            SELECT id, tag, value 
            FROM input('id String, tag String, value UInt32') 
            FORMAT CSV
        connection: clickhouse://user:password@myhost:9000/mydatabase
```
