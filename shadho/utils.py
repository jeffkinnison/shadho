import json

import numpy as np


class ShadhoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return {
                '__data': list(obj.ravel()),
                '__dtype': str(obj.dtype),
                '__shape': obj.shape
            }
        else:
            return super(ShadhoEncoder, self).default(obj)


class ShadhoDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(ShadhoDecoder, self).__init__(
            *args, object_hook=self.object_hook, **kwargs)

    def object_hook(self, obj):
        if isinstance(obj, dict) and sorted(obj.keys()) == ['__data', '__dtype', '__shape']:
            arr = np.array(obj['__data']).astype(obj['__dtype']).reshape(obj['__shape'])
            return arr
        else:
            return obj
