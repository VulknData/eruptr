# I/O

I/O modules provide read/write support for all types of data stores, object stores 
and filesystems.

They must provide input or output (read or write) features only. No specific
function can provide both input/output and separate modules must be specified 
in a chain.

For example - you can use an I/O module to read from a file and write to a data store:

```yaml
defaults:
    params:
        connection: clickhouse://user:pass@hostname:9000/mydatabase
input:
    - io.file.read:
        filename: myfile.csv
    - pipes.utils.duplicate:
        - io.clickhouse.write:
            table: mydatabase.table
            format: formats.clickhouse.CSV
        - io.clickhouse.write:
            table: mydatabase.object_store
            format: formats.clickhouse.RawBLOB
```