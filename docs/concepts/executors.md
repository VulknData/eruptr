# Executors

Eruptr supports different execution methods for data processing. An executor
can provide step-wise, micro-batch, stream or any combination of these.

You can mix different executors in a single run as part of a composable workflow.

For instance - in the workflow section of your YAML definition you might specify
the following flows with their associated executors:

```yaml
workflow
  - input:
      executor: UnixPipeExecutor
  - transform:
      executor: StepExecutor
```

This tells eruptr to switch executors when running the named flow.

As of the initial release only the UnixPipeExecutor and StepExecutor are 
available however we will be adding a StreamExecutor for event based streaming
in the future. Users can also create their own and couple the execution with the 
relevant command function.