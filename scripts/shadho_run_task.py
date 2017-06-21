import json
import os
try:
    import cPickle as pickle
except:
    import pickle


def run_task(task, params='hyperparameters.json', out='results.json'):
    """Run a function with arguments pulled from a JSON source.

    For simple use cases, SHADHO should be able to run without user-defined
    bash scripts, JSON parsing, etc. Users will expect this to be automated in
    the standard case.

    Parameters
    ----------
    task : callable
        The function/callable object to run.
    params : {'hyperparameters.json', str, dict, callable}
        The path to the JSON file defining the Hyperparameter values, a dict
        containing the hyperparameter values, or a JSON string containing to
        be decoded.
    out : {'results.json', str, callable}
        The path to the results file to be written. File type determined by the
        extension. If a function/ callable object, call on the results of task.
    """
    try:
        spec = {}

        if os.path.isfile(params):
            with open(params, 'r') as f:
                spec = json.load(f)
        elif isinstance(params, dict):
            spec = params
        else:
            spec = json.loads(params)
        result = task(spec)

        if callable(out):
            out(result)
        else:
            (_, ext) = os.path.splitext(out)
            with open(out, 'w') as f:
                if ext == '.pkl':
                    pickle.dump(result, f, protocol=2)
                else:
                    json.dump(result, f)

    except IOError as err:
        print(err)
    except json.decoder.JSONDecodeError as err:
        print("Error decoding parameters: {}".format(err))
    except TypeError as err:
        print(err)
