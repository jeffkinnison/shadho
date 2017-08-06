"""
"""
from shadho.backend import *
from shadho.managers import *
from shadho.config import *

import time


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
                   else ComputeClass('all', None, None, max_tasks)

        self.files = files
        self.trees = make_forest(spec,
                            use_complexity=use_complexity,
                            use_priority=use_priority)

        self.assign_to_ccs()

    def run(self):
        start = time.time()
        current = start
        curr_tasks = 0
        while current - start < timeout:
            tasks = self.generate()

    def generate(self):
        pass

    def assign_to_ccs(self):
