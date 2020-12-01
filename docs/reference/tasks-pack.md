# tasks.pack

## tasks.pack.pack

This is a generic pack/compression function that accepts the type of compression
as the key.

* Parameters:
    * `run: str='gz'` - the packing method to use when compressing.
    * `input_file: str=None` - the input file to compress.
    * `output_file: str=None` - the output file name after compression.
    * `keep_original: bool=False` - whether to keep the original file.
    * `tag: str=None` - optional user-defined tag for the resource.
* YAML

```yaml
transform:
    ...
    - tasks.clickhouse.export:
    ...
    - tasks.pack.pack:
        run: gz
        input_file: clickhouse-export.csv
        output_file: clickhouse-export.csv.gz
```

## tasks.pack.gz

A shorthand for `run='gz'` using the tasks.pack.pack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `input_file: str=None` - the input file to compress.
    * `output_file: str=None` - the output file name after compression.
    * `keep_original: bool=False` - whether to keep the original file.
    * `tag: str=None` - optional user-defined tag for the resource

## tasks.pack.bz2

A shorthand for `run=bz2` using the tasks.pack.pack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `input_file: str=None` - the input file to compress.
    * `output_file: str=None` - the output file name after compression.
    * `keep_original: bool=False` - whether to keep the original file.
    * `tag: str=None` - optional user-defined tag for the resource

## tasks.pack.xz

A shorthand for `run=xz` using the tasks.pack.pack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `input_file: str=None` - the input file to compress.
    * `output_file: str=None` - the output file name after compression.
    * `keep_original: bool=False` - whether to keep the original file.
    * `tag: str=None` - optional user-defined tag for the resourcee

## tasks.pack.lz

A shorthand for `run=lz4` using the tasks.pack.pack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `input_file: str=None` - the input file to compress.
    * `output_file: str=None` - the output file name after compression.
    * `keep_original: bool=False` - whether to keep the original file.
    * `tag: str=None` - optional user-defined tag for the resource