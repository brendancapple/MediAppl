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

def powerset(s):
    n = len(s)
    result = []

    # Iterate through all subsets (represented by 0 to 2^n - 1)
    for i in range(1 << n):
        subset = ""
        for j in range(n):
            # Check if the j-th bit is set in i
            if i & (1 << j):
                subset += " " + s[j]

        result.append(subset.strip())

    return result

def hash_string(string: str) -> int:
    total = 0
    for c in string:
        total += ord(c)
    return total
