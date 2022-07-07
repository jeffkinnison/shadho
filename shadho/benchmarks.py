import argparse
import functools
import re
import sys

from hpobench.benchmarks.ml.xgboost_benchmark import XGBoostBenchmark
from hpobench.benchmarks.ml.nn_benchmark import NNBenchmark
from hpobench.benchmarks.ml.rf_benchmark import RandomForestBenchmark
from hpobench.benchmarks.ml.lr_benchmark import LRBenchmark
from hpobench.benchmarks.ml.svm_benchmark import SVMBenchmark

import numpy as np
from pyrameter.methods import ncqs, random, tpe, bayes, pso, smac, hom
from shadho import Shadho, spaces

# Easy pyrameter methods lookup from args
METHODS = {
    'bayes': bayes,
    'ncqs': ncqs,
    'hom': hom,
    'pso': pso,
    'random': random,
    'smac': smac,
    'tpe': tpe
}

# Easy nechmarks lookup from args
BENCHMARKS = {
    'XGBoostBenchmark': XGBoostBenchmark, 
    'NNBenchmark': NNBenchmark, 
    'RandomForestBenchmark': RandomForestBenchmark, 
    'LRBenchmark': LRBenchmark, 
    'SVMBenchmark': SVMBenchmark
}

def parse_args(args=None):
    """Parse command line arguments.
    Parameters
    ----------
    args : str, optional
        Command line arguments to process. If not supplied, reads from
        `sys.argv`.
    
    Returns
    -------
    args : argparse.Namespace
        The processed command line arguments.
    """
    p = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    p.add_argument('--task', type=int, 
        help='The task model to optimize.')
    p.add_argument('--seed', type=int, 
        help='random seed for reproducibility')
    p.add_argument('--benchmark', type=str,
        choices=['XGBoostBenchmark', 'NNBenchmark', 'RandomForestBenchmark', 
                 'LRBenchmark', 'SVMBenchmark'],  
        help='The benchmark model to optimize.')
    p.add_argument('--dataset', type=int,
        choices=[10101, 53, 146818, 146821, 9952, 146822, 31, 3917, 168912, 
                 3, 167119, 12, 146212, 168911, 9981, 167120, 14965, 146606,
                 7592, 9977],  # add dataset names to `choices`
        help='Dataset to train/evaluate models.')
    p.add_argument('--exp-key', type=str,
        help='Experiment name for driver/worker coordination.')
    p.add_argument('--method', type=str,
        choices=['random', 'tpe', 'bayes', 'smac', 'pso', 'ncqs', 'hom'],
        help='The hyperparameter optimization method to use in SHADHO.')
    p.add_argument('--inner-method', type=str,
        choices=['random', 'tpe', 'bayes', 'smac', 'pso'],
        help='The inner method to use during bilevel optimization.')
    p.add_argument('--timeout', type=int, default=600,
        help='the amount of time (in seconds) to run the benchmark')
    p.add_argument('--max-tasks', type=int, default=500,
        help='the maximum number of hyperparameter sets to evaluate')
    
    return p.parse_args(args)

def convert_config_to_shadho(config):
    """Convert HPOBench config to a SHADHO search space.
    Parameters
    ----------
    config : dict or `hpobench.Configuration`
        HPOBench model config drawn from `
    Returns
    -------
    space : dict or pyrameter.Specification
        The SHADHO translation of the HPOBench searh space configuration.
    """
    # Create the shadho search space here and return it.
    space = {}
    
    for param in config.get_all_unconditional_hyperparameters():
        param_type = type(config.get_hyperparameter(param)).__name__
        lower = config.get_hyperparameter(param).lower 
        upper = config.get_hyperparameter(param).upper
        log = config.get_hyperparameter(param).log
        print(param, param_type, log)
        
        # TODO: THE BELOW BREAKS FOR DIFFERENT TESTS WHEN USING LOG SPACES 
        if param_type == 'UniformFloatHyperparameter' and log==False:
            space[param] = spaces.uniform(np.float64(lower), np.float64(upper))
        elif param_type == 'UniformIntegerHyperparameter' and log==False:
            space[param] = spaces.randint(int(lower), int(upper))
        elif param_type == 'UniformIntegerHyperparameter' and log==True: 
            space[param] = spaces.randint(int(lower), int(upper))
        elif param_type == 'UniformFloatHyperparameter' and log==True:
            space[param] = spaces.uniform(np.float64(lower), np.float64(upper))
        else:
            raise TypeError(
                f'Unhandled HPOBench hyperparameter type {param_type}.' + \
                'Submit a bug report with the benchmark name and this message.'
            )
    
    return space

def run_benchmark(benchmark, hyperparameters):
    """Train an HPOBench benchmark object with one set of hyperparamters.
    Parameters
    ----------
    benchmark
        The HPOBench benchmark object to train.
    hyperparameters : dict
        The hyperparameter values to give it.
    
    Returns
    -------
    performance : dict
        Any performance metrics provided by the benchmark.
    """
    performance = benchmark.objective_function(hyperparameters)
    
    out = performance['info']
    out['loss'] = out['val_loss']
    del out['config']
    del out['fidelity']

    if out['loss'] is None:
        out['loss'] = np.nan
    
    return out

def driver(benchmark, dataset, exp_key, method, inner_method='random',
           timeout=600, max_tasks=500, seed=None):
    print(type(seed))
    """Run an HPOBench benchmark through a SHADHO optimizer.
    Parameters
    ----------
    benchmark : {}  PUT THE BENCHMARK NAMES HERE
        The name of the HPOBench benchmark to run.
    dataset : {} PUT THE DATASET NAMES HERE
        The name of the HPOBench dataset to use.
    exp_key : str
        Name of the session provided to the driver and workers.
    method : str or `pyrameter.methods.Method`
        The optimization method to use.
    inner_method : str or `pyrameter.methods.Method`, optional
        The inner optimization method to use in a bilevel optimization.
        Ignored if ``method`` is not bilevel or is an instance of
        `pyrameter.methods.BilevelMethod`.
    timeout : int
        The amount of time to run the search in seconds. Default 600.
    max_tasks : int
        The maximum number of hyperparameter sets to evaluate. Default: 500.
    seed : int, optional
        The random seed to apply to SHADHO and HPOBench. If not supplied, uses
        the default RNG protocol for each.
    """
    # Grab the benchmark object here with importlib
    b = BENCHMARKS[benchmark](task_id=dataset, rng=seed)
    obj = functools.partial(run_benchmark, b)

    # Grab the configuration space here
    config = b.get_configuration_space(seed=seed)
    
    # Convert the HPOBench config to a SHADHO search space
    space = convert_config_to_shadho(config)
    
    # Create the SHADHO object
    if isinstance(method, str):
        try:
            if re.search('^ncqs', method) or re.search('^hom', method):
                method = METHODS[method](METHODS[inner_method]())
            else:
                method = METHODS[method]()
        except KeyError:
            raise ValueError(
                f'Invalid optimization method {method} requested. ' + \
                f'Re-run with one of {list(METHODS.keys())}'
            )
    opt = Shadho(
        exp_key, 
        obj, 
        space, 
        method=method,
        timeout=timeout,
        max_tasks=max_tasks
    )
    
    # Run the SHADHO search
    opt.run()
    
if __name__ == '__main__':
    args = parse_args()
    
    driver(
        args.benchmark,
        args.dataset,
        args.exp_key,
        args.method,
        timeout=args.timeout,
        max_tasks=args.max_tasks,
        inner_method=args.inner_method,
        seed=args.seed
    )
