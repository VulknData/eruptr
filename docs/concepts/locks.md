# Locks

Locks provide primitive support for advisory locking a namespace in either 
exclusive or shared mode. By providing a decoupled way to implement locking 
users can grow a data pipeline from one server using simple file based locking 
to 10s of servers using distributed, HA locking within a Redis datastore
with a single configuration change.

Exclusive locks ensure there will be no collisions when running multiple instances
of eruptr. Shared locks can be used in an advisory fashion to prevent global 
processes from executing in a given lockspace.

For example - an import task (task 1) may need to stream in several thousand files per 
hour. Each file may be keyed by a given device id and exclusive locks need to be
taken on the device id to prevent clashes. If an overall materialized table needs
to be generated periodically (task 2) and must have exclusive access to the data 
set task 1 should also have a shared lock on task 2. This prevents task 2 from 
obtaining an exclusive lock until there is a gap in processing.