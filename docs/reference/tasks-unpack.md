# tasks.unpack

## tasks.unpack.unpack

This is a generic pack/compression function that accepts the type of compression
as the key.

* Parameters:
    * `run: str='gz'` - the packing method to use when compressing.
    * `input_file: str=None` - the input file to decompress.
    * `output_file: str=None` - the output file name after decompression.
    * `keep_original: bool=False` - whether to keep the original file.
    * `tag: str=None` - optional user-defined tag for the resource.
* YAML

```yaml
transform:
    - tasks.unpack.unpack:
        run: gz
        input_file: clickhouse-export.csv.gz
        output_file: clickhouse-export.csv
    - tasks.clickhouse.import:
    ...
```

## tasks.unpack.gz

A shorthand for `run='gz'` using the tasks.unpack.unpack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `input_file: str=None` - the input file to decompress.
    * `output_file: str=None` - the output file name after decompression.
    * `keep_original: bool=False` - whether to keep the original file.
    * `tag: str=None` - optional user-defined tag for the resource

## tasks.unpack.bz2

A shorthand for `run=bz2` using the tasks.unpack.unpack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `input_file: str=None` - the input file to decompress.
    * `output_file: str=None` - the output file name after decompression.
    * `keep_original: bool=False` - whether to keep the original file.
    * `tag: str=None` - optional user-defined tag for the resource

## tasks.unpack.xz

A shorthand for `run=xz` using the tasks.unpack.unpack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `input_file: str=None` - the input file to decompress.
    * `output_file: str=None` - the output file name after decompression.
    * `keep_original: bool=False` - whether to keep the original file.
    * `tag: str=None` - optional user-defined tag for the resourcee

## tasks.unpack.lz

A shorthand for `run=lz4` using the tasks.unpack.unpack module.

* Parameters:
    * `run: str=None` - this value is ignored.
    * `input_file: str=None` - the input file to decompress.
    * `output_file: str=None` - the output file name after decompression.
    * `keep_original: bool=False` - whether to keep the original file.
    * `tag: str=None` - optional user-defined tag for the resource