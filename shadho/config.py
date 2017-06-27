# -*- coding: utf-8 -*-
"""Helper objects for configuring and using Work Queue.
"""
try:
    import configparser
except:
    import ConfigParser as configparser
import getpass
import json
import os

import work_queue


class LocalFileDoesNotExist(Exception):
    pass


class InvalidFileType(Exception):
    def __init__(self, ftype):
        msg = """
{} is not a valid file type for Work Queue files.
Please specify one of 'input' or 'output'.
""".format(ftype)
        super(InvalidFileType, self).__init__(msg)


class InvalidCacheSetting(Exception):
    def __init__(self, ftype):
        msg = """
{} is not a valid caching option.
Please specify one of True or False.
""".format(ftype)
        super(InvalidFileType, self).__init__(msg)


class SHADHOConfig():
    DEFAULTS = {
        'global': {
            'wrapper': 'shadho_run_task.py',
            'output': 'out.tar.gz',
            'resultfile': 'performance.json',
            'minval': 'loss'
        },
        'workqueue': {
            'port': '9123',
            'name': 'shadho_master',
            'exclusive': 'yes',
            'shutdown': 'yes',
            'catalog': 'no',
            'logfile': 'shadho_master.log',
            'debugfile': 'shadho_master.debug',
            'password': 'no'
        },
        'storage': {
            'type': 'json'
        }
    }

    def __init__(self, ignore_shadhorc=False):
        configfile = os.environ['SHADHORC'] if 'SHADHORC' in os.environ \
            else os.path.join(self._shadho_dir(), '.shadhorc')
        print(configfile)

        self.config = configparser.ConfigParser()
        if hasattr(self.config, 'read_dict'):
            # Python 3
            self.config.read_dict(SHADHOConfig.DEFAULTS)
        else:
            # Python 2
            for key, value in SHADHOConfig.DEFAULTS.iteritems():
                self.config.add_section(key)
                for k, v in value.iteritems():
                    self.config.set(key, k, v)

        if not ignore_shadhorc:
            with open(configfile, 'r') as f:
                self.config.read_file(f)

    def __getattr__(self, name):
        if self.config.has_section(name):
            return self.config[name]
        else:
            raise AttributeError

    def _shadho_dir(self):
        try:
            home = os.path.expanduser(os.environ['HOME'] if 'HOME' in os.environ
                                          else os.environ['USERPROFILE'])
        except KeyError:
            print('Error: Could not find home directory in environment')

        return home


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
        Path to the file after transferred to the Work Queue worker. If not
        supplied, defaults to the basename of localpath
        (e.g. "/foo/bar/file.txt" -> "file.txt").
    ftype : {'input', 'output', 'buffer'}, optional
        Whether the file is an input file (to send to a worker), an output file
        (to receive from a worker), or created from a string buffer.
    cache : {False, True}, optional
        Whether to cache the file on a Work Queue worker between tasks. Doing
        so can reduce the overhead of running multiple tasks on a worker by
        preserving files common to all tasks.

    Attributes
    ----------
    localpath : str
        Path to the local copy of the file.
    remotepath : str
        The name of the file on the remote worker.
    type : {'input', 'output', 'buffer'}
        Whether the file is a task input, task output, or created from a string
        buffer.
    cache : bool
        Whether to cache the file on the worker between tasks.

    Notes
    -----
    For more information on Work Queue file specifications, see the
    `CCTools documentation<http://ccl.cse.nd.edu/software/manuals/api/html/work__queue_8h.html#a8f9af7213ea271d3b58fe0f62ad160c0>`_.

    """

    TYPES = {
        'input': work_queue.WORK_QUEUE_INPUT,
        'output': work_queue.WORK_QUEUE_OUTPUT
    }

    CACHE = {
        True: work_queue.WORK_QUEUE_CACHE,
        False: work_queue.WORK_QUEUE_NOCACHE
    }

    def __init__(self, localpath, remotepath=None,
                 ftype='input', cache=False):
        # TODO: add check for localpath existence
        # TODO: add exception handling for invalid type
        # TODO: add exception handling for invalid caching flag
        # TODO: add handling for buffers (?)
        if os.path.isfile(localpath):
            self.localpath = localpath
        else:
            raise LocalFileDoesNotExist("{} does not exist".format(localpath))
        self.remotepath = remotepath if remotepath is not None \
            else os.path.basename(localpath)

        if ftype in WQFile.TYPES:
            self.type = WQFile.TYPES[ftype]
        else:
            raise InvalidFileType("{} is not a valid file type".format(ftype))

        if cache in WQFile.CACHE:
            self.cache = WQFile.CACHE[cache]
        else:
            raise InvalidCacheSetting("{} is not a valid cache flag".format(cache))

    def add_to_task(self, task, tag=''):
        """Add the file to a task.

        Parameters
        ----------
        task : work_queue.Task
            The task to add the file to.
        tag : {'', str}, optional
            Tag to prepend to localpath. This allows for output files to be
            save to a common temporary directory without clobbering each other.
            If empty, localpath is unchanged.

        Notes
        -----
        The reference for work_queue.Task.specify_file may be found in the Work
        Queue `documentation<http://ccl.cse.nd.edu/software/manuals/api/html/classwork__queue_1_1Task.html#a0a1f1922908f822ac8d70d3903919024>`_.

        """
        task.specify_file(str(''.join([tag, self.localpath])),
                          remote_name=str(self.remotepath),
                          type=self.type,
                          cache=self.cache
                          )
