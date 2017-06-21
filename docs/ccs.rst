Compute Classes
===============

Not all computers are created equal: CPUs and GPUs require different approaches
and are appropriate for different problems, for example. `shadho` allows you to
specify **Compute Classes** (CC), groups of computers with similar hardware or
performance to better manage your distributed resources.

CCs are defined by you because a lot of variation exists in the world of
distirbuted environments. One user may have access to uniform resources through
a cloud provider; another may have a hodge-podge of different systems managed by
different organizations (think academic clusters). If you have two computers--one
with 8 CPUs and one with a GPU--you probably want to run the more complex or more
important jobs on the GPU machine.

``shadho`` uses CCs to organize searches based on the relative complexity and
importance of particular values.

::

    from shadho import ComputeClass

    # Pass a name, the name of the hardware
    cc = ComputeClass('myclass', 'gpu', 'TITAN X (Pascal)')
