# Dictionary Add
def dictionary_list_add(d: dict, k, e):
    if k not in d:
        d[k] = []
    d[k].append(e)


def dictionary_list_remove(d:dict, k, e):
    if k not in d:
        return
    if e not in d[k]:
        return
    d[k].remove(e)
    if len(d[k]) <= 0:
        d.pop(k)


def hash_string(string: str) -> int:
    total = 0
    for c in string:
        total += ord(c)
    return total
