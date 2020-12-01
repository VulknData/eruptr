# tasks.python

## tasks.python.run

Dynamically imports and executes the run parameter as a block of Python. Note
you can also provide your own task modules in Python - in most cases this is 
the preferred method however tasks.python.run may be useful for small blocks of
code or importing external modules.

Note that unlike pipe modules, task modules must return a success code, 0 or 
non-zero on failure. Use of sys.exit here will abort the entire eruptr process.

* Parameters:
    * `run: str` - the packing method to use when compressing.
    * `tag: str=None` - optional user-defined tag for the resource.

* YAML (my thanks to https://www.alt17.com/en/how-to-train-a-machine-learning-model-in-python-and-save-it-for-later-use/
for the Python example)

```yaml
transform:
    - tasks.clickhouse.export:
        ...
    - tasks.python.run:
        tag: train-model
        run: |
            import pandas as pd
            from sklearn import linear_model
            training_dataset = pd.read_csv("clickhouse-export.csv")
            regression_model = linear_model.LinearRegression()
            print ("Training model...")
            regression_model.fit(
                training_dataset[['area']],
                training_dataset.price
            ) 
            print ("Model trained.")
            input_area = int(input("Enter area: "))
            proped_price = regression_model.predict([[input_area]])
            proped_price.save_model('clickhouse-trained-model.csv')

            return 0
    ...
```

In the example above the block of code will be converted to a function:

```python
def tasks_python_run_b5bb9d8014a0f9b1d61e21e796d78dccdf1352f23cd32812f485....(
    **kwargs
):
    import pandas as pd
    from sklearn import linear_model
    training_dataset = pd.read_csv("clickhouse-export.csv")
    regression_model = linear_model.LinearRegression()
    print ("Training model...")
    regression_model.fit(
        training_dataset[['area']],
        training_dataset.price
    ) 
    print ("Model trained.")
    input_area = int(input("Enter area: "))
    proped_price = regression_model.predict([[input_area]])
    proped_price.save_model('clickhouse-trained-model.csv')

    return 0
```
