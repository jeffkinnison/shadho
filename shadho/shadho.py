"""
"""
from .backend import create_backend
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
import scipy.stats


def shadho():
    pass


class Shadho(object):
    """Optimize hyperparameters using specified hardware.

    Parameters
    ----------
    spec : dict
        The specification defining search spaces.
    files : list of str or WQFile
        The files to send to remote workers for task execution.
    ccs : list of `shadho.hardware.ComputeClass`, optional
        The types of hardware to expect during optimization. If not supplied,
        tasks are run on the first available worker.
    use_complexity : bool, optional
        If True, use the complexity heuristic to adjust search proportions.
    use_priority : bool, optional
        If True, use the priority heuristic to adjust search proportions.
    timeout : int, optional
        Number of seconds to search for.
    max_tasks : int, optional
        Number of tasks to queue at a time.

    Attributes
    ----------
    config : `shadho.config.ShadhoConfig`
        Global configurations for shadho.
    backend : `shadho.backend.basedb.BaseBackend`
        The data storage backend.
    manager : `shadho.managers.workqueue.WQManager`
        The distributed task manager to use.
    trees : list
        The ids of every tree in the search forest.
    ccs : list of `shadho.hardware.ComputeClass`
        The types of hardware to expect during optimization. If not supplied,
        tasks are run on the first available worker.
    assignments : dict
        Record of trees assigned to compute classes.
    timeout : int
        Number of seconds to search for.

    """

    def __init__(self, cmd, spec, ccs=None, files=None, use_complexity=True,
                 use_priority=True, timeout=600, max_tasks=100):
        self.config = ShadhoConfig()
        self.cmd = cmd
        self.spec = spec
        self.use_complexity = use_complexity
        self.use_priority = use_priority
        self.timeout = timeout
        self.max_tasks = max_tasks

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
            self.config['global']['shadho_dir'],
            self.config['global']['wrapper']))

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
        cc = ComputeClass(name, resource, value, max_tasks)
        self.ccs[cc.id] = cc

    def run(self):
        """Search hyperparameter values on remote workers.
        """
        if not hasattr(self, 'manager'):
            self.manager = create_manager(
                manager_type=self.config['global']['manager'],
                config=self.config,
                tmpdir=self.__tmpdir)

        if not hasattr(self, 'backend'):
            self.backend = create_backend(
                backend_type=self.config['global']['backend'],
                config=self.config)

        if len(self.ccs) == 0:
            cc = ComputeClass('all', None, None, self.max_tasks)
            self.ccs[cc.id] = cc

        self.trees = self.backend.make_forest(
            self.spec,
            use_complexity=self.use_complexity,
            use_priority=self.use_priority)

        start = time.time()
        elapsed = 0
        try:
            while elapsed < self.timeout:
                self.assign_to_ccs()
                params = self.generate()
                for p in params:
                    print(p)
                    tag = '.'.join([p[0], p[1]])
                    cc = self.ccs[p[1]]
                    self.manager.add_task(self.cmd,
                                          tag,
                                          p[-1],
                                          files=self.files,
                                          resource=cc.resource,
                                          value=cc.value)
                result = self.manager.run_task()
                if result is not None:
                    if len(result) == 4:
                        self.success(*result)
                    else:
                        self.failure(*result)
                elapsed = time.time() - start
        except KeyboardInterrupt:
            if hasattr(self, '__tmpdir') and self.__tmpdir is not None:
                os.rmdir(self.__tmpdir)

        opt = self.backend.get_optimal(mode='global')
        print("Optimal loss: {}".format(opt[0]))
        print("With parameters: {}".format(opt[1]))
        print("And additional results: {}".format(opt[2]))

    def generate(self):
        """Generate hyperparameter values to test.

        Returns
        -------
        params : list of tuple
            A list of triples (result_id, compute_class_id, parameter_values).
        """
        params = []
        for ccid in self.ccs:
            cc = self.ccs[ccid]
            n = cc.max_tasks - cc.current_tasks
            assignments = self.assignments[ccid]
            rng = scipy.stats.randint(0, len(assignments))
            for i in range(n):
                idx = rng.rvs()
                rid, param = self.backend.generate(assignments[idx])
                param = (rid, ccid, param)
                params.append(param)
            cc.current_tasks = cc.max_tasks
        return params

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
                            self.config['global']['param_file'],
                            cache=False)
            outfile = WQFile(os.path.join(
                                self.__tmpdir,
                                '.'.join([tag,
                                          self.config['global']['output']])),
                             remotepath=self.config['global']['output'],
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
        """
        self.backend.update_rank()

        if len(self.ccs) == 1:
            self.assignments[list(self.ccs.keys())[0]] = self.trees
            return

        else:
            for cc in self.ccs:
                self.assignments[cc] = []

            larger = self.trees if len(self.trees) >= len(self.ccs) else self.ccs
            smaller = self.trees if len(self.trees) < len(self.ccs) else self.ccs

            x = float(len(larger)) / float(len(smaller))
            y = x - 1
            j = 0
            n = len(larger) / 2

            for i in range(len(larger)):
                if i > np.ceil(y):
                    j += 1
                    y += x

                if smaller[j] in self.assignments:
                    self.assignments[smaller[j]].append(larger[i])
                    if i <= n:
                        self.assignments[smaller[j + 1]].append(larger[i])
                    else:
                        self.assignments[smaller[j - 1]].append(larger[i])
                else:
                    self.assignments[larger[i]].append(smaller[j])
                    if i <= n:
                        self.assignments[larger[i]].append(smaller[j + 1])
                    else:
                        self.assignments[larger[i]].append(smaller[j - 1])

    def success(self, rid, ccid, loss, results):
        """Handle successful task completion.

        Parameters
        ----------
        task : `work_queue.Task`
            The task to process.
        """
        self.backend.register_result(rid, loss, results=results)
        self.ccs[ccid].current_tasks -= 1


    def failure(self, rid, ccid):
        """Handle task failure.

        Parameters
        ----------
        task : `work_queue.Task`
            The failed task to process.
        """
        self.ccs[ccid].current_tasks -= 1
