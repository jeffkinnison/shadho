"""
"""
import os

import work_queue


class WQManager(work_queue.WorkQueue):
    """Work Queue master with utilities to generate conformant tasks.

    Parameters
    ----------
    name : str, optional
        The name of this Work Queue master, 'shadho' by default.
    port : int, optional
        The port that the master will listen on. 9123 by default.
    exclusive : bool, optional
        Whether to allow multiple Work Queue masters in the same process. True
        by default.
    shutdown : bool, optional
        Whether to shut down connected workers when this manager shuts down.
        True by default.
    logfile : str, optional
        Where to write Work Queue logs. ./wq_shadho.log by default.
    debugfile : str, optional
            Where to write Work Queue debug logs. ./wq_shadho.debug by default.

    """

    def __init__(self, name='shadho', port=9123, exclusive=True, shutdown=True,
                 logfile='shadho_wq.log', debugfile='shadho_wq.debug'):
        work_queue.cctools_debug_flags_set("all")
        work_queue.cctools_debug_config_file(debugfile)
        work_queue.cctools_debug_config_file_size(0)

        super(WQManager, self).__init__(name=name,
                                        port=port,
                                        exclusive=exclusive,
                                        shutdown=shutdown,
                                        catalog=False)

        self.specify_log(logfile)

    def make_task(self, cmd, tag, files):
        """Create a task for this manager.

        Parameters
        ----------
        cmd : str
            The command to run on the remote worker, e.g. ``echo hello`` or
            ``python script.py``.
        tag : str
            The tag to give this task.
        files : list of `WQFile` or `WQBuffer`
            The input and output files and data buffers that this task will
            send/receive.

        Notes
        -----
        Any command may be passed to the task to run, and the task makes stdout
        and stderr of the command available upon return, regardless of failure.

        See Also
        --------
        `shadho.managers.workqueue.WQFile`
        `shadho.managers.workqueue.WQBuffer`
        `work_queue.Task`
        """
        task = work_queue.Task(cmd)
        task.specify_tag(tag)

        for f in files:
            f.add_to_task(task)

        return task

    def task_succeeded(self, task):
        return task is not None and \
               task.result == work_queue.WORK_QUEUE_RESULT_SUCCESS


class WQFile(object):
    """File to send to or receive from a remote worker.

    Parameters
    ----------
    localpath : str
        The path to the file on the local system.
    remotepath : str, optional
        Where to place the file on the remote worker relative to cwd. Set to
        the basename of `localpath` by default (e.g. foo/bar.baz -> bar.baz).
    ftype : {'input', 'output'}
        Whether to send this file to or expect to receive it from the remote
        worker.
    cache : bool, optional
        Whether to cache this file on the remote worker.

    Attributes
    ----------
    localpath : str
        The path to the file on the local system.
    remotepath : str
        Where to place the file on the remote worker relative to remote cwd.
    ftype : {'input', 'output'}
        Whether to send this file to or expect to receive it from the remote
        worker.
    cache : bool
        Whether to cache this file on the remote worker.

    """

    TYPES = {
        'input': work_queue.WORK_QUEUE_INPUT,
        'output': work_queue.WORK_QUEUE_OUTPUT,
    }

    CACHE = {
        True: work_queue.WORK_QUEUE_CACHE,
        False: work_queue.WORK_QUEUE_NOCACHE
    }

    def __init__(self, localpath, remotepath=None, ftype='input', cache=True):
        if ftype != 'output' and not os.path.isfile(localpath):
            raise IOError("{} does not exist.".format(localpath))
        else:
            self.localpath = localpath

        self.remotepath = remotepath if remotepath is not None \
                          else os.path.basename(localpath)

        self.ftype = WQFile.TYPES[ftype]
        self.cache = WQFile.CACHE[cache]

    def add_to_task(self, task):
        """Add the file to a task.

        Parameters
        ----------
        task : `work_queue.Task`
            The task to add the file to.
        tag : str, optional
            The task tag.

        Notes
        -----
        If this file is an output file, `tag` is prepended to the local path
        name, then
        """
        #if self.ftype == WQFile.TYPES['output']:
        print(self.localpath)
        task.specify_file(self.localpath,
                          remote_name=self.remotepath,
                          type=self.ftype,
                          cache=self.cache)


class WQBuffer(object):
    """File to send to or receive from a remote worker.

    Parameters
    ----------
    buffer : str
        The string buffer to send to the remote task.
    remotepath : str, optional
        Where to place the file on the remote worker relative to cwd. Set to
        the basename of `localpath` by default (e.g. foo/bar.baz -> bar.baz).
    cache : bool, optional
        Whether to cache this file on the remote worker.

    Attributes
    ----------
    buffer : str
        The string buffer to send to the remote task.
    remotepath : str
        Where to place the file on the remote worker relative to remote cwd.
    cache : bool
        Whether to cache this file on the remote worker.

    Notes
    -----
    Buffers are most useful for task-specific data (e.g. hyperparameter values)
    and as such are always treated as non-caching input files.

    """

    def __init__(self, buffer, remotepath, cache=False):
        self.buffer = str(buffer)
        self.remotepath = str(remotepath)
        self.cache = WQFile.CACHE[cache]
        self.ftype = 'buffer'

    def add_to_task(self, task):
        """Add the buffer to a task.

        Parameters
        ----------
        task : `work_queue.Task`
            The task to add the file to.
        tag : str, optional
            The task tag.

        Notes
        -----
        `tag` is currently unused, included as a placeholder to match the
        signature of `shadho.managers.workqueue.WQFile.add_to_task`.
        """
        task.specify_buffer(self.buffer, self.remotepath, self.cache)
