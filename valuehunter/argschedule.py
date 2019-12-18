import json
from copy import deepcopy


class ArgSchedule(object):

    def __init__(self, json_path):
        self._schedule = []
        with open(json_path, 'r') as f:
            self._data = json.load(f)
        self._compile()
        self._feed = None
        self.reset()

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._feed)

    def __len__(self):
        return len(self._schedule)

    def _compile(self, keys=None, sequence=None):
        if sequence is None:
            sequence = []
        else:
            sequence = deepcopy(sequence)

        if keys is None:
            keys = [k for k in self._data]

        if len(keys) == 0:  # terminal
            self._schedule.append(sequence)
        else:  # key node
            keys = deepcopy(keys)
            key = keys.pop()
            vals = self._data[key]
            sequence.append(key)
            if len(vals) == 0:
                self._compile(keys, sequence)
            else:
                for val in vals:
                    s = deepcopy(sequence)
                    if isinstance(val, list):
                        for v in val:
                            s.append(str(v))
                    else:
                        s.append(str(val))

                    self._compile(keys, s)

    def reset(self):
        self._feed = iter(self._schedule)
