"""
"""
import os

import work_queue


class WQManager(work_queue.WorkQueue):
    def __init__(self, name='shadho', port=9123, exclusive=True, shudown=True,
                 catalog=False, logfile='shadho_wq.log',
                 debugfile='shadho_wq.debug'):
        work_queue.cctools_debug_flags_set("all")
        work_queue.cctools_debug_config_file(self.wq_config['debug'])
        work_queue.cctools_debug_config_file_size(0)

        super(WQManager, self).__init__(name=name,
                                        port=port,
                                        exclusive=exclusive,
                                        shutdown=shutdown,
                                        catalog=catalog)

        self.specify_log(logfile)

    def make_task(self, cmd, tag, files):
        task = work_queue.Task(cmd)
        task.specify_tag(tag)

        for f in files:
            f.add_to_task(task)

        return task


class WQFile(object):
    """
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
        if os.path.isfile(localpath):
            self.localpath = localpath
        else:
            raise IOError("{} does not exist.".format(localpath))

        self.remotepath = remotepath if remotepath is not None \
                          else os.path.basename(localpath)

        self.ftype = WQFile.TYPES[type]
        self.cache = WQFile.CACHE[cache]

    def add_to_task(self, task, tag=''):
        task.specify_file(str(''.join([tag, self.localpath]))
                          remote_name=self.remotepath,
                          type=self.type,
                          cache=self.cache)


class WQBuffer(object):
    def __init__(self, buffer, remotepath, cache=False):
        self.buffer = str(buffer)
        self.remotepath = remotepath
        self.cache = WQFile.CACHE[cache]

    def add_to_task(task):
        task.specify_buffer(self.buffer, self.remotepathm self.cache)
