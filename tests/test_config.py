from shadho.config import SHADHOConfig, WQFile, LocalFileDoesNotExist
from shadho.config import InvalidFileType, InvalidCacheSetting

import os

import work_queue

from nose.tools import assert_dict_equal, assert_equal, assert_not_equal
from nose.tools import raises


class TestSHADHOConfig(object):
    def test_init(self):
        # Test default initialization
        cfg = SHADHOConfig(ignore_shadhorc=True)
        defaults = {s: dict(cfg.config.items(s)) for s in cfg.config.sections()}
        print(defaults)
        assert_dict_equal(defaults,
                          SHADHOConfig.DEFAULTS,
                          msg='Default values not used')

        # Test reading from .shadhorc
        os.environ['SHADHORC'] = os.path.abspath(
                                    os.path.join('.', 'tests', '.shadhorc')
                                 )
        cfg = SHADHOConfig()
        assert_not_equal(cfg.config.get('workqueue', 'port'),
                         SHADHOConfig.DEFAULTS['workqueue']['port'],
                         msg='New port not set')
        del os.environ['SHADHORC']

    def test_shadhodir(self):
        home = os.getenv('HOME')
        if home is None:
            home = os.path.expanduser('~')
            if home == '~':
                home = os.getenv('USERPROFILE')

        # Test searching for $HOME directory (Unix/Linux/OS X)
        pop = False
        if not 'HOME' in os.environ:
            os.environ['HOME'] = home
            pop = True
        cfg = SHADHOConfig()
        d = cfg._shadho_dir()
        assert_equal(d, home, msg='')
        if pop:
            del os.environ['HOME']

        # Test searching for %USERPROFILE% (Windows)
        pop = False
        if not 'USERPROFILE' in os.environ:
            os.environ['USERPROFILE'] = os.path.expanduser('~')
            pop = True
        nix_home = os.getenv('HOME')
        if nix_home is not None:
            del os.environ['HOME']
        cfg = SHADHOConfig()
        d = cfg._shadho_dir()
        assert_equal(d, home, msg='')
        if nix_home is not None:
            os.environ['HOME'] = home
        if pop:
            del os.environ['USERPROFILE']


class TestWQFile(object):
    @raises(LocalFileDoesNotExist, InvalidFileType, InvalidCacheSetting)
    def test_init(self):
        # Test default parameters
        wqf = WQFile('tests/.shadhorc')
        assert_equal(wqf.localpath,
                     'tests/.shadhorc',
                     msg='local filepath not set')
        assert_equal(wqf.remotepath,
                     '.shadhorc',
                     msg='default remotepath not set to localpath basename')
        assert_equal(wqf.type,
                     work_queue.WORK_QUEUE_INPUT,
                     msg='default type is not work_queue.WORK_QUEUE_INPUT')
        assert_equal(wqf.cache,
                     work_queue.WORK_QUEUE_NOCACHE,
                     msg='caching not disabled by default')

        # Test setting parameters
        wqf = WQFile('tests/.shadhorc',
                     remotepath='tests/.shadhorc',
                     ftype='output',
                     cache=True)
        assert_equal(wqf.localpath,
                     'tests/.shadhorc',
                     msg='local filepath not set')
        assert_equal(wqf.remotepath,
                     'tests/.shadhorc',
                     msg='remotepath not set to supplied value')
        assert_equal(wqf.type,
                     work_queue.WORK_QUEUE_OUTPUT,
                     msg='type not set to work_queue.WORK_QUEUE_OUTPUT')
        assert_equal(wqf.cache,
                     work_queue.WORK_QUEUE_CACHE,
                     msg='caching not enabled')

        # Test finding invalid file
        wqf = WQFile('/foo/bar.txt')

        # Test using invalid type
        wqf = WQFile('tests/.shadhorc',
                     ftype='kjfghlsidfhg'
                    )

        # Test using invalid cache setting
        wqf = WQFile('tests/.shadhorc',
                     cache=12
                    )
