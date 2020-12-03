# Pipes

Pipes provide an abstraction on top of simple Linux/Unix interprocess
communication with pipes. Whilst pipes are generally streaming in nature they
should not be confused with streaming pipelines and more general streaming ETL
solutions. Pipes are a critical part of our performance story.

Experience has shown that when processing individual files, simple shell 
pipelines with shell tools vastly outperform large BigData eco-systems in 95% of
all cases. We've worked with examples where several Spark nodes were required to
match the performance of a single node running a handful of shell scripts. Even 
with several nodes the single node, using ClickHouse as the main storage target,
was able to provide realtime (to the second) transformations and analytics - the
Spark solution would have required several more nodes in addition to the main 
nodes to match this use-case.

Of course this doesn't discount Spark, Nifi or Flink - these solutions provide 
greater opportunity and power for inspecting and working with the dataset. They 
would also facilitate the creation of custom logic for data anomalies as part of 
an ETL pipeline. That being said the benefits of such frameworks diminish when 
the file format is mostly structured or the velocity of the data is high. 

Pipe modules differ to other modules in that they provide an input and output
path for one way processing of data in realtime - there is no writing to and from
files or datastores with pipes. Note though that a pipe module can be fed data 
from an input io module or write to an output io module which itself can handle 
writing to a data store.

A typical scenario may be to uncompress a file, then remove the header, before 
replacing commas with tabs and finally writing the file into a datastore.

A shell solution for the above may be:

```shell
cat myfile.csv.gz | \
    gunzip | \
    sed 's/\t/,/g' | \
    tail -n+2 | \
    clickhouse-client -q 'INSERT INTO mydatabase.mytable FORMAT CSV'
```

And an Eruptr input YAML spec may look something like:

```yaml
input:
    - io.file.read: myfile.csv.gz
    - pipes.unpack.gz
    - pipes.text.sed: s/\t/,/g
    - pipes.text.tail: +2
    - io.clickhouse.write:
        table: mydatabase.myfile
        format: formats.clickhouse.CSV
```

You can also perform more complex operations - such as continuously polling an 
S3 endpoint, converting between multiple formats and writing to different 
datastores in a single pipeline:

!!! Generators
    Generators are a preview feature only available to select VulknData users at this time.

```yaml
generators:
    - generators.s3.poll:
        tag: spool
        filename: s3://spool/myfile*.csv.gz
        every: 10s
        on_success:
            - tasks.s3.move:
                filename: s3://spool/@@ context.tags.poll.filename @@
                to: s3://archive/@@ context.tags.poll.filename @@
        on_error:
            - tasks.s3.move:
                filename: s3://spool/@@ context.tags.poll.filename @@
                to: s3://error/@@ context.tags.poll.filename @@
    - generators.s3.poll:
        tag: error
        filename: s3://error/myfile*.csv.gz
        every: 300s
        on_success:
            - tasks.s3.move:
                filename: s3://error/@@ context.tags.poll.filename @@
                to: s3://archive/@@ context.tags.poll.filename @@
input:
    - io.s3.read: @@ context.tags.poll.filename @@
    - pipes.unpack.gz
    - pipes.text.replace:
        search: \t
        replace: ,
    - pipes.text.tail: +2
    - pipes.utils.duplicate:
        to-s3-as-parquet:
            - pipes.clickhouse.local:
                columns:
                    - id String
                    - tag String
                    - value UInt32
                input_format: formats.clickhouse.CSV
                output_format: formats.clickhouse.Parquet
            - pipes.pack.gz
            - io.s3.write:
                bucket: processed
                filename: |
                    s3://processed/
                    @@ context.tags.poll.filename |
                        replace(".csv.gz", ".parquet.gz") @@.parquet.gz
        to-clickhouse:
            - io.clickhouse.local:
                table: mydatabase.mytable
                format: formats.clickhouse.CSV
```

In these types of scenarios Eruptr vastly out performs the likes of Spark or Nifi.
It would finish processing several files before the aforementioned systems have
even finished initialising the JVM and use vastly less memory and CPU power.
