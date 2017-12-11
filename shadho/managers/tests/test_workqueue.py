import pytest

from shadho.managers.workqueue import WQManager, WQFile, WQBuffer

import gc
import os
import shutil
import tempfile

import work_queue


class TestWQManager(object):
    def test_init(self):
        tmpdir = tempfile.mkdtemp()

        # Test the default initialization
        wq = WQManager('hyperparameters.json',
                       'out.tar.gz',
                       'performance.json',
                       'loss',
                       tmpdir)
        assert isinstance(wq, work_queue.WorkQueue)
        assert wq._shutdown is True
        # assert os.path.isfile('wq_shadho.log')
        # assert os.path.isfile('wq_shadho.debug')

        wq = None
        gc.collect()

        # Test setting the values that can currently be checked from Python
        wq = WQManager('hyperparameters.json',
                       'out.tar.gz',
                       'performance.json',
                       'loss',
                       tmpdir,
                       port=9124,
                       shutdown=False,
                       logfile='dummy.log',
                       debugfile='dummy.debug')
        assert isinstance(wq, work_queue.WorkQueue)
        assert wq._shutdown is False
        # assert os.path.isfile('dummy.log')
        # assert os.path.isfile('dummy.debug')

        #del wq

        os.remove('shadho_wq.log')
        os.remove('shadho_wq.debug')
        os.remove('dummy.log')
        os.remove('dummy.debug')
        shutil.rmtree(tmpdir)

    def test_add_task(self):
        tmpdir = tempfile.mkdtemp()
        # This needs to be expanded in the future, when work_queue module
        # object attributes can be retrieved from Python.
        # Test that this returns a work_queue.Task instance.
        wq = WQManager('hyperparameters.json',
                       'out.tar.gz',
                       'performance.json',
                       'loss',
                       tmpdir,
                       port=9125)

        wq.add_task('echo hello', 'totally_unique_tag', {})
        assert wq.tasks_submitted == 1

        os.remove('shadho_wq.log')
        os.remove('shadho_wq.debug')
        shutil.rmtree(tmpdir)

class TestWQFile(object):
    def test_init(self):
        open('foo.bar', 'a').close()
        os.mkdir('foo')
        open(os.path.join('foo', 'bar.baz'), 'a').close()

        # Test default initialization
        f = WQFile('foo.bar')
        assert f.localpath == 'foo.bar'
        assert f.remotepath == 'foo.bar'
        assert f.ftype == WQFile.TYPES['input']
        assert f.cache == WQFile.CACHE[True]

        # Test default with path with subdirectories
        f = WQFile('foo/bar.baz')
        assert f.localpath == 'foo/bar.baz'
        assert f.remotepath == 'bar.baz'
        assert f.ftype == WQFile.TYPES['input']
        assert f.cache == WQFile.CACHE[True]

        # Test explicitly setting remotepath, ftype, and cache
        f = WQFile('foo.bar', remotepath='baz', ftype='output', cache=False)
        assert f.localpath == 'foo.bar'
        assert f.remotepath == 'baz'
        assert f.ftype == WQFile.TYPES['output']
        assert f.cache == WQFile.CACHE[False]

        # Test setting ftype and cache to invalid values
        with pytest.raises(KeyError):
            WQFile('foo.bar', ftype='baz')

        with pytest.raises(KeyError):
            WQFile('foo.bar', cache='baz')

        os.remove('foo.bar')
        os.remove(os.path.join('foo', 'bar.baz'))
        os.rmdir('foo')

        # Test using a file that does not exist
        # Should work for output files, but not for input files
        with pytest.raises(IOError):
            WQFile('foo.bar')

        f = WQFile('foo.bar', remotepath='baz', ftype='output', cache=False)
        assert f.localpath == 'foo.bar'
        assert f.remotepath == 'baz'
        assert f.ftype == WQFile.TYPES['output']
        assert f.cache == WQFile.CACHE[False]

    def test_add_to_task(self):
        # Cannot test until API access to the input_files and output_files
        # fields are given.
        pass


class TestWQBuffer(object):
    def test_init(self):
        f = WQBuffer('foo', 'bar.baz')
        assert f.buffer == 'foo'
        assert f.remotepath == 'bar.baz'
        assert f.cache == WQFile.CACHE[False]

        f = WQBuffer(12, 392847, cache=True)
        assert f.buffer == '12'
        assert f.remotepath == '392847'
        assert f.cache == WQFile.CACHE[True]

        with pytest.raises(KeyError):
            WQBuffer('foo', 'bar.baz', None)

    def test_add_to_task(self):
        # Cannot test until API access to the input_files and output_files
        # fields are given.
        pass
