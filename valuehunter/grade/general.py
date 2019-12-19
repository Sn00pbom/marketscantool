

def hi_thresh(series, factor) -> float:
    return series.max() * factor


def lo_thresh(series, factor) -> float:
    return series.min() * factor


def value_chain(vals, istart: int) -> int:
    i1 = istart
    i2 = istart + 1
    direction = None
    chain = 0
    while i2 < len(vals):
        a = vals[i1]
        b = vals[i2]
        if direction is None:
            if a > b:
                direction = 'up'
                chain += 1
            elif b > a:
                direction = 'down'
                chain *= -1
                chain -= 1
            else:
                chain += 1
        elif direction is 'up' and a >= b:
            chain += 1
        elif direction is 'down' and a <= b:
            chain -= 1
        else:
            return chain

        i1 += 1
        i2 += 1
    return chain
