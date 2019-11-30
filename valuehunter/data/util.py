from pandas import Series
from numpy import ndarray

def newline_list_to_namespace(path) -> list:
    with open(path, 'r') as ns_file:
        data = ns_file.read()
        data = data.split('\n')
        data = list(filter(lambda n: n is not '', data))
        return data

def weighted_average(l, w):
    valid = [list, ndarray, Series]
    if type(l) is list and type(w) is list:
        w_sum = 0
        for l, w in zip(l, w):
            w_sum += l * w
        return w_sum/sum(w)

    else:
        raise ValueError('Not valid types. Valid types include {}'.format(valid))
