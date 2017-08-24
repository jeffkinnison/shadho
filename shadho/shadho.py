"""
"""
from shadho.backend import *
from shadho.managers import *
from shadho.config import *

import json
import os
import tarfile
import tempfile
import time

import numpy as np


def shadho():
    pass


class SHADHO(object):
    def __init__(self, spec, ccs, files, use_complexity=True, use_priority=True,
                 timeout=600, max_tasks=100):
        self.config = ShadhoConfig()
        self.backend = JSONBackend()
        self.manager = WQManager(name=self.config['workqueue']['name'],
                                 port=self.config['workqueue']['port'],
                                 exclusive=self.config['workqueue']['exclusive'],
                                 shutdown=self.config['workqueue']['shutdown'],
                                 catalog=self.config['workqueue']['catalog'],
                                 logfile=self.config['workqueue']['logfile'],
                                 debugfile=self.config['workqueue']['debugfile'])
        self.timeout = timeout
        self.ccs = ccs if ccs is not None and len(ccs) > 0 \
            else [ComputeClass('all', None, None, max_tasks)]

        self.files = files
        self.trees = make_forest(spec,
                                 use_complexity=use_complexity,
                                 use_priority=use_priority)

        self.assignments = {}
        self.assign_to_ccs()

        self.__tmpdir = tempfile.mkdtemp()

    def __del__(self):
        if hasattr(self, '__tmpdir') and self.__tmpdir is not None:
            os.rmdir(self.__tmpdir)

    def run(self):
        start = time.time()
        elapsed = 0
        while elapsed < timeout:
            self.assign_to_ccs()
            params = self.generate()
            tasks = self.make_tasks(params)
            for t in tasks:
                self.manager.submit(t)
            task = self.manager.wait(timeout=10)
            if task is not None:
                if task.result == work_queue.WORK_QUEUE_RESULT_SUCCESS:
                    self.__success(task)
                else:
                    self.__failure(task)
            elapsed = time.time() - start

        self.backend.get_opt(mode='global')

    def generate(self):
        params = []
        for cc in self.ccs:
            n = cc.max_tasks - cc.current_tasks
            assignments = self.assignments[cc]
            for i in range(n):
                idx = np.random.randint(len(assignments))
                param = self.backend.generate()
                param = (param[0], cc.id, param[1])
                params.append(param)
            cc.current_tasks = cc.max_tasks
        return params

    def make_tasks(self, params):
        tasks = []
        for p in params:
            tag = '.'.join([p[0], p[1]])
            buff = WQBuffer(str(json.dumps(p[1])),
                            self.config['global']['result_file'],
                            cache=False)
            files = [f for f in self.files]
            files.append(buff)
            task = self.manager.make_task(self.cmd, tag, files)
            tasks.append(task)
        return tasks

    def assign_to_ccs(self):
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
        rid, ccid = str(task.tag).split('.')

        try:
            result = tarfile.open('.'.join([rid,
                                            self.config['global']['output']]),
                                  'r')
            resultstr = result.extractfile(self.config['global']['result_file'])
            result.close()
        except IOError:
            print("Error opening task {} result".format(rid))

        result = json.loads(resultstr.decode('utf-8'))
        self.backend.register_result(rid, result['loss'], result)

        for cc in self.ccs:
            if cc.id == ccid:
                cc.current_tasks -= 1


    def __failure(self, task):
        print('Task {} failed with result {} and WQ status {}'
              .format(task.tag, task.result, task.return_status))
        print(task.output)

        ccid = str(task.tag)[1]
        for cc in self.ccs:
            if cc.id == ccid:
                cc.current_tasks -= 1
