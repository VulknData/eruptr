# pipes.clickhouse

## pipes.clickhouse.local

Transforms the input data as per the specified query. If a query is not provided
the data is returned as-is applying any output format transformations.

* Parameters:
    * `run: str=None` - the query/transformation execute.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `structure: str=None` - list or comma delimited string representing the 
    columns in the input stream.
    * `input_format: str='formats.clickhouse.CSV'` - the format for the input stream.
    * `output_format: str='formats.clickhouse.CSV'` - the format for the output stream.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args

* YAML

```yaml
input:
    - io.file.stdin
    - pipes.clickhouse.local:
        run: |
            SELECT
                id, 
                cityHash64(id) AS hash, 
                tag, 
                toFloat32(value) AS value
            FROM table
        columns:
            - id String
            - tag String
            - value UInt32
        input_format: formats.clickhouse.CSV
        output_format: formats.clickhouse.JSONEachRow
    - io.file.stdout
```
