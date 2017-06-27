# -*- coding: utf-8 -*-
"""Helper for grouping similar hardware.

Classes
-------
ComputeClass: Group distributed compute nodes by hardware properties.
"""
import json
import uuid

import numpy as np

from work_queue import Task


class ComputeClass(object):
    """Group distributed compute nodes by hardware properties.

    Parameters
    ----------
    name : str
        The name of the compute class.
    resource : str
        The name of the required resource.
    value : str or int
        The value of the required resource.
    max_tasks : int
        The expected maximum number of concurrent tasks to run.
    inputs : list of shadho.config.WQFile, optional
        The set of input files to send to this compute class.
    output : str
        Name of the expected output file from this compute class. Default:
        ``out.tar.gz``
    adapt_max_tasks : bool, optional
        (Future Release) If true, determine the max number of tasks based on
        connected workers with this compute class's resource/value pair.

    Attributes
    ----------
    name : str
        The name of the compute class.
    resource : str
        The name of the required resource.
    value : str or int
        The value of the required resource.
    max_tasks : int
        The expected maximum number of concurrent tasks to run.


    """

    def __init__(self, name, resource, value, max_tasks, inputs=None,
                 output='out.tar.gz', adapt_max_tasks=False):
        self.name = name
        self.resource = resource
        self.value = value
        self.max_tasks = max_tasks
        self.inputs = inputs
        self.output = output

    def create_task(self, cmd, tag):
        task = Task(cmd)

        tag = '.'.join([str(uuid.uuid4()), tag])

        if self.resource == 'cores':
            task.specify_cores(self.value)
        else:
            task.specify_resource(self.resource, self.value)

        for i in self.inputs:
            i.add_to_task(task)

        self.output.add_to_task(task, tag=tag)

        return task


    def update_max_tasks(self):
        """Update the max tasks for this CC based on the number of workers.

        Makes a call to the Work Queue catalog to determine how many of the
        workers connected to this Work Queue master have the resource requested
        by this CC.

        Returns
        -------
        max_tasks : int
            The maximum number of tasks to submit to the queue.

        """
        pass

    def __str__(self):
        kids = ' '.join([str(a.root.children[0].name)
                         for a in self.assignments])
        return ' '.join([self.name, ': [', kids, ']'])
