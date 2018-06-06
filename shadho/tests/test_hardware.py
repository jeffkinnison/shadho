import pytest

from shadho.hardware import ComputeClass


class TestComputeClass(object):
    def test_init(self):
        cc = ComputeClass("class_name", "resource", 1, 100)

        assert cc.name == "class_name"
        assert cc.resource == "resource"
        assert cc.value == 1
        assert cc.current_tasks == 100

        assert cc.model_group.models == {}
        assert cc.model_group.model_ids == []

    def test_generate(self):
        pass

    def test_add_model(self):
        pass

    def test_remove_model(self):
        pass
