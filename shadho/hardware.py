"""
"""
import uuid
import sys
sys.path.append("./pyrameter")
from pyrameter.modelgroup import ModelGroup
from pyrameter.models.model import Model

class ComputeClass(object):
    def __init__(self, name, resource, value, max_tasks):
        self.id = str(uuid.uuid4())
        self.name = name
        self.resource = resource
        self.value = value
        self.max_tasks = max_tasks
        self.current_tasks = 0

        self.model_group = ModelGroup()

    def __hash__(self):
        return hash((self.id, self.name, self.resource, self.value))

    def generate(self, model_id):
        return self.model_group.generate(model_id)

    def add_model(self, model):
        if not self.model_group:
            self.model_group = ModelGroup(model)
        else:
            self.model_group.add_model(model)

    def remove_model(self, model_id):
        self.model_group.remove_model(model_id)

    def clear(self):
        for model_id in self.model_group.model_ids:
            self.remove_model(model_id)

    def register_result(self, model_id, result_id, loss, results=None):
        self.model_group.register_result(model_id, result_id, loss,
                                         results=results)
