from lib2to3.pytree import convert
from re import X
from hpobench.benchmarks.ml.xgboost_benchmark import XGBoostBenchmark
from hpobench.benchmarks.ml.nn_benchmark import NNBenchmark
from hpobench.benchmarks.ml.rf_benchmark import RandomForestBenchmark
from hpobench.benchmarks.ml.lr_benchmark import LRBenchmark
from hpobench.benchmarks.ml.svm_benchmark import SVMBenchmark
from shadho import Shadho, spaces
import argparse
import sys
from pyrameter.methods import ncqs, random, tpe, bayes, pso, smac, ncqsh

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
    p.add_argument('--benchmark', type=str, choices=['XGBoostBenchmark', 'NNBenchmark', 'RandomForestBenchmark', 
                                                      'LRBenchmark', 'SVMBenchmark'],  
        help='The benchmark model to optimize.')
    p.add_argument('--dataset', type=int, choices=[10101, 53, 146818, 146821,
                                                   9952, 146822, 31, 3917, 168912, 
                                                   3, 167119, 12, 146212, 168911, 
                                                   9981, 167120, 14965, 146606, 7592, 9977],  # add dataset names to `choices`
        help='Dataset to train/evaluate models.')
    p.add_argument('--exp-key', type=str,
        help='Experiment name for driver/worker coordination.')
    p.add_argument('--method', type=str,
        choices=['random', 'tpe', 'bayes', 'smac', 'pso', 'ncqs'],
        help='The hyperparameter optimization method to use in SHADHO.')
    p.add_argument('--inner-method', type=str,
        choices=['random', 'tpe', 'bayes', 'smac', 'pso'],
        help='The inner method to use during bilevel optimization.')

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
            space[param] = spaces.uniform(float(lower), float(upper))
        elif param_type == 'UniformIntegerHyperparameter' and log==False:
            space[param] = spaces.randint(int(lower), int(upper))
        elif param_type == 'UniformIntegerHyperparameter' and log==True: 
            space[param] = spaces.randint(int(lower), int(upper))
        elif param_type == 'UniformFloatHyperparameter' and log==True:
            space[param] = spaces.uniform(float(lower), float(upper)) 
    return space

def driver(benchmark, dataset, exp_key, method, inner_method=None):
    # TODO: Not sure how to properly pass the args - but example of running is below in main 
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
    """
    # Grab the benchmark object here with importlib
    b = benchmark(task_id=dataset, rng=1)
    # Grab the configuration space here
    config = b.get_configuration_space(seed=1)
    # Convert the HPOBench config to a SHADHO search space
    space = convert_config_to_shadho(config)
    # Create the SHADHO object
    opt = method(inner_method())
    shadho = Shadho(exp_key = exp_key, 
                    cmd=b, 
                    space=space, 
                    method=opt)
    # Run the SHADHO search
    shadho.run()


if __name__ == '__main__':

    p = parse_args()
    print(p.dataset)

    method = ncqsh(smac())
    b = SVMBenchmark(task_id=p.dataset, rng=1)
    config = b.get_configuration_space(seed=1)

    space = convert_config_to_shadho(config)
    # TODO: Max tasks does not actually work 
    opt = Shadho('svm_test', b, space, method=method, max_tasks=200)
    opt.run()

