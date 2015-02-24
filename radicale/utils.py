import time
import weakref
from collections import namedtuple, Mapping, MutableMapping

# is_valid for container
# TODO autoprune to root
# TODO type for parent/root timeout/no timeout
# TODO method for setting/validating tag/property
# TODO timer for regular cleanup


class ValContainer(namedtuple('ValContainer', ['tstamp', 'value'])):
    def __new__(cls, value):
        tstamp = time.time()
        return super(ValContainer, cls).__new__(cls, tstamp, value)


class CacheDict(dict):
    def __init__(self, timeout=None, mapping=None, root=None):
        super(CacheDict, self).__init__()
        self._timeout = float(timeout) if timeout is not None else None
        real_root = root if root is not None else self
        self._root = weakref.ref(real_root)
        if mapping is not None:
            self.update(mapping)

    def __setitem__(self, name, value):
        if isinstance(value, Mapping):
            # create new CacheDict holding the actual values
            entry = CacheDict(None, value, self._root())
        else:
            entry = ValContainer(value)
        super(CacheDict, self).__setitem__(name, entry)

    def _get_entry(self, name):
        return super(CacheDict, self).__getitem__(name)

    def is_valid(self, entry):
        if isinstance(entry, ValContainer):
            cur_time = time.time()
            if self.timeout is None:
                return True
            else:
                return entry.tstamp > cur_time - self.timeout
        else:
            return True

    @property
    def timeout(self):
        return self._timeout or self._root()._timeout

    def __getitem__(self, name):
        entry = self._get_entry(name)

        if isinstance(entry, ValContainer):
            if self.is_valid(entry):
                return entry.value
            else:
                del self[name]
                raise KeyError(name)
        else:
            return entry

    def __contains__(self, name):
        return self.is_valid(self._get_entry(name))

    def __iter__(self):
        i = super(CacheDict, self).__iter__()
        g = (k for k in i if k in self)
        for k in g:
            yield k

    update = MutableMapping.update
    keys = MutableMapping.keys
    values = MutableMapping.values
    items = MutableMapping.items
    __ne__ = MutableMapping.__ne__

    def clean(self, timeout=None):
        raise NotImplemented

    def reset_time(self, name):
        raise NotImplemented

    def __del__(self):
        print("cachedict deleted.")
