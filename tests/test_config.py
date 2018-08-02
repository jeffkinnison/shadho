import copy
import os

import pytest

from shadho.config import ShadhoConfig, ConfigGroup, ShadhorcDoesNotExistError


class TestShadhoConfig(object):
    def test_init(self):
        dummyrc = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), '.shadhorc'))

        # Test the default configuration.
        cfg = ShadhoConfig(use_defaults=True)
        assert cfg.config == ShadhoConfig.DEFAULTS

        defaults = copy.deepcopy(ShadhoConfig.DEFAULTS)
        defaults['workqueue']['port'] = 9123

        # Test loading from a dummy .shadhorc file using the SHADHORC
        # environment variable.
        os.environ['SHADHORC'] = dummyrc
        cfg = ShadhoConfig()
        assert cfg.workqueue.port == 9123
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
        assert cfg.workqueue.port == 9123
        assert cfg.config == defaults
        del os.environ['HOME']

        os.environ['USERPROFILE'] = os.path.dirname(dummyrc)
        cfg = ShadhoConfig()
        assert cfg.workqueue.port == 9123
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

    def test_save_config(self, tmpdir):
        tmpdir = str(tmpdir)
        cfg = ShadhoConfig()
        cfg.save_config(tmpdir)


class TestConfigGroup(object):
    def test_init(self):
        # Initialize with an empty dictionary
        g = ConfigGroup()
        assert g.data == {}

        # Initialize with a simple dictionary passed to data
        correct1 = {'a': 1, 'b': 'foo', 'c': 0.16854}
        g = ConfigGroup(data=copy.deepcopy(correct1))
        assert g.data == correct1

        # Initialize with a simple dictionary passed to data
        correct2 = {'d': 'bar', 'e': 65.68473, 'f': 8675}
        g = ConfigGroup(**copy.deepcopy(correct2))
        assert g.data == correct2

        # Initialize with a simple dictionary passed to data
        correct3 = copy.deepcopy(correct1)
        correct3.update(correct2)
        g = ConfigGroup(data=copy.deepcopy(correct1),
                        **copy.deepcopy(correct2))
        assert g.data == correct3
