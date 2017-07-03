"""
"""
import os.path
import uuid


class JSONBackend(object):
    def __init__(self, path='.'):
        path = os.path.abspath(path)
        self.fname = os.path.join(path, 'shadho.json')
        self.json = {}

    def add(self, obj):
        pass

    def query(self, type):
        pass

    def remove(self, obj):
        pass

    def commit(self):
        pass


class Tree(object):
    def __init__(self, complexity=None, priority=None, rank=None):
        self.id = str(uuid.uuid4())
        self.complexity = complexity
        self.priority = priority
        self.rank = rank


class Node(object):
    def __init__(self):
        pass


class Space(object):
    def __init__(self):
        pass

class Value(object):
    def __init__(self):
        pass


class Result(object):
    def __init__(self):
        pass
