#! /usr/bin/python

import collectd
import json
import urllib2

PREFIX = "hadoop"
VERBOSE_LOGGING = False

INSTANCE_TYPE_NAMENODE = 'namenode'

CONFIGS = []


def configure_callback(conf):
    """Received configuration information"""
    host = None
    port = None
    instance = None
    instance_type = None
    verbose_logging = VERBOSE_LOGGING

    for node in conf.children:
        if node.key == 'HDFSNamenodeHost':
            host = node.values[0]
            instance_type = INSTANCE_TYPE_NAMENODE
        elif node.key == 'Port':
            port = node.values[0]
        elif node.key == 'Instance':
            instance = node.values[0]
        elif node.key == 'Verbose':
            verbose_logging = bool(node.values[0])
        else:
            collectd.warning('hadoop plugin: Unknown config key: %s.' % node.key)

    if not host and not instance and not instance_type and not port:
        collectd.error('hadoop plugin: Error Host, Port, Instance must be set.')
    else:
        config = {
            'host': host,
            'port': port,
            'instance': instance,
            'instance_type': instance_type,
            'verbose_logging': verbose_logging
        }

        CONFIGS.append(config)

        log_verbose('Configured hadoop instance_type=%s with host=%s' % (instance_type, host), verbose_logging)


def read_callback():
    """Parse stats response from Hadoop services"""

    config = CONFIG

    log_verbose('Read callback called for instance: %s' % config['instance'], config['verbose_logging'])
    try:
        metrics = json.load(urllib2.urlopen(config['metrics_url'], timeout=10))

        for group in ['gauges', 'histograms', 'meters', 'timers', 'counters']:
            for name, values in metrics.get(group, {}).items():
                for metric, value in values.items():
                    if not isinstance(value, basestring):
                        dispatch_stat('gauge', '.'.join((name, metric)), value, config['instance'], config['verbose_logging'])
    except urllib2.URLError as e:
        collectd.error('hadoop plugin: Error connecting to %s - %r' % (config['metrics_url'], e))


# def dispatch_stat(type, name, value, instance, verbose_logging):
#     """Read a key from info response data and dispatch a value"""
#     if value is None:
#         collectd.warning('hadoop plugin: Value not found for %s' % name)
#         return

#     log_verbose('Sending value[%s]: %s=%s' % (type, name, value), verbose_logging)

#     val = collectd.Values(plugin='hadoop')
#     val.type = type
#     val.type_instance = name
#     val.values = [value]
#     # https://github.com/collectd/collectd/issues/716
#     val.plugin_instance = instance
#     val.meta = {'0': True}
#     val.dispatch()


def log_verbose(msg, verbose_logging):
    if not verbose_logging:
        return
    collectd.info('hadoop plugin [verbose]: %s' % msg)


collectd.register_config(configure_callback)
collectd.register_read(read_callback)
