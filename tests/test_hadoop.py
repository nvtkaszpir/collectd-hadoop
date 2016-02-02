import mock

import collectd
from hadoop import process_metrics
from hadoop import dispatch_stat


def test_process_metrics_happy_path(mocker):
    # must be imported like this for mocker to work
    import hadoop

    mocker.patch('hadoop.get_jmx_beans', return_value=[{'name': 'java.lang:type=Threading', 'modelerType': 'com.banno.TestModeler', 'mymetric': 99, 'notvalidmetric': 'laksdjflsd'}])
    mocker.patch('hadoop.dispatch_stat')

    process_metrics('example.com', 9999, 'myinstance', 'namenode', True)

    hadoop.dispatch_stat.assert_called_once_with('gauge', '.'.join(('TestModeler', 'mymetric')), 99, 'myinstance', 'namenode', True)


def test_dispatch_stat_happy_path(mocker):
    value_mock = mock.Mock()
    mocker.patch('collectd.Values', return_value=value_mock)

    dispatch_stat('gauge', 'TestModeler.mymetric', 99, 'myinstance', 'namenode', True)

    assert value_mock.type == 'gauge'
    assert value_mock.type_instance == 'TestModeler.mymetric'
    assert value_mock.values == [99]
    assert value_mock.plugin_instance == 'myinstance.namenode'
    assert value_mock.meta == {'0': True}

    value_mock.dispatch.assert_called_once_with()


def test_dispatch_stat_no_value(mocker):
    mocker.patch('collectd.warning')
    mocker.patch('collectd.Values')

    dispatch_stat('gauge', 'doesntmatter', None, 'doesntmatter', 'doesntmatter', False)

    collectd.Values.assert_not_called()
    collectd.warning.assert_called_once_with('hadoop plugin: Value not found for doesntmatter')
