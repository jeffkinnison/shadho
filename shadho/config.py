"""Helper objects for configuring and using Work Queue.
"""

import json
import os

import work_queue


class WQConfig(object):
    """Data store for WorkQueue master and task configuration information.

    Work Queue [1]_ has a large number of configurations for both Work Queue
    masters and Work Queue tasks. This object provides a standard interface for
    the configurations with default values so that users can use only the
    features they need.

    Parameters
    ----------
    name : str
        The name of the Work Queue master, used to direct workers to the
        correct master and for potential Work Queue statistical information.
    port : {work_queue.WORK_QUEUE_DEFAULT_PORT, int}, optional
        The port on which the master will listen.
    catalog : {False, True}, optional
        Whether or not to run the Work Queue master in catalog mode. Catalog
        mode allows workers to find the master by its name rather than by its
        hostname and port.
    exclusive : {True, False}, optional
        If True, prevents this process from starting additional Work Queue
        masters. Other processes, however, may do so.
    logfile : {'wq_shadho.log', str}, optional
        Name of the log file to write to. The log file records statistics about
        connected workers, submitted tasks, network usage, etc. Output roughly
        as a csv file.
    debug : {'wq_shadho.debug', str}, optional
        Name of the debug file to write to. The debug file contains Work Queue
        master output and information about all workers and tasks that interact
        with the master.
    password : {False, True}, optional
        If True, requires workers to send the correct password to the master
        before receiving tasks. A password entry prompt will be displayed when
        this object is initialized.
    command : {None, str}, optional
        The command for tasks to execute. Format identical to how a command
        would be run in terminal, e.g. 'python example.py 1 foo'
    files : {None, list(dict)}, optional
        The input and output files that should be sent to and returned from
        each task.

    Notes
    -----
    Information about the Work Queue Python API can be foung in the `CCTools
    documentation<http://ccl.cse.nd.edu/software/manuals/api/html/namespaceWorkQueuePython.html>`_.

    References
    ----------
    .. _[1] Li Yi, Christopher Moretti, Scott Emrich, Kenneth Judd, and Douglas
           Thain. 2009. Harnessing parallelism in multicore clusters with the
           all-pairs and wavefrontabstractions. In Proceedings of the 18th ACM
           international symposium on High performance distributed computing.
           ACM, 1–10.

    """

    def __init__(self, name, port=work_queue.WORK_QUEUE_DEFAULT_PORT,
                 catalog=False, exclusive=True, shutdown=False,
                 logfile='wq_shadho.log', debug='wq_shadho.debug',
                 password=False, command=None, files=None):
        if password:
            p = getpass.getpass('Supply a password:')
        else:
            p = None

        self.cfg = {
            'name': name,
            'port': port,
            'catalog': catalog,
            'exclusive': exclusive,
            'shutdown': shutdown,
            'logfile': logfile,
            'debug': debug,
            'wq_logfile': wq_logfile,
            'task_logfile': task_logfile,
            'password': p,
            'command': command,
            'files': self.add_files(files) if files else []
        }

    def __getitem__(self, key):
        try:
            val = self.cfg[key]
        except KeyError:
            val = None
        return val

    def __setitem__(self, key, val):
        self.cfg[key] = val

    def add_files(self, files):
        '''Add files to be sent to with Tasks.

        Each file should be specified in the following format:

            ``{
                'localpath': # Path to the local file,
                'remotepath': # Path to/name of the file after transfer,
                'type': # 'input' or 'output',
                'cache': # True or False, whether to cache the file remotely
            }``

        Parameters
        ----------
        files : list(dict)
            The list of files, each specified as above.

        Returns
        -------
        wqfs : list(shadho.config.WQFile)
            The list of Work Queue files to send to/receive from each task.

        '''
        wqfs = []
        for f in files:
            try:
                wqf = WQFile(f['localpath'], f['remotepath'],
                             f['type'], cache=f['cache'])
                wqfs.append(wqf)
            except KeyError:
                continue

        return wqfs


class WQFile(object):
    """Representation of a file to send to/receive from a remote worker.

    Parameters
    ----------
    localpath : str
        Path to the local copy of the file.
    remotepath : str
        Path to the file after transferred to the Work Queue worker.
    type : {'input', 'output', 'buffer'}, optional
        Whether the file is an input file (to send to a worker), an output file
        (to receive from a worker), or created from a string buffer.
    cache : {False, True}, optional
        Whether to cache the file on a Work Queue worker between tasks. Doing
        so can reduce the overhead of running multiple tasks on a worker by
        preserving files common to all tasks.

    Notes
    -----
    For more information on Work Queue file specifications, see the `CCTools
    documentation<http://ccl.cse.nd.edu/software/manuals/api/html/work__queue_8h.html#a8f9af7213ea271d3b58fe0f62ad160c0>`_.

    """

    def __init__(self, localpath, remotepath=None,
                 type='input', cache=False):
        self.localpath = localpath
        self.remotepath = remotepath if remotepath else os.basename()
        self.type = work_queue.WORK_QUEUE_INPUT \
            if type == 'input' else work_queue.WORK_QUEUE_OUTPUT
        self.cache = work_queue.WORK_QUEUE_CACHE \
            if cache else work_queue.WORK_QUEUE_NOCACHE

    def add_to_task(self, task, tag=''):
        task.specify_file(str(''.join([tag, self.localpath])),
                          remote_name=str(self.remotepath),
                          type=self.type,
                          cache=self.cache
                          )
