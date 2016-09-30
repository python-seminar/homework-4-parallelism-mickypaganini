from darts import pidarts
import numpy as np

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
    from dask.distributed import Executor, progress
    e = Executor(set_as_default=True)
    futures = [e.submit(pidarts, num) for num in np.logspace(1, 7, 14)]
    d = {}
    _ = [d.update(f.result()) for f in futures]
    return d

def concurrent_darts():
    from concurrent.futures import ProcessPoolExecutor
    e = ProcessPoolExecutor()
    results = list(e.map(pidarts, np.logspace(1, 7, 14)))
    d = {}
    _ = [d.update(r) for r in results]
    return d

def simple_darts():
    d = {}
    _ = [d.update(pidarts(number_of_darts)) for number_of_darts in np.logspace(1, 7, 14)]
    return d

# -----------------------------------------------

def plot(d, orig_methods, orig_trials):
    methods = d.keys()
    trials = len(d[methods[0]].keys())
    assert sorted(methods) == sorted(orig_methods)
    assert trials == orig_trials
    import matplotlib.pyplot as plt
    x = d[methods[0]].values()[0].keys()
    color = iter(['red', 'blue', 'green'])#(plt.cm.jet(np.linspace(0, 1, len(methods))))
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
        if method not in ['dask', 'concurrent', 'simple']:
            raise ValueError("Invalid method: {}. \
                Available options: 'dask', 'concurrent', 'simple'".format(method))

# -----------------------------------------------    

if __name__ == '__main__':
    import sys
    import argparse
    # -- read in arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--methods',
        help="Select any among 'dask', 'concurrent', 'simple'",
        nargs="+", 
        default=['dask', 'concurrent', 'simple'])
    parser.add_argument('--repeat',
        type=int,
        help="int, number of times you want to repeat the simulation",
        default=1)
    args = parser.parse_args()
    check_args(args.methods)
    sys.exit(main(args.methods, args.repeat))

