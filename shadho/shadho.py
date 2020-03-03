"""Main driver for the SHADHO framework.

Classes
-------
Shadho
    Driver class for local and distributed hyperparameter optimization.
"""
from .configuration import ShadhoConfig
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

from pyrameter.optimizer import FMin


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
    max_queued_tasks : int, optional
        Number of tasks to queue at a time.
    await_pending : bool, optional
        If True, wait for all running tasks to complete after `timeout`.
        Default: False
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
    use_complexity : bool
        If True, use the complexity heuristic to adjust search proportions.
    use_priority : bool
        If True, use the priority heuristic to adjust search proportions.
    timeout : int
        Number of seconds to search for.
    max_queued_tasks : int
        Maximum number of tasks to enqueue at a time.
    await_pending : bool
        If True, wait for all running tasks to complete after `timeout`.
    max_evals : int
        The maximum number of evaluations for a grid point in grid search. Only
        used when the hyperparameter search has no infinite (continuous)
        domains. If ``None``, search until ``timeout``; otherwise, stop early
        once every grid point has been evaluated ``max_evals`` times.
    max_resubmissions: int
        Maximum number of times to resubmit a particular parameterization for
        processing if task failure occurs. Default is not to resubmit.

    Notes
    -----
    To enable configuration after intialization, ``backend`` and ``manager``
    are created when `Shadho.run` is called.

    """

    def __init__(self, exp_key, cmd, spec, method='random', backend='results.json',
                 files=None, use_complexity=True, use_uncertainty=True,
                 timeout=600, max_queued_tasks=100, await_pending=False,
                 max_evals=None, max_resubmissions=0, save_frequency=10,
                 hyperparameters_per_task=1):
        self.exp_key = exp_key
        self.config = ShadhoConfig()
        self.cmd = cmd
        if not isinstance(cmd, str):
            self.config.manager = 'local'
        else:
            self.config.workqueue.name = exp_key
        self.spec = spec
        self.method = method
        self.use_complexity = use_complexity
        self.use_uncertainty = use_uncertainty
        self.timeout = timeout if timeout is not None and timeout >= 0 \
                       else float('inf')
        self.max_queued_tasks = max_queued_tasks
        self.max_resubmissions = max_resubmissions
        self.max_evals = max_evals
        self.await_pending = await_pending
        self.save_frequency = save_frequency
        self.hyperparameters_per_task = hyperparameters_per_task \
            if isinstance(hyperparameters_per_task, int) \
            and hyperparameters_per_task > 0 \
            else 1

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

        self.add_input_file(
            os.path.join(os.path.dirname(__file__), 'worker.py'),
            remotepath=self.config.wrapper)

        self.add_input_file(
            os.path.join(os.path.dirname(__file__), 'utils.py'),
            remotepath=self.config.utils)

        self.config.save_config(self.__tmpdir)
        self.add_input_file(os.path.join(self.__tmpdir, '.shadhorc'))
        self.backend = backend

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

    def add_compute_class(self, name, resource, value, max_queued_tasks=100):
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
        max_queued_tasks : int, optional
            The maximum number of tasks to queue for this compute class,
            default 100.
        """
        cc = ComputeClass(name, resource, value, 2 * max_queued_tasks, None)
        cc.optimizer.method = self.method
        self.ccs[cc.id] = cc

    def load(self):
        if not hasattr(self, 'backend') or not isinstance(self.backend, FMin):
            self.backend = FMin(self.exp_key, self.spec, self.method,
                                self.backend, max_evals=self.max_evals)
        self.backend.load()

    def plot_objective(self, show=True, save=False, filename=None):
        try:
            self.backend.plot_objective()
        except AttributeError:
            print('Could not find trials! Have you run a search or loaded results?')

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
        # Set up the task manager as defined in `shadho.managers`
        if not hasattr(self, 'manager'):
            self.manager = create_manager(
                manager_type=self.config.manager,
                config=self.config,
                tmpdir=self.__tmpdir)

        # Set up the backend hyperparameter generation and database
        if not isinstance(self.backend, FMin):
            self.backend = FMin(self.exp_key, self.spec, self.method,
                                self.backend, max_evals=self.max_evals)

        # If no ComputeClass was created, create a dummy class.
        if len(self.ccs) == 0:
            cc = ComputeClass('all', None, None, self.max_queued_tasks,
                              self.backend)
            self.ccs[cc.id] = cc
        else:
            for cc in self.ccs.values():
                cc.optimizer = self.backend.copy()

        # Set up intial model/compute class assignments.
        self.assign_to_ccs()

        start = time.time()
        elapsed = 0
        exhausted = False
        try:
            # Run the search until timeout or until all tasks complete
            while elapsed < self.timeout and not exhausted and (elapsed == 0 or not self.manager.empty()):
                # Generate hyperparameters and a flag to continue or stop
                stop = self.generate()
                if not stop:
                    # Run another task and await results
                    result = self.manager.run_task()
                    if result is not None:
                        # If a task returned post-process as a success or fail
                        if len(result) == 3:
                            self.success(*result)  # Store and move on
                        else:
                            self.failure(*result)  # Resubmit if asked
                    # Checkpoint the results to file or DB at some frequency
                    if self.backend.trial_count % self.save_frequency == 0:
                        self.backend.save()
                    # Update the time for timeout check
                    elapsed = time.time() - start
                    exhausted = all([ss.done for ss in self.backend.searchspaces])
                else:
                    break

            self.backend.save()

            # If requested, continue the loop until all tasks return
            if self.await_pending:
                while not self.manager.empty():
                    result = self.manager.run_task()
                    if result is not None:
                        if len(result) == 3:
                            self.success(*result)
                        else:
                            self.failure(*result)
                self.backend.save()

        # On keyboard interrupt, save any results and clean up
        except KeyboardInterrupt:
            if hasattr(self, '__tmpdir') and self.__tmpdir is not None:
                os.rmdir(self.__tmpdir)

        # Save the results and print the optimal set of parameters to  screen
        self.backend.save()
        self.backend.summary()
        return self.backend.to_dataframes()

    def generate(self):
        """Generate hyperparameter values to test.

        Hyperparameter values are generated from the search space specification
        supplied at instantiation using the requested generation method (i.e.,
        random search, TPE, Gaussian process Bayesian optimization, etc.).

        Returns
        -------
        stop : bool
            If True, no values were generated and the search should stop. This
            facilitates grid-search-like behavior, for example stopping on
            completion of an exhaustive search.

        Notes
        -----
        This method will automatically add a new task to the queue after
        generating hyperparameter values.
        """
        stop = True

        # Generate hyperparameters for every compute class with space in queue
        for cc_id in self.ccs:
            cc = self.ccs[cc_id]
            n = cc.max_queued_tasks - cc.current_tasks

            # Generate enough hyperparameters to fill the queue
            for i in range(n):
                # Get bookkeeping ids and hyperparameter values
                if self.hyperparameters_per_task == 1:
                    trial = cc.generate()
                    if trial is not None:
                        # Encode info to map to db in the task tag
                        tag = '.'.join([str(trial.id),
                                        str(trial.searchspace.id),
                                        cc_id])
                        self.manager.add_task(
                            self.cmd,
                            tag,
                            trial.parameter_dict,
                            files=self.files,
                            resource=cc.resource,
                            value=cc.value)

                elif self.hyperparameters_per_task > 1:
                    trial = [cc.generate() for _ in range(self.hyperparameters_per_task)]

                    if not any([t is None for t in trial]):
                        # Encode info to map to db in the task tag
                        tag = '.'.join(['@'.join([str(t.id) for t in trial]),
                                        str(trial[0].searchspace().id),
                                        cc_id])
                        parameters = [t.parameter_dict for t in trial]
                        self.manager.add_task(
                            self.cmd,
                            tag,
                            parameters,
                            files=self.files,
                            resource=cc.resource,
                            value=cc.value)


                # Create a new distributed task if values were generated
                stop = False  # Ensure that the search continues
            cc.current_tasks = cc.max_queued_tasks  # Update to show full queue

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
        # If only one CC exists, do nothing; otherwise, update assignments
        if len(self.ccs) == 1:
            key = list(self.ccs.keys())[0]
            self.ccs[key].optimizer = self.backend
        else:
            # Sort models in the search by complexity, priority, or both and
            # get the updated order.
            self.backend.sort_spaces(use_complexity=self.use_complexity,
                                     use_uncertainty=self.use_uncertainty)

            # Clear the current assignments
            for cc in self.ccs:
                cc.clear()

            # Determine if the number of compute classes or the number of
            # model ids is larger
            ccids = list(self.ccs.keys())
            larger = self.backend.searchspaces \
                     if len(self.backend.searchspaces) >= len(ccids) \
                     else ccids
            smaller = ccids if larger == model_ids \
                      else self.backend.searchspaces

            # Assign models to CCs such that each model is assigned to at
            # least two CCs.

            # Steps between `smaller` index increment
            x = float(len(larger)) / float(len(smaller))
            y = x - 1  # Current step index (offset by 1 for 0-indexing)
            j = 0  # Current index of `smaller`
            m = len(smaller) / 2  # Halfway point for second assignment
            n = len(larger) / 2  # Halfway point for second assignment

            for i in range(len(larger)):
                # If at a step point for `smaller` increment the index
                if i > np.ceil(y):
                    j += 1
                    y += x

                # Add the model to the current CC. If i <= n, add the model to
                # the next CC as well; if i > n, add to the previous CC.
                if smaller[j] in self.ccs:
                    self.ccs[smaller[j]].add_searchspace(larger[i])
                    if j < m:
                        self.ccs[smaller[j + 1]].add_model(
                            self.backend[larger[i]])
                    else:
                        self.ccs[smaller[j - 1]].add_model(
                            self.backend[larger[i]])
                else:
                    self.ccs[larger[i]].add_model(smaller[j])
                    if i < n:
                        self.ccs[larger[i + 1]].add_model(
                            self.backend[smaller[j]])
                    else:
                        self.ccs[larger[i - 1]].add_model(
                            self.backend[smaller[j]])

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
        # Get bookkeeping information from the task tag
        trial_id, ss_id, ccid = tag.split('.')

        if not isinstance(results, list):
            results['compute_class'] = {
                'id': ccid,
                'name': self.ccs[ccid].name,
                'value': self.ccs[ccid].value
            }
        else:
            trial_id = trial_id.split('@')
            ccdata = {
                'id': ccid,
                'name': self.ccs[ccid].name,
                'value': self.ccs[ccid].value
            }
            for r in results:
                r['compute_class'] = ccdata


        # Update the DB with the result
        self.backend.register_result(ss_id, trial_id, loss, results)

        # Reassign models to CCs at some frequency
        n_completed = sum([1 for trial in self.backend.trials.values()
                           if trial.status.value == 3])
        if n_completed % 10 == 0:
            self.assign_to_ccs()

        # Update the number of enqueued items
        self.ccs[ccid].current_tasks -= 1

    def failure(self, tag, resub):
        """Handle task failure.

        Parameters
        ----------
        task : `work_queue.Task`
            The failed task to process.

        Notes
        -----
        This method will resubmit failed tasks on request to account for
        potential worker dropout, etc.
        """
        # Get bookkeeping information from the task tag
        trial_id, ss_id, ccid = tag.split('.')

        trials = trial_id.split('@')

        # Determine whether or not to resubmit
        submissions, params = \
            self.backend.register_result(ss_id, trial_id, objective=None,
                                         results=None, errmsg='yes')

        # Resubmit the task if it should be, otherwise update the number of
        # enqueued items.
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
