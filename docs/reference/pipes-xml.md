# pipes.xml

## pipes.xml.xml2kv

Passes XML data through the xml2 command. This produces a flattened key/value 
structure that is easier to parse by ClickHouse. The data does not need to have 
any specific repeating row structure - nested structures are fine.

* Parameters:
    * `run: str=None` - ignored.
    * `tag: str=None` - optional user-defined tag for the resource.
    * `env: dict=None` - additional Popen environment variables
    * `__context__` - run context
    * `**kwargs` - other keyword args

* Example. Given the following XML structure -

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MyRecordSet>
<MyRecord>
    <key1>device-1</key1>
    <dimension1 attr1='foo'>some-dimension</dimension1>
    <dimension2>some-dimension-2</dimension2>
    <dimension3>some-dimension-3</dimension3>
    <value1>10</value1>
    <value2>11.3</value2>
    <value3>0.34</value3>
    <value4>4</value4>
</MyRecord>
<MyRecord>
    <key1>device-2</key1>
    <dimension1 attr1='bar'>some-dimension-dev2</dimension1>
    <dimension2>some-dimension-2</dimension2>
    <dimension3>some-dimension-3</dimension3>
    <value1>14</value1>
    <value2>15.2</value2>
    <value3>0.28</value3>
    <value4>1</value4>
</MyRecord>
</MyRecordSet>
```

pipes.xml.xml2kv will produce the following output:

```python
/MyRecordSet/MyRecord/key1=device-1
/MyRecordSet/MyRecord/dimension1/@attr1=foo
/MyRecordSet/MyRecord/dimension1=some-dimension
/MyRecordSet/MyRecord/dimension2=some-dimension-2
/MyRecordSet/MyRecord/dimension3=some-dimension-3
/MyRecordSet/MyRecord/value1=10
/MyRecordSet/MyRecord/value2=11.3
/MyRecordSet/MyRecord/value3=0.34
/MyRecordSet/MyRecord/value4=4
/MyRecordSet/MyRecord
/MyRecordSet/MyRecord/key1=device-2
/MyRecordSet/MyRecord/dimension1/@attr1=bar
/MyRecordSet/MyRecord/dimension1=some-dimension-dev2
/MyRecordSet/MyRecord/dimension2=some-dimension-2
/MyRecordSet/MyRecord/dimension3=some-dimension-3
/MyRecordSet/MyRecord/value1=14
/MyRecordSet/MyRecord/value2=15.2
/MyRecordSet/MyRecord/value3=0.28
/MyRecordSet/MyRecord/value4=1
```

pipes.clickhouse.local or io.clickhouse.write can then be used to transform the
key/value structure into a more formal schema:

```yaml
{%
  set cols = ['key1|toString', 'attr1|toString', 'dimension1|toString',
              'dimension2|toString', 'dimension3|toString',
              'value1|toUInt16OrNull', 'value2|toFloat32OrNull',
              'value3|toFloat32OrNull', 'value4|toUInt16OrNull']
%}
{% set comma = joiner(",") %}
input:
    - io.file.stdin
    - pipes.unpack.gz
    - pipes.xml.xml2kv
    - io.clickhouse.write:
        run: |
            WITH
                extractAllGroupsVertical(
                    arrayJoin(splitByString('/MyRecordSet/MyRecord\n', data)),
                    '/@?(\\w+)=(.*?)\n'
                ) AS row
            SELECT
                {% for colspec in cols %} {{ comma() }}
                {{ colspec.split('|')[1] }}(
                    arrayFilter(
                        x -> x[1] == '{{ colspec.split('|')[0] }}', 
                        row
                    )[1][2]
                ) AS {{ colspec.split('|')[0] }}
                {% endfor %}
            FROM input('data String')
        table: mydatabase.mytable
        format: formats.clickhouse.RawBLOB
        connection: clickhouse://user:password@myhost:9000/mydatabase
```

This will render the following SQL to pass through to the run argument:

```sql
WITH
    extractAllGroupsVertical(
        arrayJoin(splitByString('/MyRecordSet/MyRecord\n', data)),
        '/@?(\\w+)=(.*?)\n') AS row
SELECT
    toString(arrayFilter(x -> x[1] == 'key1', row)[1][2]) AS key1,
    toString(arrayFilter(x -> x[1] == 'attr1', row)[1][2]) AS attr1,
    toString(arrayFilter(x -> x[1] == 'dimension1', row)[1][2]) AS dimension1,
    toString(arrayFilter(x -> x[1] == 'dimension2', row)[1][2]) AS dimension2,
    toString(arrayFilter(x -> x[1] == 'dimension3', row)[1][2]) AS dimension3,
    toUInt16OrNull(arrayFilter(x -> x[1] == 'value1', row)[1][2]) AS value1,
    toFloat32OrNull(arrayFilter(x -> x[1] == 'value2', row)[1][2]) AS value2,
    toFloat32OrNull(arrayFilter(x -> x[1] == 'value3', row)[1][2]) AS value3,
    toUInt16OrNull(arrayFilter(x -> x[1] == 'value4', row)[1][2]) AS value4
FROM input('data String')
```

This really demonstrates the power of Jinja templating.

For bonus points the above could be turned into a Jinja macro or a custom 
clickhouse pipes function could be created that re-uses the logic of 
pipes.clickhouse.local and the SQL above to service the generic case.

For large files the same process in Spark, Flink or Nifi, using standard Java 
or Python XML parsing libraries, either fails due to memory limits or requires 
many minutes to complete.