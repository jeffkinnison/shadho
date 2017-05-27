# -*- coding: utf-8 -*-
"""Main driver for distributed hyperparameter search.

Classes
-------
HyperparameterSearch: perform hyperparameter search with or without decisions
"""

from .forest import OrderedSearchForest
from .config import WQConfig

import json
import os
import tarfile
import time
import uuid

import numpy as np

import work_queue
from work_queue import WorkQueue


class HyperparameterSearch(object):
    """Perform distributed hyperparameter search.

    This class conducts and manages distributed hyperparameter search using the
    data structures, heuristics, and techniques described in REFERENCE. The
    search is fully configurable, meaning users may define the expected runtime
    environments, whether to direct the search using complexity and priority
    heuristics, and stopping conditions.

    Parameters
    ----------
    spec : dict
        Specification to build an OrderedSearchForest.
    ccs : list(shadho.ComputeClass)
        The ordered list of compute classes that will connect.
    wq_config : {dict, shadho.WQConfig}
        Work Queue master and task configurations.
    use_complexity: {True, False}, optional
        If True, use the complexity heuristic to adjust search proportions.
    use_priority: {True, False}, optional
        If True, use the priority heuristic to adjust search proportions.
    timeout: {600, int}, optional
        Search timeout in seconds.
    max_tasks: {100, int}, optional
        The maximum number of concurrent searches to maintain.

    See Also
    --------

    """

    def __init__(self, spec, ccs, wq_config, use_complexity=True,
                 use_priority=True, timeout=600, max_tasks=100):
        self.wq_config = WQConfig(**wq_config) \
                            if isinstance(wq_config, dict) else wq_config
        work_queue.cctools_debug_flags_set("all")
        work_queue.cctools_debug_config_file(self.wq_config['debug'])
        work_queue.cctools_debug_config_file_size(0)
        self.wq = WorkQueue(port=int(self.wq_config['port']),
                            name=str(self.wq_config['name']),
                            catalog=self.wq_config['catalog'],
                            exclusive=self.wq_config['exclusive'],
                            shutdown=self.wq_config['shutdown']
                            )
        self.forest = SearchForest(spec)
        self.ccs = [] if ccs is None else ccs
        self.use_complexity = use_complexity
        self.use_priority = use_priority
        self.timeout = timeout
        self.max_tasks = max_tasks
        self.wq.specify_log(self.wq_config['logfile'])

    def optimize(self):
        """Run the distributed hyperparameter search.
        """
        start = time.time()
        elapsed = 0
        if len(self.ccs) > 0:
            self.assign_to_ccs()
            for cc in self.ccs:
                print(str(cc))
        while elapsed < self.timeout:
            n_tasks = self.max_tasks - self.wq.stats.tasks_waiting
            tasks = self.__generate_tasks(n_tasks)
            for task in tasks:
                self.wq.submit(task)
            task = self.wq.wait(timeout=30)
            if task is not None:
                if task.result == work_queue.WORK_QUEUE_RESULT_SUCCESS:
                    self.__success(task)
                else:
                    self.__failure(task)
            elapsed = time.time() - start
            if len(self.ccs) > 0:
                for cc in self.ccs:
                    print(str(cc))

        self.forest.write_all()

    def __generate_tasks(self, n_tasks):
        """Generate values to search.

        Parameters
        ----------
        n_tasks : int
            The number of tasks to generate.

        Returns
        -------
        tasks : list(work_queue.Task)
            The tasks to submit to Work Queue.
        """
        tasks = []
        if (not self.use_complexity and not self.use_priority) or len(self.ccs) == 0:
            for i in range(n_tasks):
                task = work_queue.Task(self.wq_config['command'])

                tid, spec = self.forest.generate()
                tag = '.'.join([str(uuid.uuid4()), tid])
                task.specify_tag(tag)

                for f in self.wq_config['files']:
                    f.add_to_task(task, tag=''
                                  if f.type == work_queue.WORK_QUEUE_INPUT
                                  else str(tag + '.'))

                task.specify_buffer(str(json.dumps(spec)),
                                    remote_name=str('hyperparameters.json'),
                                    flags=work_queue.WORK_QUEUE_NOCACHE
                                    )
                tasks.append(task)
        else:
            self.assign_to_ccs()
            for cc in self.ccs:
                specs = cc.generate()
                for s in specs:
                    tid, spec = s
                    task = work_queue.Task(self.wq_config['command'])

                    tag = '.'.join([str(uuid.uuid4()), cc.name, tid])
                    task.specify_tag(tag)
                    if cc.resource == 'cores':
                        task.specify_cores(cc.value)

                    for f in self.wq_config['files']:
                        f.add_to_task(task, tag=''
                                      if f.type == work_queue.WORK_QUEUE_INPUT
                                      else str(tag + '.'))

                    task.specify_buffer(str(json.dumps(spec)),
                                        remote_name=str('hyperparameters.json'),
                                        flags=work_queue.WORK_QUEUE_NOCACHE
                                        )
                    tasks.append(task)
        return tasks

    def assign_to_ccs(self):
        """Assign hyperparameter search spaces to compute classes.

        This function iterates over the set of trees five times and over the
        compute classes twice. If we can reduce this, that would be suuuuper.
        """
        # TODO: Reduce the number of times iterating over things
        # TODO: Make the assignments agnostic to the number of trees and ccs
        # Clear the assignments within both trees and Compute Classes
        trees = [self.forest.trees[key] for key in self.forest.trees]
        for cc in self.ccs:
            cc.clear_assignments()
        for tree in trees:
            tree.rank = 1   # Clear the rank for re-ordering
            tree.clear_assignments()

        # Sort trees by complexity if using the complexity heuristic
        if self.use_complexity:
            trees.sort(key=lambda x: x.complexity, reverse=True)
            for i in range(len(trees)):
                trees[i].rank *= (i + 1)

        # Sort trees by priority if using the complexity heuristic
        if self.use_priority:
            trees.sort(key=lambda x: x.priority, reverse=True)
            for i in range(len(trees)):
                trees[i].rank *= (i + 1)

        trees.sort(key=lambda x: x.rank)

        # larger, smaller = (trees, self.ccs) \
        #     if len(trees) > len(self.ccs) else (self.ccs, trees)
        x = float(len(larger)) / float(len(smaller))
        y = x - 1
        j = 0
        n = len(larger) / 2

        for i in range(len(trees)):
            if i > np.ceil(y):
                j += 1
                y += x
            trees[i].assign(self.ccs[j])
            self.ccs[j].assign(trees[i])

            if i <= n:
                trees[i].assign(self.ccs[j + 1])
                self.ccs[j + 1].assign(trees[i])

            if i > n:
                trees[i].assign(self.ccs[j - 1])
                self.ccs[j - 1].assign(trees[i])

    def __success(self, task):
        """Default handling for successful task completion.
        """
        # Task tag is unique and contains information about the tree its values
        # came from and the compute class it was assigned to.
        tag = str(task.tag)
        print('Task {} was successful'.format(tag))
        ids = tag.split('.')

        # Get the correct tree from the OSF
        tree_id = ids[-1]
        tree = self.forest.trees[tree_id]

        # Extract the results from the output tar file.
        try:
            result = tarfile.open('.'.join([tag, 'out.tar.gz']), 'r')
            resultstring = result.extractfile('performance.json').read()
            result.close()
        except IOError:
            print('Error opening task {} result'.format(tag))

        # Load the results from file and store them to the correct tree
        result = json.loads(resultstring.decode('utf-8'))
        result['task_id'] = task.id
        tree.add_result(result['params'],
                        result,
                        update_priority=self.use_priority)

        # If using Compute Classes, update task statistics.
        if len(self.ccs) > 0:
            ccid = ids[1]
            for cc in self.ccs:
                if cc.name == ccid:
                    cc.submitted_tasks -= 1

        # Clean up
        os.remove('.'.join([tag, 'out.tar.gz']))

    def __failure(self, task):
        """Default handling for task failure.
        """
        # Report the failure and print any output for debugging.
        print('Task {} failed with result {} and WQ status {}'
              .format(task.tag, task.result, task.return_status))
        print(task.output)

        # If using Compute Classes, update task statistics.
        if len(self.ccs) > 0:
            ccid = task.tag.split('.')[1]
            for cc in self.ccs:
                if cc.name == ccid:
                    cc.submitted_tasks -= 1
