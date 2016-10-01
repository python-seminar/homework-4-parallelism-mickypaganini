To run this project, type:
```
python experiment.py --methods dask concurrent simple --repeat 10
```
where the `--methods` flag takes the names of the methods to use to parallelize this task ('multiprocessing', 'joblib', 'dask', 'concurrent', 'simple' are currently available), and the `--repeat` flag stores the number of times we want to repeat the experiment.

The performance plots look a bit puzzling at the moment.
