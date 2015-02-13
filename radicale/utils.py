import time


class ValContainer(dict):
    def __init__(self, value):
        tstamp = time.time()
        super(ValContainer, self).__init__()
        self['tstamp'] = tstamp
        self['value'] = value

class CacheDict(dict):
    def __init__(self, timeout, mapping=None, *args, **kwargs):
        self._timeout = float(timeout)
        super(CacheDict, self).__init__(*args, **kwargs)
        if mapping is not None:
            self.update(mapping)

    def __setitem__(self, name, value):
        if issubclass(type(value), dict):
            # create new CacheDict holding the actual values
            entry = CacheDict(self._timeout, value)
        else:
            entry = ValContainer(value)
        super(CacheDict, self).__setitem__(name, entry)

    def __getitem__(self, name):
        cur_time = time.time()
        entry = super(CacheDict, self).__getitem__(name)
        if issubclass(type(entry), ValContainer):
            if (entry['tstamp'] < (cur_time - self._timeout)):
                super(CacheDict, self).__delitem__(name)
                raise KeyError(name)
            return entry['value']
        else:
            return entry

    def update(self, mapping):
        # TODO: use generator
        for (k,v) in mapping.items():
            self.__setitem__(k, v)

    def clean(self,timeout=None):
        raise NotImplemented

    def is_valid(self, name):
        raise NotImplemented

    def reset_time(self, name):
        raise NotImplemented
