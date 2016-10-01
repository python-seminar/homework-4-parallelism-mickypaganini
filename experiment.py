from darts import pidarts
import numpy as np

N_POINTS = 14

def main(methods, repeat):
    d = {}
    for method in methods:
        d[method] = {}
    for trial in xrange(repeat):
            
        if 'dask' in methods:
            d['dask'].update(
                {trial : dask_darts()}
            )
        if 'concurrent' in methods:
            d['concurrent'].update(
                {trial : concurrent_darts()}
            )
        if 'joblib' in methods:
            d['joblib'].update(
                {trial : joblib_darts()}
            )
        if 'multiprocessing' in methods:
            d['multiprocessing'].update(
                {trial : multiprocessing_darts()}
            )
        if 'simple' in methods:
            d['simple'].update(
                {trial : simple_darts()}
            )

    # import cPickle as pickle
    # d = pickle.load(open('dict_darts.pkl', 'rb'))
    plot(d, methods, repeat)
    import cPickle as pickle
    pickle.dump(d, open('dict_darts.pkl', 'wb'))

# -----------------------------------------------

def dask_darts():
   import dask.array as da
   x = da.from_array(np.logspace(1, 7, N_POINTS), (1, ))
   lazy_pidarts = x.map_blocks(pidarts)
   d = {}
   _ = [d.update(r) for r in lazy_pidarts.compute()]
   return d

def concurrent_darts():
    from concurrent.futures import ProcessPoolExecutor
    e = ProcessPoolExecutor()
    results = list(e.map(pidarts, np.logspace(1, 7, N_POINTS)))
    d = {}
    _ = [d.update(r) for r in results]
    e.shutdown()
    return d

def joblib_darts():
    from joblib import Parallel, delayed
    results = Parallel(n_jobs=10, verbose=5, backend="threading") \
        (delayed(pidarts)(i) for i in np.logspace(1, 7, N_POINTS))
    d = {}
    _ = [d.update(r) for r in results]
    return d

def multiprocessing_darts():
    from multiprocessing import Pool 
    pool = Pool(processes=4) 
    results = list(pool.map(pidarts, np.logspace(1, 7, N_POINTS)))
    pool.close()
    d = {}
    _ = [d.update(r) for r in results]
    return d

def simple_darts():
    d = {}
    _ = [d.update(pidarts(number_of_darts)) for number_of_darts in np.logspace(1, 7, N_POINTS)]
    return d

# -----------------------------------------------

def plot(d, orig_methods, orig_trials):
    methods = d.keys()
    trials = len(d[methods[0]].keys())
    assert sorted(methods) == sorted(orig_methods)
    assert trials == orig_trials
    import matplotlib.pyplot as plt
    x = d[methods[0]].values()[0].keys()
    color = iter(['red', 'blue', 'green', 'magenta', 'orange'])#(plt.cm.jet(np.linspace(0, 1, len(methods))))
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Darts Thrown')
    ax1.set_ylabel('Execution Time (seconds), solid line')
    ax2 = ax1.twinx()
    ax2.set_ylabel('Simulation Rate (darts/seconds), dashed line')

    for method in methods:
        c = next(color)
        mean_rates = [np.mean([_[darts]['rate'] 
            for _ in d[method].values()]) 
            for darts in d[method].values()[0].keys()]
        std_rates = [np.std([_[darts]['rate'] 
            for _ in d[method].values()]) 
            for darts in d[method].values()[0].keys()]
        mean_times = [np.mean([_[darts]['time'] 
            for _ in d[method].values()]) 
            for darts in d[method].values()[0].keys()]
        std_times = [np.std([_[darts]['time'] 
            for _ in d[method].values()]) 
            for darts in d[method].values()[0].keys()]
        ix = np.argsort(x)
        ax1.errorbar(
            sorted(x),
            np.array(mean_times)[ix],
            yerr=np.array(std_times)[ix],
            label=method,
            color=c)
        ax2.errorbar(
            sorted(x),
            np.array(mean_rates)[ix],
            yerr=np.array(std_rates)[ix],
            linestyle='dashed',
            color=c)

    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax2.set_yscale('log')

    ax1.legend(loc='lower right', fancybox=True, framealpha=0.5)
    plt.show()

# -----------------------------------------------

def check_args(methods):
    """
    Check if methods are valid
    """
    for method in methods:
        if method not in ['dask', 'concurrent', 'simple', 'multiprocessing', 'joblib']:
            raise ValueError("Invalid method: {}. \
                Available options: 'dask', 'concurrent', 'simple', 'multiprocessing', 'joblib'".format(method))

# -----------------------------------------------    

if __name__ == '__main__':
    import sys
    import argparse
    # -- read in arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--methods',
        help="Select any among 'dask', 'concurrent', 'simple', 'multiprocessing', 'joblib'",
        nargs="+", 
        default=['simple'])
    parser.add_argument('--repeat',
        type=int,
        help="int, number of times you want to repeat the simulation",
        default=1)
    args = parser.parse_args()
    check_args(args.methods)
    sys.exit(main(args.methods, args.repeat))

