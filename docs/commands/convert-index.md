# Format Conversion

Eruptr can be used to convert and optionally transform data between different
formats as well. An organisation could use this create a data transformation
service, convert old datasets or provide different formats for other systems.

In `convert` mode no configuration file is used. Instead users use the CLI only 
to drive all necessary functions and parameters.

## Command Line Interface

```shell
VulknData Eruptr (C) 2020 VulknData, Jason Godden

GPLv3 - see https://github.com/VulknData/eruptr/COPYING

usage: eruptr convert [-h] [--log-level LOG_LEVEL] [--input INPUT]
                      [--output OUTPUT] --input-schema INPUT_SCHEMA
                      --input-format INPUT_FORMAT --output-format
                      OUTPUT_FORMAT [--transform TRANSFORM] [--timing]

optional arguments:
  -h, --help            show this help message and exit
  --log-level LOG_LEVEL
                        Optional. The log level (try INFO, WARNING, DEBUG
                        etc..). (default WARNING)

Conversion mode options:
  --input INPUT         Specify the input type (default - io.file.stdin)
  --output OUTPUT       Specify the output type (default - io.file.stdout)
  --input-schema INPUT_SCHEMA
                        Comma delimited input schema
  --input-format INPUT_FORMAT
                        Input format (see --list-formats for available input
                        formats)
  --output-format OUTPUT_FORMAT
                        Optional. Output format (see --list-formats for
                        available output formats). (default --input-format)
  --transform TRANSFORM
                        Optional. SQL queries to transform data between
                        formats
  --timing              Enable logging timing information
```

## Options

### --log-level LOG_LEVEL

Optional. The log level (try INFO, WARNING, DEBUG etc..). (default WARNING).

### --input INPUT

Optional. Specify the input type (default - io.file.stdin).

```shell
echo -e 'IT,Manager,80000\nHR,Assistant,70000' | \
./eruptr convert \
--input io.file.stdin \
--input-schema 'department String, title String, wage UInt32' \
--input-format formats.clickhouse.CSV \
--output-format formats.clickhouse.TSKV 2>/dev/null > data.tskv

cat data.tskv
department=IT	title=Manager	wage=80000
department=HR	title=Assistant	wage=70000
```

Parameters to input functions can be provided using key=value notation:

```shell
./eruptr convert \
--input io.file.read:run=data.tskv \
--input-schema 'department String, title String, wage UInt32' \
--input-format formats.clickhouse.TSKV \
--output-format formats.clickhouse.Vertical 2>/dev/null
Row 1:
──────
department: IT
title:      Manager
wage:       80000

Row 2:
──────
department: HR
title:      Assistant
wage:       70000
```

You can also chain input processing. For example:

```shell
--input io.file.read:run=data.tskv.gz,pipes.unpack.unpack
```

Comma is used to delineate between modules and colon between arguments. To provide 
multiple arguments delineate them with colons.

```python
--input io.clickhouse.select:run=SELECT..:connection=http://...
```

The following will read the file and uncompress:

```shell
./eruptr convert \
--input io.file.read:run=data.tskv.gz,pipes.unpack.unpack \
--input-schema 'department String, title String, wage UInt32' \
--input-format formats.clickhouse.TSKV \
--output-format formats.clickhouse.Vertical 2>/dev/null
Row 1:
──────
department: IT
title:      Manager
wage:       80000

Row 2:
──────
department: HR
title:      Assistant
wage:       70000
```

### --output OUTPUT

Optional. Specify the output type (default - io.file.stdout). Output functions 
can also be chained much like input functions. Note the order matters - the IO 
operation/module must always be the last one in the chain.

```shell
./eruptr convert \
--input io.file.read:run=data.tskv.gz,pipes.unpack.unpack \
--input-schema 'department String, title String, wage UInt32' \
--input-format formats.clickhouse.TSKV \
--output-format formats.clickhouse.Vertical \
--output pipes.pack.pack,io.file.write:run=foo.vertical.gz
```

### --input-schema INPUT_SCHEMA

Required. Comma delimited input schema.

```shell
--input-schema 'department String, title String, wage UInt32'
```

### --input-format INPUT_FORMAT

Required. Input format (see the formats.clickhouse module for available input formats).

### --output-format OUTPUT_FORMAT

Optional. Output format (see the formats.clickhouse module for available input formats).
(default --input-format).

### --transform TRANSFORM

Optional. You can specify a custom transformation to occur as part of the 
conversion. The special table name `table` is used as the source for the query.

```shell
./eruptr convert \
--input io.file.read:run=data.parquet.gz,pipes.unpack.unpack \
--input-schema 'department String, title String, wage UInt32' \
--input-format formats.clickhouse.Parquet \
--output-format formats.clickhouse.CSVWithNames \
--transform 'SELECT count() AS total_records FROM table' 2>/dev/null
"total_records"
2
```

### --timing

Enable logging timing information.