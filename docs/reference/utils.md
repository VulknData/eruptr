# utils

## utils.noop

This is a no-op function that returns the data as passed in.

* Parameters:
    * `run: str=''` - the string to evaluate.
    * `tag: str=None` - optional user defined tag for the resource.
* Returns: the string passed to the 'run' parameter unchanged.

* Python

```python
query = __eruptr__['utils.noop']('SELECT now()')
print(query)

>> SELECT now()
```

* Standard YAML

```yaml
vars:
    query:
        utils.none: SELECT now()
```

* Minimal YAML. By default SELECT statements are evaluated by the 
tasks.clickhouse.local function.

```yaml
defaults:
    handlers:
        evaluator: utils.none
vars:
    query: SELECT now()
```

* Templates

```yaml
vars:
    jinja_query: {{ eruptr['utils.none']('SELECT now()') }}
    mako_query: ${eruptr['utils.none']('SELECT now()')}
```