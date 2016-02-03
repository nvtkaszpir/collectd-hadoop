# collectd-hadoop

A [collectd](http://collectd.org) plugin for [Hadoop](https://hadoop.apache.org/)

It collects data from the http `/jmx` endpoints for:

* [x] HDFS NameNodes
* [x] HDFS DataNodes
* [ ] HDFS JournalNodes
* [ ] HDFS Namenode ZKFCs

* [x] Hbase Masters
* [ ] Hbase Regionservers

These are currently all we use, so if you would like to monitor other pieces, pull requests
are greatly appreciated.

## Install

1. Place `hadoop.py` in /opt/collectd/lib/collectd/plugins/python (assuming you have collectd installed to /opt/collectd).
2. Configure the plugin (see below).
3. Restart collectd.

Configuration
-------------
 * See `hadoop.conf`

Requirements
------------
 * collectd 4.9+
 * Hadoop 2.7.1
 * HBASE 1.1.2

## Testing

We have stubbed out a few things to aid in development of this plugin. Functional tests are run
inside `Docker` with the help of `docker-compose`

```bash
$ docker-compose run tests
...
collected 3 items

tests/test_collectdharness.py::test_defaults PASSED
tests/test_collectdharness.py::test_happy_path_children_count PASSED
tests/test_config.py::test_defaults PASSED
...
```

`docker-compose` respects exit codes, so if the tests fail, the status code will be non-zero. Super helpful for
build environments.
