#!/usr/bin/python

import collectd
import json
import urllib2

VERBOSE_LOGGING = False
# replace any underscore in metric name to dot, for backward compatibility it is set to false
# to enable it use in collectd config 'ReplaceUnderscore true'
REPLACE_UNDERSCORE = False

INSTANCE_TYPE_NAMENODE = 'namenode'
INSTANCE_TYPE_DATANODE = 'datanode'
INSTANCE_TYPE_HDFS_JOURNALNODE = 'hdfs_journalnode'
INSTANCE_TYPE_HBASE_MASTER = 'hbase_master'
INSTANCE_TYPE_HBASE_REGIONSERVER = 'hbase_regionserver'

CONFIGS = []


BEAN_PREFIXES = {
    INSTANCE_TYPE_NAMENODE: {
        'FSNamesystem': 'Hadoop:service=NameNode,name=FSNamesystemState',
        'GCPSScavenge': 'java.lang:type=GarbageCollector,name=PS Scavenge',
        'GCPSMarkSweep': 'java.lang:type=GarbageCollector,name=PS MarkSweep',
        'Threading': 'java.lang:type=Threading',
        'JvmMetrics': 'Hadoop:service=NameNode,name=JvmMetrics',
    },
    INSTANCE_TYPE_DATANODE: {
        'DatanodeActivity': 'Hadoop:service=DataNode,name=DataNodeActivity',
        'GCPSScavenge': 'java.lang:type=GarbageCollector,name=PS Scavenge',
        'GCPSMarkSweep': 'java.lang:type=GarbageCollector,name=PS MarkSweep',
        'Threading': 'java.lang:type=Threading',
        'JvmMetrics': 'Hadoop:service=DataNode,name=JvmMetrics',
    },
    INSTANCE_TYPE_HDFS_JOURNALNODE: {
        'GCPSScavenge': 'java.lang:type=GarbageCollector,name=PS Scavenge',
        'GCPSMarkSweep': 'java.lang:type=GarbageCollector,name=PS MarkSweep',
        'Threading': 'java.lang:type=Threading',
        'JvmMetrics': 'Hadoop:service=JournalNode,name=JvmMetrics',
    },
    INSTANCE_TYPE_HBASE_MASTER: {
        'MasterBalancer': 'Hadoop:service=HBase,name=Master,sub=Balancer',
        'MasterAssignmentManager': 'Hadoop:service=HBase,name=Master,sub=AssignmentManger',
        'GCPSScavenge': 'java.lang:type=GarbageCollector,name=PS Scavenge',
        'GCPSMarkSweep': 'java.lang:type=GarbageCollector,name=PS MarkSweep',
        'MasterServer': 'Hadoop:service=HBase,name=Master,sub=Server',
        'Threading': 'java.lang:type=Threading',
        'JvmMetrics': 'Hadoop:service=HBase,name=JvmMetrics',
    },
    INSTANCE_TYPE_HBASE_REGIONSERVER: {
        'Regions': 'Hadoop:service=HBase,name=RegionServer,sub=Regions',
        'Replication': 'Hadoop:service=HBase,name=RegionServer,sub=Replication',
        'WAL': 'Hadoop:service=HBase,name=RegionServer,sub=WAL',
        'Server': 'Hadoop:service=HBase,name=RegionServer,sub=Server',
        'GCPSScavenge': 'java.lang:type=GarbageCollector,name=PS Scavenge',
        'GCPSMarkSweep': 'java.lang:type=GarbageCollector,name=PS MarkSweep',
        'Threading': 'java.lang:type=Threading',
        'JvmMetrics': 'Hadoop:service=HBase,name=JvmMetrics',
    },
}


