# YAML Configuration

## Example

Eruptr uses YAML for it's configuration files. A sample configuration for batch
processing using minimal block format can be seen below.

```yaml
name: Zabbix Data
shard: http://localhost/test
locks:
    - exclusive: zabbix_data
vars:
    dt: SELECT now()
pre:
    - DROP TABLE IF EXISTS test.tmp_zabbix_data_summary
input:
    - pigz -d 2>/dev/null
    - grep '.*,.*,.*,.*'
    - |
        INSERT INTO test.zabbix_data
        SELECT
            device,
            toDateTime(epoch_dt) AS t_dt,
            value,
            tag,
            'file' AS sys_source_type,
            basename('{{ opts.name or opts.source }}') AS sys_source,
            '{{ vars.dt }}' AS sys_dt_created
        FROM input('device String, epoch_dt DateTime, value Float32, tag String')
        FORMAT CSV
transform:
    - OPTIMIZE TABLE test.zabbix_data
    - DROP TABLE IF EXISTS test.tmp_zabbix_data_summary
    - |
        CREATE TABLE IF NOT EXISTS test.zabbix_data_summary
            ENGINE = MergeTree ORDER BY t_dt AS
        SELECT * FROM test.zabbix_data
    - |
        CREATE TABLE IF NOT EXISTS test.tmp_zabbix_data_summary
            ENGINE = MergeTree ORDER BY t_dt AS
        SELECT * FROM test.zabbix_data
    - EXCHANGE TABLES test.zabbix_data_summary AND test.tmp_zabbix_data_summary
    - DROP TABLE IF EXISTS test.tmp_zabbix_data_summary
on_error:
    - DROP TABLE IF EXISTS test.tmp_zabbix_data_summary
create:
    - CREATE DATABASE IF NOT EXISTS test ENGINE = Atomic
    - |
        CREATE TABLE IF NOT EXISTS test.zabbix_data
        (
            device String COMMENT '@dimension: Site/physical name for equipment',
            t_dt DateTime COMMENT '@timeseries: Series key',
            value Float32 COMMENT '@metric: Metric value',
            tag String COMMENT '@dimension: Column name',
            sys_source_type String COMMENT '@system: Source type (file/table/stream)',
            sys_source String COMMENT '@system: Source filename',
            sys_dt_created DateTime COMMENT '@system: Record creation timestamp'
        )
        ENGINE = MergeTree
        ORDER BY t_dt
drop:
    - DROP TABLE IF EXISTS test.zabbix_data
```
