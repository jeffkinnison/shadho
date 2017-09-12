"""
"""
from .backend import *
from .config import ShadhoConfig
from .hardware import ComputeClass
from .managers import *

import json
import os
import tarfile
import tempfile
import time

import numpy as np


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
        self.cmd = cmd
        self.config = ShadhoConfig()
        # self.backend = JSONBackend()
        # self.manager = WQManager(name=self.config['workqueue']['name'],
        #                          port=self.config['workqueue']['port'],
        #                          exclusive=self.config['workqueue']['exclusive'],
        #                          shutdown=self.config['workqueue']['shutdown'],
        #                          logfile=self.config['workqueue']['logfile'],
        #                          debugfile=self.config['workqueue']['debugfile'])
        self.timeout = timeout
        self.ccs = ccs if ccs is not None and len(ccs) > 0 \
            else [ComputeClass('all', None, None, max_tasks)]

        self.files = []
        if files is not None:
            for f in files:
                if not isinstance(f, WQFile):
                    self.add_input_file(f)
                else:
                    self.files.append(f)

        self.trees = self.backend.make_forest(spec,
                                              use_complexity=use_complexity,
                                              use_priority=use_priority)

        self.assignments = {}

        self.__tmpdir = tempfile.mkdtemp(prefix='shadho_', suffix='_output')

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
        self.files.append(WQFile(localpath,
                                 remotepath=remotepath,
                                 ftype='input',
                                 cache=cache))

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
        self.files.append(WQFile(localpath,
                                 remotepath=remotepath,
                                 ftype='output',
                                 cache=cache))

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
        self.ccs.append(ComputeClass(name, resource, value, max_tasks))

    def run(self):
        """Search hyperparameter values on remote workers.
        """
        if not hasattr(self, 'manager'):
            create_manager(manager_type=self.config['global']['manager'],
                           config=self.config)

        if not hasattr(self, 'backend'):
            create_backend(backend_type=self.config['global']['backend'])

        start = time.time()
        elapsed = 0
        try:
            while elapsed < self.timeout:
                self.assign_to_ccs()
                params = self.generate()
                tasks = self.make_tasks(params)
                for t in tasks:
                    self.manager.submit(t)
                task = self.manager.wait(timeout=10)
                if task is not None:
                    if self.manager.task_succeeded(task):
                        self.__success(task)
                    else:
                        self.__failure(task)
                elapsed = time.time() - start
        except KeyboardInterrupt:
            if hasattr(self, '__tmpdir') and self.__tmpdir is not None:
                os.rmdir(self.__tmpdir)

        print(self.backend.get_optimal(mode='global'))

    def generate(self):
        """Generate hyperparameter values to test.

        Returns
        -------
        params : list of tuple
            A list of triples (result_id, compute_class_id, parameter_values).
        """
        params = []
        for cc in self.ccs:
            n = cc.max_tasks - cc.current_tasks
            assignments = self.assignments[cc]
            for i in range(n):
                idx = np.random.randint(len(assignments))
                param = self.backend.generate(assignments[idx])
                param = (param[0], cc.id, param[1])
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
            outfile = WQFile(os.path.join(self.__tmpdir,
                                          '.'.join([tag,
                                            self.config['global']['output']])),
                             remotepath=self.config['global']['output'],
                             ftype='output',
                             cache=False)
            files = [f for f in self.files]
            files.append(buff)
            files.append(outfile)
            task = self.manager.make_task(self.cmd, tag, files)
            tasks.append(task)
        return tasks

    def assign_to_ccs(self):
        """Assign trees to compute classes.
        """
        self.backend.update_rank()

        if len(self.ccs) == 1:
            self.assignments[self.ccs[0]] = self.trees
            return

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

    def __success(self, task):
        """Handle successful task completion.

        Parameters
        ----------
        task : `work_queue.Task`
            The task to process.
        """
        # Extract the result and compute class ids
        rid, ccid = str(task.tag).split('.')

        try:
            # Open the result tarfile and get the results file.
            outfile = '.'.join([task.tag,
                                self.config['global']['output']])
            result = tarfile.open(os.path.join(self.__tmpdir, outfile), 'r')
            resultstr = result.extractfile(self.config['global']['result_file']).read()
            result.close()
        except IOError:
            print("Error opening task {} result".format(rid))

        result = json.loads(resultstr.decode('utf-8'))
        self.backend.register_result(rid, result['loss'], result)

        for cc in self.ccs:
            if cc.id == ccid:
                cc.current_tasks -= 1


    def __failure(self, task):
        """Handle task failure.

        Parameters
        ----------
        task : `work_queue.Task`
            The failed task to process.
        """
        print('Task {} failed with result {} and WQ status {}'
              .format(task.tag, task.result, task.return_status))
        print(task.output)

        ccid = str(task.tag).split('.')[1]
        for cc in self.ccs:
            if cc.id == ccid:
                cc.current_tasks -= 1
