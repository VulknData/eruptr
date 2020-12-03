# VulknData Eruptr

## Data needs a Makefile

Eruptr is an extensible, model and configuration driven data management system targeting ETL, DataOps and Analytics Engineering. It has been purposefully designed with a focus on the [ClickHouse](https://clickhouse.tech) OLAP engine however it is being adapted and extended to address other data eco-systems.

## Don't ETL or ELT. LET your data be free.

Extract-Transform-Load (ETL) is typically used by most BigData systems including [Hadoop](https://hadoop.apache.org/), [Spark](https://spark.apache.org/) and [Flink](https://flink.apache.org/). In this case the target system expects data in a specific format and it may be beneficial to decouple the transformation / compute from the target system. This has advantages in cases where a transformation is significantly large or there are multiple disparate data sources specified in the Extract phase.

Extract-Load-Transform (ELT) have become popular with the rise of cloud-native data warehouses which can source data from disparate systems without external tooling. In this case a table engine / type, database or object store can be specified as part of the query and standard relational SQL can be used to transform the data as required. Typically an SQL orchestration or data processing tool is employed to manage these different stages.

Real-time streaming also has it's place in terms of on-stream event processing and analytics however data generally finds its way into a persistent store for further OLAP reporting and analytics. There are a plethora of per-event real-time streaming options.

The examples described above often require careful co-ordination of disjoint services and data sources. An accepted practice is to pull together large / complex Java, Scala or Python eco-systems and libraries to extract and reformat data in a strongly typed format before landing it into an object store / data lake or cloud-native data warehouse. Eruptr throws back to a simpler time, building on the knowledge that untyped text processing using awk, sed and other decades old tools vastly outperform most modern BigData eco-systems 95% of the time with identical data accuracy. The performance of such tooling also has a positive benefit to the environment - something we love @ VulknData.

Eruptr is a hybrid of all the aforementioned patterns - streaming, ELT and ETL merge together to provide a straight forward and simple approach with both streaming and step-wise transformations. We call this LET but in reality all aspects of the above can be employed at different stages.

## Eruptr Features

- Specific support/target for ClickHouse and real-time workloads.
- Declarative YAML driven ELT/ETL/LET pipeline configuration that mixes both batch and streaming transformation capability.
- Template configurations - use stacked template engines, Jinja and Mako, in the one YAML document.
- Multiple execution modes - model administration, data conversion, batch and streaming options.
- Model deployment - describe target tables as part of the workflow and let Eruptr deploy them for you.
- Data conversion - use eruptr to convert between multiple data formats from multiple source / object stores on the fly.
- Extensible modular ecosystem. Users can author new modules - eruptr will automatically detect and load your modules:
    - `drivers` - Execution targets to deploy your workloads
    - `engines` - Create new data store execution engines
    - `executors` - High level process co-ordinators to mix batch and streaming 
    modules
    - `filters` - Jinja template filters that can be used throughout your 
    workflows
    - `formats` - Convert data sources without having to fire up Spark or employ 
    complex layers of  Java/Scala code
    - `io` - Interact with different data store endpoints and streaming systems
    - `locks` - Employ file, database or distributed key/value store locking for 
    rapid data applications and co-ordinating multiple data stores
    - `macros` - Declare both SQL snippets and functions as Jinja, Mako or 
    simple SQL macros for re-use
    - `pipes` - Simple Unix pipes streaming API - process text using gawk, awk, 
    sed and other shell tools
    - `tasks` - Execute batch-style tasks from shell, scripts, embedded code or 
    SQL
- ClickHouse only features
    - Streaming SQL transformations using the `pipes.clickhouse.local` and `io.clickhouse.write` functions
    - Shard allocation / detection for data files
    - Distributed table management
    - Automatic model generation from raw SQL. No fancy DSL or YAML breakdown of your model required.
    - Automatic schema migrations for simple cases (columns, indexes, settings).