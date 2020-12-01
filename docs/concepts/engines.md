# Engines

Engines are basic data system connection helpers. Think of them as an ODBC 
connection to a datasource. They should be relatively simple modules that 
support an execute method and provide any specialised helper methods that
can be re-used by other modules.

As of the first release only the `clickhouse` engine is available. This provides
interfaces using both the http and CLI clients along with parsers for the URI.

Engines are available within your execution modules using the dunder dictionary
`__engines__`. There is no need to import an engine module directly unless you 
need to import specific specialised functions not exposed through the engine
interface.

* Example

```python
def select(run, connection=None):
    return __engines__['clickhouse.execute'](
        query=run,
        connection=connection,
        output_format='TSV'
    )
```