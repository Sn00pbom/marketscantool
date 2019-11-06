

class NameSpace:

    def __init__(self, vals=None):
        # TODO potentially change to dictionary
        if vals is None: vals = []
        self._vals = vals 

    @property
    def values(self):
        return self._vals

    @classmethod
    def from_tos_wl(cls, path):
        with open(path, 'r') as ns_file:
            data = ns_file.read()
            data = data.split('\n')
            data = data[4:-1]
            out = []
            for line in data:
                elements = line.split(',')
                out.append(elements[0])
            return NameSpace(out)
    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as ns_file:
            data = ns_file.read()
            data = data.split('\n')
            data = list(filter(lambda n: n is not '', data))
            return NameSpace(data)

