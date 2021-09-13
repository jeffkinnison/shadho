"""Work Queue wrapper for hardware-aware distributed task management.

Classes
-------
WQManager
    Work Queue master with additional task packaging logic.
WQFile
WQBuffer
    Work-Queue-conformant representations of files and buffers for task I/O.
"""
import json
import os
import sys
import tarfile

try:
    import work_queue as WORKQUEUE
except ImportError:
    print('Work Queue not found, installing.')
    try:
        import shadho.installers.workqueue
        shadho.installers.workqueue.main()
        import work_queue as WORKQUEUE
    except OSError:
        raise

from shadho.utils import ShadhoEncoder, ShadhoDecoder


class WQManager(WORKQUEUE.WorkQueue):
    """Work Queue master with utilities to generate conformant tasks.

    Parameters
    ----------
    param_file : str
        The name of the hyperparameter value file sent to the worker.
    out_file : str
        The name of the expected output file returned from the worker.
    results_file : str
        The name of the expected results file returned from the worker.
    opt_value : str
        The name of the value to optimize on in `results_file`.
    tmpdir : str
        Temporary directory used by SHADHO.
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

    Attributes
    ----------

    """

    def __init__(self, param_file, out_file, results_file, opt_value, tmpdir,
                 name='shadho', port=9123, shutdown=True,
                 logfile='shadho_wq.log', debugfile='shadho_wq.debug'):
        WORKQUEUE.cctools_debug_flags_set("all")
        WORKQUEUE.cctools_debug_config_file(debugfile)
        WORKQUEUE.cctools_debug_config_file_size(0)

        if os.environ['USER'] not in name:
            name += '-{}'.format(os.environ['USER'])

        super(WQManager, self).__init__(name=name,
                                        port=int(port),
                                        shutdown=shutdown)

        self.specify_log(logfile)

        self.param_file = param_file
        self.out_file = out_file
        self.results_file = results_file
        self.opt_value = opt_value
        self.tmpdir = tmpdir
        self.tasks_submitted = self.stats.tasks_submitted

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
        # Set up the task to run the specified command with its tag as the
        # trailing argument.
        task = WORKQUEUE.Task(' '.join([cmd, tag]))
        task.specify_tag(tag)

        # Set up the input and output file structure of the task. This
        # structure is preserved on the worker.
        if files is None:
            files = []

        for f in files:
            if isinstance(f, tuple):
                f = WQFile(f[0], remotepath=f[1], ftype=f[2], cache=f[3])
            f.add_to_task(task)

        # Set up the output file
        out = WQFile(os.path.join(self.tmpdir,
                                  '.'.join([tag, self.out_file])),
                     remotepath=self.out_file,
                     ftype='output',
                     cache=False)

        # Send the hyperparameters as a JSON string
        buff = WQBuffer(str(json.dumps(params, cls=ShadhoEncoder)),
                        self.param_file,
                        cache=False)

        out.add_to_task(task)
        buff.add_to_task(task)

        # Add information about the expected hardware resource
        if resource is not None:
            if resource == 'cores':
                task.specify_cores(value)
            elif resource == 'feature':
                task.specify_requirement(value)
            else:
                task.specify_resource(resource, value)

        # Submit the task
        self.submit(task)
        self.tasks_submitted = self.stats.tasks_submitted

    def run_task(self):
        """Await the return of a running task.

        Returns
        -------
        tag : str
            The task tag.
        loss : float
            The loss value. Only returned on success.
        results : dict
            Additional results returned by the objective function.
            Only returned on success.
        """
        task = None
        while task is None:
            # Wait for a task to return for 10s
            task = self.wait(timeout=10)

            # Handle task success or failure (no return if `task` is None)
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

        Notes
        -----
        The task succeeded if it was not None and Work Queue reported a
        successful return.
        """
        return task is not None and \
            task.result == WORKQUEUE.WORK_QUEUE_RESULT_SUCCESS

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
        try:
            # Open the result tarfile and get the results file.
            outfile = '.'.join([task.tag, self.out_file])
            result = tarfile.open(os.path.join(self.tmpdir, outfile), 'r')
            resultstr = result.extractfile(self.results_file).read()
            result.close()
        except IOError:
            print("Error opening task {} result".format(rid))

        result = json.loads(resultstr.decode('utf-8'), cls=ShadhoDecoder)
        if isinstance(result, list):
            loss = []
            for r in result:
                loss.append(r[self.opt_value])
                r['submit_time'] = task.submit_time
                r['start_time'] = task.execute_cmd_start
                r['finish_time'] = task.finish_time
        else:
            loss = result[self.opt_value]
            result['submit_time'] = task.submit_time
            result['start_time'] = task.execute_cmd_start
            result['finish_time'] = task.finish_time
        return (task.tag, loss, result)

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

        resub = (int(task.return_status) == 137)

        #rid, ccid = str(task.tag).split('.')
        return (task.tag, resub)


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
        'input': WORKQUEUE.WORK_QUEUE_INPUT,
        'output': WORKQUEUE.WORK_QUEUE_OUTPUT,
    }

    CACHE = {
        True: WORKQUEUE.WORK_QUEUE_CACHE,
        False: WORKQUEUE.WORK_QUEUE_NOCACHE
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
