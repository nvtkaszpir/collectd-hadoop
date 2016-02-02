#! /usr/bin/python

import collectd
import json
import urllib2

VERBOSE_LOGGING = False

INSTANCE_TYPE_NAMENODE = 'namenode'

CONFIGS = []


BEANS = {
    INSTANCE_TYPE_NAMENODE: [
        'Hadoop:service=NameNode,name=FSNamesystemState',
        'java.lang:type=OperatingSystem',
        'java.lang:type=Threading',
        'Hadoop:service=NameNode,name=JvmMetrics',
    ],
}


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


def process_metrics(host, port, instance, instance_type, verbose_logging):
    jmx_url = "http://{}:{}/jmx".format(host, port)

    try:
        beans = json.load(urllib2.urlopen(jmx_url, timeout=10))['beans']

        for bean in beans:
            if bean['name'] in BEANS[instance_type]:
                name = bean['modelerType'].split('.')[-1]
                for key, value in bean.iteritems():
                    if isinstance(value, int):
                        dispatch_stat('gauge', '.'.join((name, key)), value, instance, instance_type, verbose_logging)

    except urllib2.URLError as e:
        collectd.error('hadoop plugin: Error connecting to %s - %r' % (jmx_url, e))


def read_callback():
    """Parse stats response from Hadoop services"""

    for config in CONFIGS:
        log_verbose('Read callback called for instance: %s' % config['instance'], config['verbose_logging'])
        process_metrics(config['host'], config['port'], config['instance'], config['instance_type'], config['verbose_logging'])


def dispatch_stat(type, name, value, instance, instance_type, verbose_logging):
    """Read a key from info response data and dispatch a value"""

    if value is None:
        collectd.warning('hadoop plugin: Value not found for %s' % name)
    else:
        log_verbose('Sending value[%s]: %s=%s' % (type, name, value), verbose_logging)

        val = collectd.Values(plugin='hadoop')
        val.type = type
        val.type_instance = name
        val.values = [value]
        val.plugin_instance = '.'.join((instance, instance_type))
        # https://github.com/collectd/collectd/issues/716
        val.meta = {'0': True}
        val.dispatch()


def log_verbose(msg, verbose_logging):
    if verbose_logging:
        collectd.info('hadoop plugin [verbose]: %s' % msg)


collectd.register_config(configure_callback)
collectd.register_read(read_callback)
