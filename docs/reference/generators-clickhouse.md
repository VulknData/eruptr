# generators.clickhouse

!!! Generators
    Generators are a preview feature only available to select VulknData users at this time.

## generators.clickhouse.select

Executes the specified query at an interval and send the results as a file to
the input pipeline.

* Parameters
    * `run: str=None` - Command/SQL to execute.
    * `tag: str=None` - Tag for the configuration item.
    * `format: str=None` - Output format for the dataset.
    * `every: int=None` - Number of seconds between executions.
    * `recordsize: int=None` - Send records in batches. None means all records.
    * `connection: str=None` - the data source connection string
        * Valid connections are:
            * `None` - execute the SELECT query using clickhouse-local
            * `http|https://user:password@host:port/database` - execute the query using the http interface
            * `clickhouse://user:password@host:port/database` - execute the query using the clickhouse-client CLI
    * `insecure: bool=True` - the string to evaluate
* YAML

```yaml
generators:
    - generators.clickhouse.select:
        tag: |
            @@ 'clickhouse-select-' + 
            tasks['clickhouse.local']('SELECT NOW()') @@
        run: |
            SELECT id, values 
            FROM mydatabase.mytable 
            WHERE dt > now() - INTERVAL 10 SECOND
        format: formats.clickhouse.JSONEachRow
        every: 10
        recordsize: 10
        connection: clickhouse://user:password@myhost:9000/mydatabase
```

## generators.clickhouse.watch

Create or re-use a LIVE VIEW and WATCH for results. Each result/version will be
sent as a separate file to the input pipeline.

* Parameters
    * `run: str=None` - Name of the LIVE VIEW to watch. If the value provided is
    a SELECT query then a TEMPORARY LIVE VIEW is created and managed instead.
    * `tag: str=None` - Tag for the configuration item.
    * `format: str=None` - Output format for the dataset.
    * `recordsize: int=None` - Send records in batches. None means all records.
    * `connection: str=None` - the data source connection string
        * Valid connections are:
            * `http|https://user:password@host:port/database` - execute the query using the http interface
            * `clickhouse://user:password@host:port/database` - execute the query using the clickhouse-client CLI
    * `insecure: bool=True` - the string to evaluate
* YAML

```yaml
generators:
    - generators.clickhouse.watch:
        tag: |
            @@ 'clickhouse-watch-' + 
            tasks['clickhouse.local']('SELECT NOW()') @@
        run: |
            SELECT id, values
            FROM mydatabase.mytable
            GROUP BY id, values
        format: formats.clickhouse.JSONEachRow
        every: 10
        recordsize: 10
        connection: clickhouse://user:password@myhost:9000/mydatabase
```

## generators.clickhouse.listen

Starts a HTTP service and connects a ClickHouse MATERIALIZED VIEW to the HTTP 
service. This provides a simple live streaming service out of ClickHouse that
can be intercepted for further processing.

* Parameters
    * `run: str=None` - SELECT query to base the MATERIALIZED VIEW on.
    * `tag: str=None` - Tag for the configuration item.
    * `format: str=None` - Output format for the dataset.
    * `recordsize: int=None` - Send records in batches. None means all records.
    * `connection: str=None` - the data source connection string
        * Valid connections are:
            * `http|https://user:password@host:port/database` - execute the query using the http interface
            * `clickhouse://user:password@host:port/database` - execute the query using the clickhouse-client CLI
    * `insecure: bool=True` - the string to evaluate
* YAML

```yaml
generators:
    - generators.clickhouse.listen:
        tag: |
            @@ 'clickhouse-listen-' + 
            tasks['clickhouse.local']('SELECT NOW()') @@
        run: |
            SELECT id, values
            FROM mydatabase.mytable
            GROUP BY id, values
        format: formats.clickhouse.JSONEachRow
        every: 10
        recordsize: 10
        connection: clickhouse://user:password@myhost:9000/mydatabase
```