'''
This is a mock of the collectd module that is present in
a running collectd environment

It is only used to satisfy method calls and callbacks. Tests
may mock these calls to capture input and outputs from them.
'''


class Value(object):

    def __setattr__(self, name, value):
        pass

    def dispatch(self):
        pass


def warning(*args, **kwargs):
    print('warning', args)


def error(*args, **kwargs):
    print('error', args)


def info(*args, **kwargs):
    print('info', args)


def register_config(*args, **kwargs):
    pass


def register_read(*args, **kwargs):
    pass


def Values(*args, **kwargs):
    return Value()
