To run this project, type:
```
python conc.py --methods dask concurrent simple --repeat 10
```
where the `--methods` flag takes the names of the methods to use to parallelize this task (only 'dask', 'concurrent', 'simple' are available right now), and the `--repeat` flag stores the number of times we want to repeat the experiment