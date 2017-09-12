from .local import LocalManager
from .work_queue import WQManager


def create_manager(manager_type='local', config=None):
    if manager_type == 'workqueue':
        return WQManager(
            name=config['workqueue']['name'],
            port=config['workqueue']['port'],
            exclusive=config['workqueue']['exclusive'],
            shutdown=config['workqueue']['shutdown'],
            logfile=config['workqueue']['logfile'],
            debugfile=config['workqueue']['debugfile']
        )
    else:
        return LocalManager()
