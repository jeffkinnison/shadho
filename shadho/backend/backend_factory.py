from .jsondb import JSONBackend
#from .sqldb import SQLBackend


def create_backend(backend_type='json', config=None):
    if backend_type == 'sql':
        return SQLBackend()
    else:
        return JSONBackend()
