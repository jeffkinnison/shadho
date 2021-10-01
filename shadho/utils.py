import json
import re

import numpy as np


class ShadhoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.ndarray, np.generic)):
            return {
                '__data': obj.tolist(),
                '__dtype': str(obj.dtype),
            }
        else:
            return super(ShadhoEncoder, self).default(obj)


class ShadhoDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(ShadhoDecoder, self).__init__(
            *args, object_hook=self.object_hook, **kwargs)

    def object_hook(self, obj):
        if isinstance(obj, dict) and sorted(obj.keys()) == ['__data', '__dtype']:
            if isinstance(obj['__data'], list):
                arr = np.array(obj['__data']).astype(obj['__dtype'])
            else:
                arr = np.dtype(obj['__dtype']).type(obj['__data'])
            return arr
        else:
            return obj
