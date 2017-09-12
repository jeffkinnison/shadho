"""
"""
import json
import os
import tarfile

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

    def __init__(self, param_file, out_file, results_file, opt_value, tmpdir,
                 name='shadho', port=9123, exclusive=True, shutdown=True,
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

        self.param_file = param_file
        self.out_file = out_file
        self.results_file = results_file
        self.opt_value = opt_value
        self.tmpdir = tmpdir

    def add_task(self, cmd, tag, params, files=None, resource=None, value=None):
        """Create a task for this manager.

        Parameters
        ----------
        cmd : str
            The command to run on the remote worker, e.g. ``echo hello`` or
            ``python script.py``.
        tag : str
            The tag to give this task.
        files : list of `WQFile` or `WQBuffer`, optional
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

        if files is None:
            files = []

        for f in files:
            if isinstance(f, tuple):
                f = WQFile(f[0], remotepath=f[1], ftype=f[2], cache=f[3])
            f.add_to_task(task)

        out = WQFile(os.path.join(self.tmpdir,
                                  '.'.join([tag, self.out_file])),
                     remotepath=self.out_file,
                     ftype='output',
                     cache=False)

        buff = WQBuffer(str(json.dumps(params)),
                        self.param_file,
                        cache=False)

        out.add_to_task(task)
        buff.add_to_task(task)

        if resource is not None:
            if resource == 'cores':
                task.specify_cores(value)
            else:
                task.specify_resource(resource, value)

        self.submit(task)

    def run_task(self):
        task = None
        while task is None:
            task = self.wait(timeout=10)
            if task is not None:
                if self.task_succeeded(task):
                    return self.success(task)
                else:
                    return self.failure(task)

    def task_succeeded(self, task):
        """Determine whether or not a task succeeded.

        Parameters
        ----------
        task : work_queue.Task
            The task to check.

        Returns
        -------
        True if the task succeeded, False otherwise.
        """
        return task is not None and \
            task.result == work_queue.WORK_QUEUE_RESULT_SUCCESS

    def success(self, task):
        """Handle Work Queue task success.

        Parameters
        ----------
        task : work_queue.Task
            The successful task with results to process.

        Returns
        -------
        result_id : str
            The id of the database entry representing this result.
        cc_id : str
            The id of the compute class that ran this result.
        loss : float
            The value being optimized.
        results : dict
            Other results returned by the task.
        """
        # Extract the result and compute class ids
        rid, ccid = str(task.tag).split('.')

        try:
            # Open the result tarfile and get the results file.
            outfile = '.'.join([task.tag, self.out_file])
            result = tarfile.open(os.path.join(self.tmpdir, outfile), 'r')
            resultstr = result.extractfile(self.results_file).read()
            result.close()
        except IOError:
            print("Error opening task {} result".format(rid))

        result = json.loads(resultstr.decode('utf-8'))
        loss = result[self.opt_value]
        return (rid, ccid, loss, result)

    def failure(self, task):
        """Handle Work Queue task failure.

        Parameters
        ----------
        task : work_queue.Task
            The failed task to process.

        Returns
        -------
        result_id : str
            The id of the database entry representing this result.
        cc_id : str
            The id of the compute class that ran this result.
        """
        print('Task {} failed with result {} and WQ status {}'
              .format(task.tag, task.result, task.return_status))
        print(task.output)

        rid, ccid = str(task.tag).split('.')
        return (rid, ccid)


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
