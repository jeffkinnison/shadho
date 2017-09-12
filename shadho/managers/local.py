"""
"""
import json
import time
import uuid


class LocalManager(object):
    def __init__(self):
        self.tasks = []

    def make_task(self, cmd, tag, files):
        task = LocalTask(cmd)

    def run_task(self):
        return self.tasks[0].run() if len(self.tasks) > 0 else None

    def submit(self, task):
        self.tasks.append(task)

    def wait(self, timeout=None):
        return self.tasks[0].run() if len(self.tasks) > 0 else None


class LocalTask(object):
    def __init__(self, cmd):
        self.id = str(uuid.uuid4())
        self.cmd = cmd

    def specify_cmd(self, cmd):
        self.cmd = cmd

    def specify_tag(self):
        self.tag = 0

    def specify_cores(self, cores):
        pass

    def specify_resource(self, name, value):
        pass

    def specify_buffer(self, buffer, remote_name='', cache=False):
        self.params = json.loads(buffer)

    def run(self):
        return self.cmd(**self.params)
