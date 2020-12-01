# generators.s3

!!! Generators
    Generators are a preview feature only available to select VulknData users at this time.

## generators.s3.poll

Polls an S3 endpoint for data.

* Parameters
    * `run: str` - a regular expression to poll the resource for.
    * `tag: str|list` - a string or list of tags for the resource.
    * `s3-key: str` - the S3 authentication key.
    * `s3-secret: str` - the S3 authentication secret.
    * `every: int` - the time in seconds between polls.
    * `on_success: task` - the task and params to execute on pipeline success.
    * `on_failure: task` - the task and params to execute on pipeline failure.
* YAML example

```yaml
generators:
    - generators.s3.poll:
        tag: s3poll
        run: s3://spool/myfile*.csv.gz
        s3-key: mykey
        s3-secret: mysecret
        every: 10
        on_success:
            - tasks.s3.move:
                filename: s3://spool/@@ context.tags.s3poll.filename @@
                to: s3://archive/@@ context.tags.s3poll.filename @@
        on_error:
            - tasks.s3.move:
                filename: s3://spool/@@ context.tags.s3poll.filename @@
                to: s3://error/@@ context.tags.s3poll.filename @@
```