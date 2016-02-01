'''
This is a mock of the collectd module that is present in
a running collectd environment

It is only used to satisfy method calls and callbacks. Tests
may mock these calls to capture input and outputs from them.
'''


def warning(*args, **kwargs):
    pass


def error(*args, **kwargs):
    pass


def register_config(*args, **kwargs):
    pass


def register_read(*args, **kwargs):
    pass
