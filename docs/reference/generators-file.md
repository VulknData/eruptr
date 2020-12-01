# generators.file

!!! Generators
    Generators are a preview feature only available to select VulknData users at this time.

## generators.file.poll

Polls an the local filesystem for input.

* Parameters
    * `run: str` - a regular expression to poll the resource for.
    * `tag: str|list` - a string or list of tags for the resource.
    * `every: int` - the time in seconds between polls.
    * `on_success: task` - the task and params to execute on pipeline success.
    * `on_failure: task` - the task and params to execute on pipeline failure.
* YAML example

```yaml
generators:
    - generators.file.poll:
        tag: filepoll
        run: /data/spool/myfile*.csv.gz
        every: 10
        on_success:
            - tasks.file.move:
                filename: /data/spool/@@ context.tags.filepoll.filename @@
                to: /data/archive/@@ context.tags.filepoll.filename @@
        on_error:
            - tasks.file.move:
                filename: /data/spool/@@ context.tags.filepoll.filename @@
                to: /data/error/@@ context.tags.filepoll.filename @@
```

## generators.file.tail

Tails a file on the local filesystem and sends chunks/lines from the file to the
input pipeline at determined intervals.

* Parameters
    * `run: str` - the filename to watch.
    * `tag: str|list` - a string or list of tags for the resource.
    * `timeout: int` - the maximum time in seconds before accumulated events are 
    sent to the input pipeline.
    * `maxlines: int` - the maximum number of lines to accumulate before sending 
    to a pipeline
    * `on_success: task` - the task and params to execute on pipeline success.
    * `on_failure: task` - the task and params to execute on pipeline failure.
* YAML example - the following will send data every 5 seconds or every 1 million 
lines - which ever occurs earliest.

```yaml
generators:
    - generators.file.tail:
        tag: filetail
        run: /var/log/apache/mysite.com.log
        timeout: 5
        maxlines: 1000000
        on_success:
            - tasks.file.move:
                filename: /var/log/apache/@@ context.tags.filetail.filename @@
                to: /data/archive/@@ context.tags.filetail.filename @@
        on_error:
            - tasks.file.move:
                filename: /var/log/apache/@@ context.tags.filetail.filename @@
                to: /data/error/@@ context.tags.filetail.filename @@
```