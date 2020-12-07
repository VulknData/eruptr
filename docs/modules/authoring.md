# Writing Modules

!!!Note
    As eruptr is new and evolving expect the module interface to change as things
    bed down.

We've made modules very easy to author. The key 

## Dunder dictionaries

The following dunder dictionaries are provided automatically to your modules. 
You don't have to be concerned about importing paths or the order you import 
modules in as eruptr will ensure all modules are visible to each other during
the module discovery process.

### `__eruptr__`

The `__eruptr__` dictionary contains all modules/functions in `type.module.functionname` 
format. For instance you can access the tasks.file.delete function 
`__eruptr__['tasks.file.delete']`.

Only functions that don't begin with underscores are imported.

### `__engines__`

The `__engines__` dictionary contains all engine modules/functions in `module.functionname` 
format. This enables you to execute database operations from within your tasks.

To execute a query against ClickHouse from one your tasks you might call:

```python
raw_result = __engines__['clickhouse.execute'](
    query="SELECT count() FROM system.tables",
    connection=connection,
    output_format='TSV',
    insecure=insecure,
    **kwargs
)
```

### `__tasks__`

The `__tasks__` dictionary contains all task modules/functions in `module.functionname` 
format. It is not uncommon to build modules from stitching together existing
functions.

For example - the `tasks.file.move` function uses the `copy` and `delete`
modules:

```python
@eruptr.utils.timer
def move(run=None, tag=None, src=None, dst=None, **kwargs):
    cp = __tasks__['file.copy'](src=src, dst=dst) 
    # Note we call copy directly in the actual source.
    if cp.retcode != 0:
        return cp
    rm = __tasks__['file.delete'](run=src) 
    # Note we call delete directly in the actual source.
    return rm
```

Where possible you should re-use existing task and engine modules.

### `__context__`

`__context__` is a special dynamic dunder dictionary. It is an object with 
following definition:

- `__context__.current` - The current pipe process or step task, including the 
    flow name, function name and the function arguments as a TaskInfo object. 
- `__context__.previous` - The previous process before the current process as 
    a TaskInfo object
- `__context__.tasks` - A list of all the current tasks in TaskInfo format up
    to the present one in order executed.
- `__context__.tags` - A dictionary of all the current tasks in TaskInfo format 
    up to the present one keyed by the task tag.

You can modify the `__context__.current` TaskInfo object during execution. This
is useful if you have a module that is dependant on an earlier module or can
use the previous module to auto-determine certain parameters.

For instance - say you want to provide some functionality further downstream 
in your execution you could store the value in the `current` object and access
it via tags in the next call:

```python
def myfunction(run=None, tag=None, env=None, **kwargs):
    __context__.current.file_dir = os.path.dirname(run)
    __context__.current.file_name = os.path.basename(run)
    ...
    # Do something here
```

```python
def myotherfunction(run=None, tag=None, env=None, **kwargs):
    if __context__.previous.get('file_dir'):
        log.info('using previous tasks file_dir')
    target_table = __context__.tags['Import data into system'].table
    ...
    # Do something here with file_dir and the arguments from the 
    # 'Import data into system' tag.
```

## Common practices

- Provide a `__virtualname__` global parameter. This will be used by the eruptr
import mechanism.

    eruptr/tasks/pack.py:

```python
__virtualname__ = 'tasks.pack'
```

- Provide a `__virtual__` function if you need to enable/disable a module 
depending on available external tools. This should return a tuple 
(False, Error Message) if the external tool or library doesn't exist or the 
`__virtualname__` if everything checks out.


```python
@functools.lru_cache(maxsize=None)
def __virtual__():
    bins = ['gawk', 'awk', 'sed', 'grep', 'head', 'tail']
    for binary in bins:
        if not eruptr.utils.path.which(binary):
            return(False, f'The {binary} binary could not be found')
    return __virtualname__
```

- Enable general logging:

```python
import logging

log = logging.getLogger()
```

- Cache discovery or other helper functions where it makes sense (not tasks, 
pipes or other modules though!)

```python
import functools

@functools.lru_cache(maxsize=None)
def myfunction....
```

- Use lower-case for exported functions.
- Ensure all non-public functions don't start with an underscore. Any functions
that start with an underscore will not be imported into the dunder dictionaries.
- All functions should accept `run`, `env` and `kwargs` at a minimum. All arguments
should specify a default value (`None` if not required/specified).
- Return data using `eruptr.utils.default_returner` or equivalent format. This
provides the returncode from the operation, any raw data and any `value` data.
Data in `value` format is used by evaluators.
- Choose an appropriate subject for the `run` parameter although it's ok to leave
this as None if this is not sensible. (see the `pipes.text.replace` command).

## Engine modules

- Use existing libraries/modules to accelerate development.
- Provide at a minimum an `execute` function and a `select` function.
- Use the `default_returner` for all operations where sensible.
- Use bulk mechanisms to import/export data. Most libraries that require
loading data into a Python or Java structure spend 95% of their time dealing 
with overhead from the language. Most of the time a carefully crafted unix pipe
directly to a DBMS client tool is several times faster than Spark or Python.
- Use RFC1738 format for database connection strings - `scheme://user:password@hostname:port/database`.

## I/O and Pipes modules

- All I/O modules must return a `UnixPipeProcess` object.
- I/O reader modules must specify the `UnixPipeProcess` argument `stdin` as `None` 
unless they specifically read from `stdin`.
- I/O writer modules must specify the `UnixPipeProcess` argument `stdout` as `None`.
- All `cmd` parameters to the `UnixPipeProces`s object should be a list.
- If you are authoring a complex process that needs to carry out certain actions
on startup or end or has a dynamic cmd list you pass in a more complex object 
to the cmd parameter. The `UnixPipeProcess` object will attempt to call the `__call__`
method on this object.
- Use on_start and on_end hooks to perform complex setup and pull downs. See 
the pipes.python example - https://github.com/VulknData/eruptr/blob/main/eruptr/pipes/python.py.
In this case we create a temporary file before running the pipeline and remove it
afterwards however we need to use a dynamic command as the filename created by
`mkstemp` is random.
- Ensure your I/O or Pipe module *doesn't actually execute*. It has to pass the
command or code through the `UnixPipeProcess` object to execute.

## Task modules

- Unlike I/O and Pipe modules, Task modules should execute and carry out an 
action including any setup and pull down tasks.
- Ensure task modules can be re-used in sensible ways as the foundation to 
a general execution library.