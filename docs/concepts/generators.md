# Generators

!!! Generators
    Generators are a preview feature only available to select VulknData users at this time.

Generators facilitate the creation of input files or data into a Pipe or Task 
based workflow. Generators can be thought of as pollers or Python generators 
with the yield keyword.

Generators have their own block within a configuration and serve as an alternate
start phase to an input section.

The example below shows the `s3.poll` generator watching/polling a specific
S3 endpoint every 10s. The list of files will be sent to the pipeline in the
input section. A new pipeline will be created per file. If running in 
multiprocess mode multiple simultaneous pipelines will be created.

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
```
