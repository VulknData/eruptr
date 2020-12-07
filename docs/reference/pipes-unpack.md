# pipes.unpack

## pipes.unpack.unpack

This is a generic unpack/decompress function that accepts the type of compression
as the key.

* Parameters:
    * `run: str='gz'` - the packing method to use when compressing.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args
* YAML

```yaml
input:
    - io.file.read: /tmp/file.csv.gz
    - pipes.unpack.unpack:
        run: gz
    - io.file.write: /tmp/file.csv
```

## pipes.unpack.gz

A shorthand for `run='gz'` using the pipes.unpack.unpack function.

* Parameters:
    * `run: str=None` - this parameter is ignored.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variable.    
    * `**kwargs` - other keyword args

* YAML

```yaml
input:
    - io.file.read: /tmp/file.csv.gz
    - pipes.unpack.gz
    - io.file.write: /tmp/file.csv
```

## pipes.unpack.bz2

A shorthand for `run=bz2` using the pipes.unpack.unpack function.

* Parameters:
    * `run: str=None` - this parameter is ignored.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args

## pipes.unpack.xz

A shorthand for `run=xz` using the pipes.unpack.unpack function.

* Parameters:
    * `run: str=None` - this parameter is ignored.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args

## pipes.unpack.lz

A shorthand for `run=lz4` using the pipes.unpack.unpack function.

* Parameters:
    * `run: str=None` - this parameter is ignored.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `**kwargs` - other keyword args
