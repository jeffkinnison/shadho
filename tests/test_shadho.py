import pytest

from shadho.shadho import Shadho

class TestShadho(object):
    def test_init(self):
        s = Shadho('echo "hello"', {'a': 6, 'b': 3654})

    def test_add_compute_class(self):
        pass

    def test_add_input_file(self):
        s = Shadho('echo "hello"', {})

    def test_add_output_file(self):
        pass

    def test_generate(self):
        s = Shadho('echo "hello"', {'a': 6, 'b': 3654})
        s.generate()

    def test_assign_to_ccs(self):
        s = Shadho('echo "hello"', {})

    def test_make_tasks(self):
        pass

    def test_success(self):
        pass

    def test_failure(self):
        pass

    def test_run(self):
        pass
