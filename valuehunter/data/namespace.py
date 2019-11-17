
def from_tos_wl(path):
    with open(path, 'r') as ns_file:
        data = ns_file.read()
        data = data.split('\n')
        data = data[4:-1]
        out = [line.split(',')[0] for line in data]
        return out

def from_text_file(path):
    with open(path, 'r') as ns_file:
        data = ns_file.read()
        data = data.split('\n')
        data = list(filter(lambda n: n is not '', data))
        return data