def configure_callback(conf):
    """Received configuration information"""
    host = None
    port = None
    instance = None
    instance_type = None
    verbose_logging = VERBOSE_LOGGING
    replace_underscore = REPLACE_UNDERSCORE

    for node in conf.children:
        if node.key == 'HDFSNamenodeHost':
            host = node.values[0]
            instance_type = INSTANCE_TYPE_NAMENODE
        elif node.key == 'HDFSDatanodeHost':
            host = node.values[0]
            instance_type = INSTANCE_TYPE_DATANODE
        elif node.key == 'HDFSJournalnodeHost':
            host = node.values[0]
            instance_type = INSTANCE_TYPE_HDFS_JOURNALNODE
        elif node.key == 'HbaseMasterHost':
            host = node.values[0]
            instance_type = INSTANCE_TYPE_HBASE_MASTER
        elif node.key == 'HbaseRegionserverHost':
            host = node.values[0]
            instance_type = INSTANCE_TYPE_HBASE_REGIONSERVER
        elif node.key == 'Port':
            port = node.values[0]
        elif node.key == 'Instance':
            instance = node.values[0]
        elif node.key == 'ReplaceUnderscore':
            replace_underscore = bool(node.values[0])
        elif node.key == 'Verbose':
            verbose_logging = bool(node.values[0])
        else:
            collectd.warning('hadoop plugin: Unknown config key: %s.' % node.key)

    if not host or not instance or not instance_type or not port:
        collectd.error('hadoop plugin error: *Host, Port, and Instance must be set.')
    else:
        config = {
            'host': host,
            'port': port,
            'instance': instance,
            'instance_type': instance_type,
            'verbose_logging': verbose_logging,
            'replace_underscore': replace_underscore
        }

        CONFIGS.append(config)

        log_verbose('Configured hadoop instance_type=%s with host=%s' % (instance_type, host), verbose_logging)


def get_jmx_beans(host, port):
    jmx_url = "http://{}:{}/jmx".format(host, port)

    try:
        beans = json.load(urllib2.urlopen(jmx_url, timeout=10))['beans']
        return beans

    except urllib2.URLError as e:
        collectd.error('hadoop plugin: Error connecting to %s - %r' % (jmx_url, e))

    return {}


def process_metrics(host, port, instance, instance_type, verbose_logging, replace_underscore=False):
    beans = get_jmx_beans(host, port)

    for bean in beans:
        for name, prefix in BEAN_PREFIXES[instance_type].iteritems():
            if bean['name'].startswith(prefix):
                for metric, value in bean.iteritems():

                    if replace_underscore:
                        metric = metric.replace('_', '.')

                    # special cases, unfortunately some metrics are booleans values as strings
                    # HBase is active master
                    # Hadoop out of sync
                    if metric in ['tag.isActiveMaster', 'tag.IsOutOfSync']:
                        if value == 'true':
                            value = True
                        else:
                            value = False
                    # Hadoop namenode state active/standby
                    if metric in ['State', 'tag.HAState']:
                        if value == 'active':
                            value = True
                        else:
                            value = False

                    # notice that this actally catches also bool as int
                    if isinstance(value, int) or isinstance(value, float):
                        dispatch_stat('gauge', '.'.join((name, metric)), value, instance, instance_type, verbose_logging)


def read_callback():
    """Parse stats response from Hadoop services"""

    for config in CONFIGS:
        log_verbose('Read callback called for instance: %s' % config['instance'], config['verbose_logging'])
        process_metrics(config['host'], config['port'], config['instance'], config['instance_type'], config['verbose_logging'], config['replace_underscore'])


def dispatch_stat(stat_type, name, value, instance, instance_type, verbose_logging):
    """Read a key from info response data and dispatch a value"""

    if value is None:
        collectd.warning('hadoop plugin: Value not found for %s' % name)
    else:
        plugin_instance = '.'.join((instance, instance_type))
        log_verbose('Sending value from %s [%s]: %s=%s' % (plugin_instance, stat_type, name, value), verbose_logging)

        val = collectd.Values(plugin='hadoop')
        val.type = stat_type
        val.type_instance = name
        val.values = [value]
        val.plugin_instance = plugin_instance
        # https://github.com/collectd/collectd/issues/716
        val.meta = {'0': True}
        val.dispatch()


def log_verbose(msg, verbose_logging):
    if verbose_logging:
        collectd.info('hadoop plugin [verbose]: %s' % msg)


collectd.register_config(configure_callback)
collectd.register_read(read_callback)
