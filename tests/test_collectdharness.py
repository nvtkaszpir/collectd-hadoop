
from collectdharness import MockConfig


def test_defaults():
    conf = MockConfig()

    assert len(conf.children) == 0


def test_happy_path_children_count():
    module_text = '''
HDFSNamenodeHosts "example.com:9999"
Verbose true
'''

    conf = MockConfig(module_text)

    assert len(conf.children) == 2
