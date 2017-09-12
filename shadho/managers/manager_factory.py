from .local import LocalManager
from .workqueue import WQManager


def create_manager(manager_type='local', config=None):
    print(config.config)
    if manager_type == 'workqueue':
        return WQManager(
            config['global']['param_file'],
            config['global']['output'],
            config['global']['result_file'],
            config['global']['optimize'],
            name=config['workqueue']['name'],
            port=config['workqueue']['port'],
            exclusive=config['workqueue']['exclusive'],
            shutdown=config['workqueue']['shutdown'],
            logfile=config['workqueue']['logfile'],
            debugfile=config['workqueue']['debugfile']
        )
    else:
        return LocalManager(config['global']['optimize'])
