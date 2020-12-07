# pipes.pack

## pipes.pack.pack

This is a generic pack/compression function that accepts the type of compression
as the key.

* Parameters:
    * `run: str='gz'` - the packing method to use when compressing.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `flags: list=None` - optional list of flags for the pack operation.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.file.stdin
    - pipes.pack.pack: gz
    - io.file.write: /tmp/file.csv.gz
```

## pipes.pack.gz

A shorthand for `run='gz'` using the pipes.pack.pack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `tag: str=None` - optional user-defined tag for the resource
    * `flags: list=None` - optional list of flags for the pack operation.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.file.stdin
    - pipes.pack.gz
    - io.file.write: /tmp/file.csv.gz
```

## pipes.pack.bz2

A shorthand for `run=bz2` using the pipes.pack.pack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `tag: str=None` - optional user-defined tag for the resource
    * `flags: list=None` - optional list of flags for the pack operation.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args

## pipes.pack.xz

A shorthand for `run=xz` using the pipes.pack.pack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `tag: str=None` - optional user-defined tag for the resource
    * `flags: list=None` - optional list of flags for the pack operation.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args

## pipes.pack.lz

A shorthand for `run=lz4` using the pipes.pack.pack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `tag: str=None` - optional user-defined tag for the resource
    * `flags: list=None` - optional list of flags for the pack operation.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args