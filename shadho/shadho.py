"""
"""
from shadho.backend import *
from shadho.managers import *
from shadho.config import *

import json
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

    def run(self):
        start = time.time()
        current = start
        while current - start < timeout:
            self.assign_to_ccs()
            params = self.generate()
            tasks = self.make_tasks(params)
            for t in tasks:
                self.manager.submit(t)
            task = self.manager.wait(timeout=10)
            if task is not None:
                self.__success(task)
            else:
                self.__failure(task)
            current = time.time()

        self.backend.get_opt(mode='global')

    def generate(self):
        params = []
        for cc in self.ccs:
            n = cc.max_tasks - cc.current_tasks
            assignments = self.assignments[cc]
            for i in range(n):
                idx = np.random.randint(len(assignments))
                param = self.backend.generate()
                params.append(param)
        return params

    def make_tasks(self, params):
        tasks = []
        for p in params:
            p =

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
