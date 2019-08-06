from .local import LocalManager
from .workqueue import WQManager


def create_manager(manager_type='local', config=None, tmpdir=None):
    print(config.config)
    if manager_type == 'workqueue':
        return WQManager(
            config.param_file,
            config.output,
            config.result_file,
            config.optimize,
            tmpdir,
            name=config.workqueue.name,
            port=config.workqueue.port,
            shutdown=config.workqueue.shutdown,
            logfile=config.workqueue.logfile,
            debugfile=config.workqueue.debugfile
        )
    else:
        return LocalManager(config.optimize)
