

def newline_list_to_namespace(path) -> list:
    with open(path, 'r') as ns_file:
        data = ns_file.read()
        data = data.split('\n')
        data = list(filter(lambda n: n is not '', data))
        return data