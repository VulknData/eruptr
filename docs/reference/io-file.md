# io.file

## io.file.read

Read a file from a local filesystem.

* Parameters:
    * `run: str=None` - the filename to read
    * `tag: str=None` - optional user-defined tag for the resource
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args

* YAML

```yaml
input:
    - io.file.read: /data/spool/incoming/mydata.csv.gz
    - pipes.unpack.gz
    ...
```

## io.file.write

Write to a file on the local filesystem.

* Parameters:
    * `run` - the filename to write
    * `tag: str=None` - optional user-defined tag for the resource
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args

* YAML

```yaml
input:
    - io.file.read: /data/spool/incoming/mydata.csv.gz
    - pipes.unpack.gz
    ...
    - pipes.pack.gz
    - io.file.write: /data/archive/transformed.parquet.gz
```

## io.file.stdin

Read the file as a data stream on stdin.

* Parameters
    * `tag: str=None` - optional user-defined tag for the resource
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args

* YAML

```yaml
input:
    - io.file.stdin
    - pipes.unpack.gz
    - io.clickhouse.write:
        table: mydatabase.mytable
        format: formats.clickhouse.CSV
        connection: clickhouse://user:password@myhost:9000/mydatabase
```

## io.file.stdout

Write the file as a data stream to stdout.

* Parameters
    * `tag: str=None` - optional user-defined tag for the resource

* YAML

```yaml
input:
    - io.file.stdin
    - pipes.unpack.gz
    - io.file.stdout
```
