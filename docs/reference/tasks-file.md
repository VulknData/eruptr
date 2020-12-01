# tasks.file

## tasks.file.copy

Copy a file on the local or network mounted filesystem.

* Parameters:
    * `run: str=None` - ignored
    * `tag: str=None` - optional user tag for the operation
    * `src: str=None` - Source path
    * `dst: str=None` - Destination path
* Python

```python
__tasks__['file.copy'](
    src='/data/spool/myfile.csv', 
    dst='/data/archive/myfile.csv'
)
```

* YAML

```yaml
transform:
    - tasks.file.copy:
        src: /data/spool/myfile.csv
        dst: /data/archive/myfile.csv
```

## tasks.file.delete

Delete the named file.

* Parameters:
    * `run: str=None` - File to delete
    * `tag: str=None` - optional user tag for the operation
* Python

```python
__tasks__['file.delete']('/data/spool/myfile.csv')
```

* YAML

```yaml
transform:
    - tasks.file.delete: /data/spool/myfile.csv
```

## tasks.file.move

Move a file on the local or network mounted filesystem.

* Parameters:
    * `run: str=None` - ignored
    * `tag: str=None` - optional user tag for the operation
    * `src: str=None` - Source path
    * `dst: str=None` - Destination pathon
* Python

```python
__tasks__['file.move'](
    src='/data/spool/myfile.csv',
    dst='/data/archive/myfile.csv'
)
```

* YAML

```yaml
transform:
    - tasks.file.move:
        src: /data/spool/myfile.csv
        dst: /data/archive/myfile.csv
```

## tasks.file.write

Write data to the filesystem. Note this is not intended to write large chunks
of data. Please use the tasks.clickhouse.export functions to write large datasets
to disk.

* Parameters:
    * `run: str=None` - ignored
    * `tag: str=None` - optional user tag for the operation
    * `path: str=None` - the filename to write to
    * `data: str=None` - the contents of the file
* Python

```python
csv_data = """
"device1","1970-04-27 03:46:40",32.3,"temperature"
"device1","1970-04-27 03:46:40",10.2,"watts"
"""
__tasks__['file.write'](path='/data/spool/myfile.csv', data=csv_data.strip())
```

* YAML

```yaml
transform:
    - tasks.file.write:
        path: /data/spool/myfile.csv
        data: |
            "device1","1970-04-27 03:46:40",32.3,"temperature"
            "device1","1970-04-27 03:46:40",10.2,"watts"
```