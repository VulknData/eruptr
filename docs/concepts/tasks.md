# Tasks

Tasks are akin to functions. They take some parameters, execute a function 
and return a result. Tasks are mostly used in step-wise transformations to:

- Unpack data
- Execute an RPC call
- Execute SQL statements (most common)
- Facilitate variables/evaluators

For instance - following a data load from an input stage there are several 
transformations or operations required:

```yaml
defaults:
    params:
        connection: http://user:pass@localhost:8123/mydatabase
input:
    - io.file.stdin
    - io.clickhouse.write:
        table: mydatabase.mytable
        format: formats.clickhouse.CSV
transform:
    - tasks.clickhouse.execute:
        run:
            - |
                INSERT INTO mydatabase.mytable_agg 
                SELECT
                    id, toDate(dt), max(value)
                FROM mydatabase.mytable
                GROUP BY id
            - DROP TABLE IF EXISTS mydatabase.tmp_mytable_idx
            - |
                CREATE TABLE mydatabase.tmp_mytable_idx (
                    id Strings,
                    tags Strings
                ) ENGINE = MergeTree
                ORDER BY id
            - |
                INSERT INTO mydatabase.tmp_mytable_idx 
                SELECT
                    id, tags
                FROM mydatabase.mytable
                GROUP BY id, tag
            - EXCHANGE TABLES mydatabase.mytable_idx 
                AND mydatabase.tmp_mytable_idx
    - tasks.clickhouse.export:
        run: SELECT * FROM mydatabase.mytable_idx FORMAT CSV
        filename: /tmp/mytable_dump.csv
    - tasks.pack.gz:
        input: /tmp/mytable_dump.csv
        output: //some/nfs/share/mytable_dump.csv.gz
    - tasks.s3.put:
        bucket: s3://daily-dumps
        source: //some/nfs/share/mytable_dump.csv.gz
```