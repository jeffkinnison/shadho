"""
"""
import uuid


class ComputeClass(object):
    def __init__(self, name, resource, value, max_tasks):
        self.id = str(uuid.uuid4())
        self.name = name
        self.resource = resource
        self.value = value
        self.max_tasks = max_tasks
        self.current_tasks = 0

    def __hash__(self):
        return hash((self.id, self.name, self.resource, self.value))
