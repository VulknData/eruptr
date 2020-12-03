# pipes.text

## pipes.text.awk

Pipes the incoming text stream through AWK.

* Parameters:
    * `run: str` - the awk program to pipe the stream through.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.file.stdin
    - pipes.pack.pack: gz
    - pipes.text.awk: |
        BEGIN {
            FS = "\n"
            RS = "\n/MyCustomDelimiter\n"
        }
        {
            for (i=1; i<=NF; ++i)
                if (split($i, a, "=") > 1) {
                    $i = a[2]
                } else {
                    $i = ""
                }
        } 1
    - io.file.write: /tmp/file.csv.gz
```

## pipes.text.grep

Uses grep to selectively allow only matched lines through the pipeline.

* Parameters:
    * `run: str` - the text to match for.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.file.stdin
    - pipes.pack.pack: gz
    - pipes.text.grep: SystemRecords
    - io.file.write: /tmp/file.csv.gz
```

## pipes.text.head

Uses head to exclude lines from the input stream.

* Parameters:
    * `run: str` - the number of lines to exclude - is passed to head as head 
    -n(+-run).
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.file.stdin
    - pipes.pack.pack: gz
    - pipes.text.head: '+1'
    - io.file.write: /tmp/file.csv.gz
```

## pipes.text.match

Similar to pipes.text.grep but uses AWK to selectively allow only matched lines 
through the pipeline.

* Parameters:
    * `run: str` - the text to match for.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.file.stdin
    - pipes.pack.pack: gz
    - pipes.text.match: SystemRecords
    - io.file.write: /tmp/file.csv.gz
```

## pipes.text.replace

Uses grep to selectively allow only matched lines through the pipeline.

* Parameters:
    * `run: str` - ignored.
    * `search: str='\n'` - the text to find/replace.
    * `replace: str='\n'` - the text to replace the searched text with.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.file.stdin
    - pipes.text.replace:
        search: Foo 
        replace: Bar
    - io.file.write: /tmp/file.csv.gz
```

## pipes.text.sed

Pipes the incoming text stream through sed.

* Parameters:
    * `run: str` - the sed program to pipe the stream through.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.file.stdin
    - pipes.pack.pack: gz
    - pipes.text.sed: |
        s/^/      /
        N
        s/^ *\(......\)\n/\1  /
    - io.file.write: /tmp/file.csv.gz
```

## pipes.text.tail

Uses tail to exclude lines from the input stream.

* Parameters:
    * `run: str` - the number of lines to exclude - is passed to tail as tail 
    -n(+-run).
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.file.stdin
    - pipes.pack.pack: gz
    - pipes.text.tail: '+1'
    - io.file.write: /tmp/file.csv.gz
```