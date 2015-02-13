import time
from collections import namedtuple, Mapping


class ValContainer(namedtuple('ValContainer', ['tstamp', 'value'])):
    def __new__(cls, value):
        tstamp = time.time()
        return super(ValContainer, cls).__new__(cls, tstamp, value)


class CacheDict(dict):
    def __init__(self, timeout, mapping=None):
        if isinstance(timeout, CacheDict):
            self._timeout = timeout
        else:
            self._timeout = float(timeout)
        super(CacheDict, self).__init__()
        if mapping is not None:
            self.update(mapping)

    def __setitem__(self, name, value):
        if isinstance(value, Mapping):
            # create new CacheDict holding the actual values
            if isinstance(self._timeout, CacheDict):
                timeout = self._timeout
            else:
                timeout = self
            entry = CacheDict(timeout, value)
        else:
            entry = ValContainer(value)
        super(CacheDict, self).__setitem__(name, entry)

    def __getitem__(self, name):
        cur_time = time.time()
        entry = super(CacheDict, self).__getitem__(name)
        if isinstance(self._timeout, CacheDict):
            timeout = self._timeout._timeout
        else:
            timeout = self._timeout

        if isinstance(entry, ValContainer):
            if entry.tstamp < cur_time - timeout:
                del self[name]
                raise KeyError(name)
            return entry.value
        else:
            return entry

    def update(self, mapping):
        # TODO: use generator
        for k, v in mapping.items():
            self.__setitem__(k, v)

    def clean(self, timeout=None):
        raise NotImplemented

    def is_valid(self, name):
        raise NotImplemented

    def reset_time(self, name):
        raise NotImplemented
