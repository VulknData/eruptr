# Drivers

Drivers are scheduling targets for Eruptr executors to run their pipelines on.

As of the initial release we only support a single driver (LocalSystem) which 
is used implicitly. There is currently no scaffolding for new drivers however 
this will be developed in the coming months. We expect the first new driver to 
be Celery with more to follow.