import copy
import os

import pytest

from shadho.config import ShadhoConfig, ShadhorcDoesNotExistError


class TestShadhoConfig(object):
    def test_init(self):
        dummyrc = os.path.abspath(
                    os.path.join('.', 'shadho', 'tests', '.shadhorc'))

        defaults = copy.deepcopy(ShadhoConfig.DEFAULTS)
        defaults['workqueue']['port'] = 9123

        # Test the default configuration.
        cfg = ShadhoConfig(use_defaults=True)
        assert cfg.config == ShadhoConfig.DEFAULTS

        # Test loading from a dummy .shadhorc file using the SHADHORC
        # environment variable.
        os.environ['SHADHORC'] = dummyrc
        cfg = ShadhoConfig()
        assert cfg.config['workqueue']['port'] == 9123
        assert cfg.config == defaults
        del os.environ['SHADHORC']

        home = os.getenv('HOME')
        userprofile = os.getenv('USERPROFILE')

        if home is not None:
            del os.environ['HOME']
        if userprofile is not None:
            del os.environ['USERPROFILE']

        os.environ['HOME'] = os.path.dirname(dummyrc)
        cfg = ShadhoConfig()
        assert cfg.config['workqueue']['port'] == 9123
        assert cfg.config == defaults
        del os.environ['HOME']

        os.environ['USERPROFILE'] = os.path.dirname(dummyrc)
        cfg = ShadhoConfig()
        assert cfg.config['workqueue']['port'] == 9123
        assert cfg.config == defaults
        del os.environ['USERPROFILE']

        with pytest.raises(ShadhorcDoesNotExistError):
            cfg = ShadhoConfig()

        fakerc = os.path.abspath(os.path.join('foo', 'bar', 'baz'))
        os.environ['SHADHORC'] = fakerc
        with pytest.raises(ShadhorcDoesNotExistError):
            cfg = ShadhoConfig()
        del os.environ['SHADHORC']

        os.environ['HOME'] = fakerc
        with pytest.raises(ShadhorcDoesNotExistError):
            cfg = ShadhoConfig()
        del os.environ['HOME']

        os.environ['USERPROFILE'] = fakerc
        with pytest.raises(ShadhorcDoesNotExistError):
            cfg = ShadhoConfig()
        del os.environ['USERPROFILE']

        if home is not None:
            os.environ['HOME'] = home

        if userprofile is not None:
            os.environ['USERPROFILE'] = userprofile
