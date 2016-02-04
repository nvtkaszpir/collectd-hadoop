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
    collectd.error.assert_called_once_with('hadoop plugin error: *Host, Port, and Instance must be set.')


def assert_config(module_string, host, port, instance, instance_type):
    conf = MockConfig(module_string)

    configure_callback(conf)

    assert len(CONFIGS) == 1

    config = CONFIGS[0]

    assert 'instance' in config
    assert config['instance'] == instance

    assert 'host' in config
    assert config['host'] == host

    assert 'port' in config
    assert config['port'] == port

    assert 'instance_type' in config
    assert config['instance_type'] == instance_type


def test_set_namenode():
    global CONFIGS
    # clear because it is global...
    del CONFIGS[:]

    module_string = '''
HDFSNamenodeHost "example.com"
Port "9999"
Instance "myinstance"
'''

    assert_config(module_string, 'example.com', '9999', 'myinstance', 'namenode')


def test_set_datanode():
    global CONFIGS
    # clear because it is global...
    del CONFIGS[:]

    module_string = '''
HDFSDatanodeHost "example.com"
Port "9999"
Instance "myinstance"
'''

    assert_config(module_string, 'example.com', '9999', 'myinstance', 'datanode')


def test_set_hdfs_journalnode():
    global CONFIGS
    # clear because it is global...
    del CONFIGS[:]

    module_string = '''
HDFSJournalnodeHost "example.com"
Port "9999"
Instance "myinstance"
'''

    assert_config(module_string, 'example.com', '9999', 'myinstance', 'hdfs_journalnode')


def test_set_hbase_master():
    global CONFIGS
    # clear because it is global...
    del CONFIGS[:]

    module_string = '''
HbaseMasterHost "example.com"
Port "9999"
Instance "myinstance"
'''

    assert_config(module_string, 'example.com', '9999', 'myinstance', 'hbase_master')


def test_set_hbase_regionserver():
    global CONFIGS
    # clear because it is global...
    del CONFIGS[:]

    module_string = '''
HbaseRegionserverHost "example.com"
Port "9999"
Instance "myinstance"
'''

    assert_config(module_string, 'example.com', '9999', 'myinstance', 'hbase_regionserver')
