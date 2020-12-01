# engines.clickhouse

## engines.clickhouse.execute

* Parameters:
    * `run: str=None` - the string to evaluate
    * `tag: str=None` - optional user defined tag for the resource
    * `connection: str=None` - the data source connection string
        * Valid formats are:
            * `None` - execute the SELECT query using clickhouse-local
            * `http|https://user:password@host:port/database` - execute the query using the http interface
            * `clickhouse://user:password@host:port/database` - execute the query using the clickhouse-client CLI
    * `insecure: bool=True` - the string to evaluate
    * `**kwargs` - any clickhouse settings in `{'key': 'value'}` format.
* Returns: the result of the query or the original string.
* Python

```python
dt = __engines__['clickhouse.select'](
    'SELECT now()',
    connection='http://localhost:8123/testdb'
)
```

## engines.clickhouse.local

* Parameters:
    * `run: str=None` - the string to evaluate
    * `tag: str=None` - optional user defined tag for the resource
    * `output_format: str='JSON'` - the output format - JSON format is automatically converted into a dictionary.
    * `**kwargs` - any clickhouse-local settings in `{'key': 'value'}` format.
* Returns: the result of the query or the original string if no select query specified.
* Python

```python
dt = __engines__['clickhouse.local']('SELECT now()')
```