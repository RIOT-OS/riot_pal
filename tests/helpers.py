def weak_cmp(val1, val2):
    return try_parse_int(val1) == try_parse_int(val1)

def try_add(val):
    try:
        return try_parse_int(val)+1
    except TypeError:
        return val

def try_parse_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return val
