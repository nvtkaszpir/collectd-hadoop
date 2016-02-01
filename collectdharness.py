

class MockNode(object):

    def __init__(self, node_string):
        self._node_string = node_string

    @property
    def key(self):
        return self._node_string.split()[0]

    @property
    def values(self):
        # probably need a better way to 'eval' strings in quotes
        return self._node_string.replace('"', '').split()[1:]


class MockConfig(object):

    def __init__(self, config_string=None):
        self._config_string = config_string

    @property
    def children(self):
        children = []

        if self._config_string:
            for row in self._config_string.strip().split('\n'):
                children.append(MockNode(row))

        return children
