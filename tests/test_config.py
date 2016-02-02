from collectdharness import MockConfig
import collectd

from hadoop import configure_callback
from hadoop import CONFIGS


def test_default_error(mocker):
    mocker.patch('collectd.error')

    global CONFIGS
    conf = MockConfig()

    configure_callback(conf)

    assert len(CONFIGS) == 0
    collectd.error.assert_called_once_with('hadoop plugin: Error Host, Port, Instance must be set.')


def test_set_namenode():
    global CONFIGS

    module_string = '''
HDFSNamenodeHost "example.com"
Port "9999"
Instance "myinstance"
'''

    conf = MockConfig(module_string)

    configure_callback(conf)

    assert len(CONFIGS) == 1

    config = CONFIGS[0]

    assert 'instance' in config
    assert config['instance'] == 'myinstance'

    assert 'host' in config
    assert config['host'] == 'example.com'

    assert 'port' in config
    assert config['port'] == '9999'

    assert 'instance_type' in config
    assert config['instance_type'] == 'namenode'
