## Handlers

Eruptr users pre-defined modules for certain operations. This allows configurations 
to be specified using minimal or standard blocks as detailed above.

Handlers can be configured system wide, project wide or at an individual batch/job level.

The default handlers are:

| Handler | Default Module | Used |
| ------- | ------- | ---- |
| `locks` | `locks.filesystem` | Specifies which locking mechanism to use |
| `io_sql_read` | `io.clickhouse.local` | The SQL module to execute for SQL input/read IO |
| `io_sql_write` | `io.clickhouse.write` | Specifies which insert module to use during SQL stream insert |
| `pipes_sql_transform` | `pipes.clickhouse.local` | Default SQL stream processing module to use during input or other stream sections |
| `pipes_command` | `pipes.cmd.shell` | Specifies which non-SQL stream processing module to use during `input` blocks | 
| `task_sql_execute` | `tasks.clickhouse.execute` | SQL module to use during transform or step-based SQL execution |
| `task_sql_select` | `tasks.clickhouse.select` | SQL module to use for step-based SELECT operations |
| `task_command` | `tasks.cmd.shell` | Default non-SQL batch/step processing module to use |
| `evaluator` | `tasks.clickhouse.local` | Default evaluator to use for variables and other standalone components |

With default handlers and default parameters the following block can be defined using minimal syntax.

```yaml
transform:
    - tasks.clickhouse.execute:
        run: |
            INSERT INTO daily_agg
            SELECT id, date, sum(votes) 
            FROM us_election 
            GROUP BY id, date
        connection: http://user:password@myserver:8123/mydatabase
    - tasks.clickhouse.execute:
        run: |
            INSERT INTO monthly_agg
            SELECT id, toStartOfMonth(date) AS month, sum(votes)
            FROM us_election
            GROUP BY id, month
        connection: http://user:password@myserver:8123/mydatabase
    - tasks.clickhouse.execute:
        run: < other query >
        connection: ...
```

With default handlers:

```yaml
defaults:
    handlers:
        task_sql_execute: tasks.clickhouse.execute
    params:
        connection: http://user:password@myserver:8123/mydatabase
transform:
    - |
        INSERT INTO daily_agg
        SELECT id, date, sum(votes)
        FROM us_election
        GROUP BY id, date
    - |
        INSERT INTO monthly_agg
        SELECT id, toStartOfMonth(date) AS month, sum(votes) 
        FROM us_election 
        GROUP BY id, month
    - ... < other queries >
```