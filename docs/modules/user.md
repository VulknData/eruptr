# User Modules

Users can provide paths to their own modules by way of a user configuration file.
By default this file is in the current users home directory under ~/.eruptr.yaml 
however you can specify the location using the `--user-config` flag on the CLI.

Within the configuration file you can either specify an umbrella path to a modules
directory or individual paths:

Example with umbrella paths:

```yaml
modules: /home/user/eruptr_modules
```

Within the umbrella path eruptr expects to find the following paths and modules.
It's ok if a particular path does not exist (for instance - you are not providing 
custom executors).

```shell
modules/
    drivers/
    engines/
    executors/
    filters/
    formats/
    io/
    locks/
    macros/
    pipes/
    streams/
    tasks/
```

Note that each subdirectory is treated as a normal Python module directory and
so must contain an `__init__.py` file.

For individual paths the configuration must appear as follows:

```yaml
modules:
  pipes:
    - /usr/lib/mysystem_eruptr_modules/pipes
    - /home/user/eruptr_modules/pipes
  tasks:
    - /home/user/eruptr_modules/tasks
```

For individual paths the paths must be provided as lists. You can specify multiple
paths if required.
