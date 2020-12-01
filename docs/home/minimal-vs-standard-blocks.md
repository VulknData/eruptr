
## Minimal vs Standard blocks

Each section is defined in blocks that specify the module and associated
configuration. In standard mode all options must be specified including the 
module and the `run` parameter. The `run` parameter is a consistent key passed
to each function specifying the command to execute. This has different meanings
depending on the module context.

A standard block to execute a streaming shell command might look as follows:

```yaml
input:
    - pipes.shell.cmd:
        run: zcat {{ opts.name }}
    # Simple key:value representation below is also valid.
    - pipes.shell.cmd: grep -v '^ABC'
    - io.clickhouse.write:
        table: mydatabase.mydata
        format: formats.clickhouse.CSV
        connection: clickhouse://user:password@myhost:9000/mydatabase
```

Each block is executed in order. Within the input section example above this will 
be executed by the stream executor as:

```bash
zcat <inputfilename> | \
grep -v '^ABC' | \
clickhouse-client \
    --host myhost \
    --port 9000 \
    --user user \
    --password password \
    --database mydatabase \
    -q "INSERT INTO mydatabase.mydata FORMAT CSV"
```

This could also be specified as a single block by providing a list to the `run` option.

```yaml
input:
    - pipes.shell.cmd:
        run:
          - zcat {{ opts.name }}
          - grep -v '^ABC'
    - io.clickhouse.write:
        table: mydatabase.mydata
        format: formats.clickhouse.CSV
        connection: clickhouse://user:password@myhost:9000/mydatabase
```

In the example above the `pipes.shell.cmd` module only accepts single shell 
commands. The `pipes.shell.pipeline` module could be used instead:

```yaml
input:
    - pipes.shell.pipeline: zcat {{ opts.name }} | grep -v '^ABC'
    - io.clickhouse.write:
        table: mydatabase.mydata
        format: formats.clickhouse.CSV
        connection: clickhouse://user:password@myhost:9000/mydatabase
```

Minimal blocks on the other hand are simple strings comprised of the `run` 
parameter only and don't include any additional parameters. Eruptr will use 
the default handler and some internal logic to determine the type of command 
to execute. The following will automatically use the `input_io_stream` 
handler (default `pipes.shell.pipeline`) and the `input_sql_insert` handler.

```yaml
defaults:
    params:
        connection: clickhouse://user:password@myhost:9000/mydatabase
input:
    - zcat {{ opts.name }} | grep -v '^ABC'
    - |
        INSERT INTO mydatabase.mydata 
        SELECT * 
        FROM input('field1 String, field2 String')
        FORMAT CSV
```

or

```yaml
input:
    - zcat {{ opts.name }}
    - grep -v '^ABC'
    ...
```

For the INSERT command the `pipes.clickhouse.insert` module will determine
the `table` and `format` from the query and the `connection` information
from the default params clause.

Eruptr will automatically determine whether it's evaluating a minimal or 
standard block.