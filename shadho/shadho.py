"""Main driver for the SHADHO framework.

Classes
-------
Shadho
    Driver class for local and distributed hyperparameter optimization.
"""
from .config import ShadhoConfig
from .hardware import ComputeClass
from .managers import create_manager

from collections import OrderedDict
import json
import os
import tarfile
import tempfile
import time

import numpy as np
import pyrameter
import scipy.stats


def shadho():
    pass


class Shadho(object):
    """Optimize hyperparameters using specified hardware.

    Parameters
    ----------
    cmd : str or function
        The command to run on remote workers or function to run locally.
    spec : dict
        The specification defining search spaces.
    files : list of str or WQFile
        The files to send to remote workers for task execution.
    use_complexity : bool, optional
        If True, use the complexity heuristic to adjust search proportions.
    use_priority : bool, optional
        If True, use the priority heuristic to adjust search proportions.
    timeout : int, optional
        Number of seconds to search for.
    max_tasks : int, optional
        Number of tasks to queue at a time.
    max_resubmissions: int, optional
        Maximum number of times to resubmit a particular parameterization for
        processing if task failure occurs. Default is not to resubmit.

    Attributes
    ----------
    config : `shadho.config.ShadhoConfig`
        Global configurations for shadho.
    backend : `pyrameter.ModelGroup`
        The data view/storage backend. This backend keeps track of all
    manager : `shadho.managers.workqueue.WQManager`
        The distributed task manager to use.
    ccs : list of `shadho.hardware.ComputeClass`
        The types of hardware to expect during optimization. If not supplied,
        tasks are run on the first available worker.
    timeout : int
        Number of seconds to search for.
    max_tasks : int
        Maximum number of tasks to enqueue at a time.
    max_resubmissions: int
        Maximum number of times to resubmit a particular parameterization for
        processing if task failure occurs. Default is not to resubmit.

    Notes
    -----
    To enable configuration, ``backend`` and ``manager`` are created when
    `Shadho.run` is called.

    """

    def __init__(self, cmd, spec, files=None, use_complexity=True,
                 use_priority=True, timeout=600, max_tasks=100,
                 await_pending=False, max_resubmissions=0):
        self.config = ShadhoConfig()
        self.cmd = cmd
        self.spec = spec
        self.use_complexity = use_complexity
        self.use_priority = use_priority
        self.timeout = timeout if timeout is not None and timeout >= 0 \
                       else float('inf')
        self.max_tasks = 2 * max_tasks
        self.max_resubmissions = max_resubmissions
        self.await_pending = await_pending

        self.ccs = OrderedDict()

        self.files = []
        if files is not None:
            for f in files:
                if not isinstance(f, WQFile):
                    self.add_input_file(f)
                else:
                    self.files.append(f)
        self.assignments = {}

        self.__tmpdir = tempfile.mkdtemp(prefix='shadho_', suffix='_output')

        self.add_input_file(os.path.join(
            self.config.shadho_dir,
            self.config.wrapper))

        self.config.save_config(self.__tmpdir)
        self.add_input_file(os.path.join(self.__tmpdir, '.shadhorc'))

    def __del__(self):
        if hasattr(self, '__tmpdir') and self.__tmpdir is not None:
            os.rmdir(self.__tmpdir)

    def add_input_file(self, localpath, remotepath=None, cache=True):
        """Add an input file to the global file list.

        Parameters
        ----------
        localpath : str
            Path to the file on the local filesystem.
        remotepath : str, optional
            Path to write the file to on the remote worker. If omitted, the
            basename of ``localpath`` (e.g. "foo/bar.baz" => "bar.baz").
        cache : bool, optional
            Whether to cache the file on the remote worker. If True (default),
            will be cached on the worker between tasks, reducing network
            transfer overhead. If False, will be re-transferred to the worker
            on each task.
        """
        self.files.append((localpath, remotepath, 'input', cache))

    def add_output_file(self, localpath, remotepath=None, cache=False):
        """Add an input file to the global file list.

        Output files are expected to be discovered on the remote worker after a
        task has completed. They are returned to the `shadho.Shadho` instance
        and will be stored for further review without additional processing.

        Parameters
        ----------
        localpath : str
            Path to the file on the local filesystem.
        remotepath : str, optional
            Path to write the file to on the remote worker. If omitted, the
            basename of ``localpath`` (e.g. "foo/bar.baz" => "bar.baz").
        cache : bool, optional
            Whether to cache the file on the remote worker. It is recommended
            that this be set to False for output files.

        Notes
        -----
        `shadho.Shadho` automatically parses the output file specified in
        ``.shadhorc``, so and output file added through this method will not be
        processed, but rather stored for later review.
        """
        self.files.append((localpath, remotepath, 'output', cache))

    def add_compute_class(self, name, resource, value, max_tasks=100):
        """Add a compute class representing a set of consistent recources.

        Parameters
        ----------
        name : str
            The name of this set of compute resources.
        resource : str
            The resource to match, e.g. gpu_name, cores, etc.
        value
            The value of the resource that should be matched, e.g. "TITAN X
            (Pascal)", 8, etc.
        max_tasks : int, optional
            The maximum number of tasks to queue for this compute class,
            default 100.
        """
        cc = ComputeClass(name, resource, value, 2 * max_tasks)
        self.ccs[cc.id] = cc

    def run(self):
        """Search hyperparameter values on remote workers.

        Generate and evaluate hyperparameters using the selected task manager
        and search strategy. Hyperparameters will be evaluated until timeout,
        and the optimal set will be printed to screen.

        Notes
        -----
        If `self.await_pending` is True, Shadho will continue to evaluate
        hyperparameters in the queue without generating new hyperparameter
        values. This will continue until the queue is empty and all tasks have
        returned.
        """
        if not hasattr(self, 'manager'):
            self.manager = create_manager(
                manager_type=self.config.manager,
                config=self.config,
                tmpdir=self.__tmpdir)

        if not hasattr(self, 'backend'):
            self.backend = pyrameter.build(self.spec)

        if len(self.ccs) == 0:
            cc = ComputeClass('all', None, None, self.max_tasks)
            self.ccs[cc.id] = cc

        self.assign_to_ccs()

        start = time.time()
        elapsed = 0
        try:
            while elapsed < self.timeout and (elapsed == 0 or not self.manager.empty()):
                stop = self.generate()
                if not stop:
                    result = self.manager.run_task()
                    if result is not None:
                        if len(result) == 3:
                            self.success(*result)
                        else:
                            self.failure(*result)
                    if self.backend.result_count % 50 == 0:
                        self.backend.save()
                    elapsed = time.time() - start
                else:
                    break

            if self.await_pending:
                while not self.manager.empty():
                    result = self.manager.run_task()
                    if result is not None:
                        if len(result) == 4:
                            self.success(*result)
                        else:
                            self.failure(*result)

        except KeyboardInterrupt:
            if hasattr(self, '__tmpdir') and self.__tmpdir is not None:
                os.rmdir(self.__tmpdir)

        self.backend.save()
        opt = self.backend.optimal(mode='best')
        key = list(opt.keys())[0]
        print("Optimal result: {}".format(opt[key]['loss']))
        print("With parameters: {}".format(opt[key]['values']))
        print("And additional results: {}".format(opt[key]['results']))

    def generate(self):
        """Generate hyperparameter values to test.

        Hyperparameter values are generated from the search space specification
        supplied at instantiation using the requested generation method (i.e.,
        random search, TPE, Gaussian process Bayesian optimization, etc.).

        Returns
        -------
        params : list of tuple
            A list of triples (result_id, compute_class_id, parameter_values).
        """
        stop = True
        for ccid in self.ccs:
            cc = self.ccs[ccid]
            n = cc.max_tasks - cc.current_tasks
            for i in range(n):
                mid, rid, param = cc.generate()

                if param is not None:
                    tag = '.'.join([rid, mid, ccid])
                    self.manager.add_task(
                        self.cmd,
                        tag,
                        param,
                        files=self.files,
                        resource=cc.resource,
                        value=cc.value)
                    stop = False
            cc.current_tasks = cc.max_tasks

    def make_tasks(self, params):
        """Create tasks to test hyperparameter values.

        Parameters
        ----------
        params : list of dict
            The hyperparameter values ot test.

        Returns
        -------
        tasks : list of `work_queue.Task`
            Tasks to submit to the distributed manager.
        """
        tasks = []
        for p in params:
            tag = '.'.join([p[0], p[1]])
            buff = WQBuffer(str(json.dumps(p[2])),
                            self.config._global.param_file,
                            cache=False)
            outfile = WQFile(os.path.join(
                                self.__tmpdir,
                                '.'.join([tag,
                                          self.config._global.output])),
                             remotepath=self.config._global.output,
                             ftype='output',
                             cache=False)
            files = [f for f in self.files]
            files.append(outfile)
            files.append(buff)
            task = self.manager.make_task(self.cmd, tag, files)
            tasks.append(task)
        return tasks

    def assign_to_ccs(self):
        """Assign trees to compute classes.

        Each independent model in the search (model being one of a disjoint set
        of search domains) is assigned to at least two compute classes based on
        its rank relative to other models. In this way, only a subset of models
        are evaluated on each set of hardware.

        Notes
        -----
        This method accounts for differing counts of models and compute
        classes, adjusting for a greater number of models, a greater number of
        compute classes, or equal counts of models and compute classes.

        See Also
        --------
        `shadho.ComputeClass`
        `pyrameter.ModelGroup`
        """
        if len(self.ccs) == 1:
            key = list(self.ccs.keys())[0]
            self.ccs[key].model_group = self.backend
        else:
            model_ids = [mid for mid in self.backend.model_ids]
            self.backend.sort_models()
            if model_ids != self.backend.model_ids or len(self.ccs) == 0:
                model_ids = self.backend.model_ids
                for cc in self.ccs:
                    cc.clear()

                ccids = list(self.ccs.keys())
                larger = model_ids if len(self.trees) >= len(ccids) else ccids
                smaller = model_ids if len(self.trees) < len(ccids) else ccids

                x = float(len(larger)) / float(len(smaller))
                y = x - 1
                j = 0
                n = len(larger) / 2

                for i in range(len(larger)):
                    if i > np.ceil(y):
                        j += 1
                        y += x

                    if smaller[j] in self.assignments:
                        self.ccs[smaller[j]].add_model(larger[i])
                        if i <= n:
                            self.ccs[smaller[j + 1]].add_model(larger[i])
                        else:
                            self.ccs[smaller[j - 1]].add_model(larger[i])
                    else:
                        self.ccs[larger[i]].add_model(smaller[j])
                        if i <= n:
                            self.ccs[larger[i]].add_model(smaller[j + 1])
                        else:
                            self.ccs[larger[i]].add_model(smaller[j - 1])

    def success(self, tag, loss, results):
        """Handle successful task completion.

        Parameters
        ----------
        tag : str
            The task tag, encoding the result id, model id, and compute class
            id as ``<result_id>.<model_id>.<cc_id>``.
        loss : float
            The loss value associated with this result.
        results : dict
            Additional metrics to be included with this result.

        Notes
        -----
        This method will trigger a model/compute class reassignment in the
        event that storing the result caused the model's priority to be
        updated.
        """
        result_id, model_id, ccid = tag.split('.')
        self.ccs[ccid].register_result(model_id, result_id, loss, results)

        if self.backend.result_count % 10 == 0:
            self.assign_to_ccs()
        self.ccs[ccid].current_tasks -= 1

    def failure(self, tag, resub):
        """Handle task failure.

        Parameters
        ----------
        task : `work_queue.Task`
            The failed task to process.

        Notes
        -----

        """
        result_id, model_id, ccid = tag.split('.')
        submissions, params = \
            self.backend.register_result(model_id, result_id, None, {})
        if resub and submissions < self.max_resubmissions:
            cc = self.ccs[ccid]
            self.manager.add_task(self.cmd,
                                  tag,
                                  params,
                                  files=self.files,
                                  resource=cc.resource,
                                  value=cc.value)
        else:
            self.ccs[ccid].current_tasks -= 1
