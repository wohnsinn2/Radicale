import time

class CacheDict(dict):
    def __init__(self, timeout, *args, **kwargs):
        self.timeout = float(timeout)
        super(CacheDict, self).__init__(*args, **kwargs)

    def __setitem__(self, name, value):
        tstamp = time.time()
        entry = {
            'value': value,
            'tstamp': tstamp,
        }
        super(CacheDict, self).__setitem__(name, entry)

    def __getitem__(self, name):
        cur_time = time.time()
        entry = super(CacheDict, self).__getitem__(name)
        if entry['tstamp'] < (cur_time - self.timeout):
            super(CacheDict, self).__delitem__(name)
            raise KeyError(name)
        return entry['value']
