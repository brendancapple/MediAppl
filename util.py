import ebooklib
from ebooklib import epub
from PIL import Image
# from io import BytesIO
# import os

# Trie
def list_tree(d: dict) -> list:
    output = []
    if "" in d:
        output.append(d[""])
    for e in d.keys():
        if e == "":
            continue
        for a in list_tree(e):
            output.append(a)
    return output


class Trie:
    def __init__(self):
        self.root = dict()

    def add(self, key: str, separator: str, value):
        key_list = key.split(separator)
        current_dict = self.root
        for k in key_list:
            if k not in current_dict:
                current_dict[k] = dict()
            current_dict = current_dict[k]
        current_dict[""] = value

    def get(self, key: str, separator: str):
        key_list = key.split(separator)
        current_dict = self.root
        for k in key_list:
            if k not in current_dict:
                return None
            current_dict = current_dict[k]
        if "" in current_dict:
            return current_dict[""]
        else:
            return None

    def remove(self, key: str, separator: str):
        key_list = key.split(separator)
        current_dict = self.root
        for k in key_list:
            if k not in current_dict:
                return
            current_dict = current_dict[k]
        if "" in current_dict:
            current_dict.remove("")

    def list_after(self, key: str, separator: str):
        key_list = key.split(separator)
        current_dict = self.root
        for k in key_list:
            if k not in current_dict:
                return None
            current_dict = current_dict[k]
        return list_tree(current_dict)

    def list(self) -> list:
        return list_tree(self.root)


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

# Set Operations
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

# Hashing
def hash_string(string: str) -> int:
    total = 0
    for c in string:
        total += ord(c)
    return total

# Safe Open
# def mkdir_p(path):
#     try:
#         os.makedirs(path)
#     except OSError as exc:  # Python >2.5
#         if exc.errno == errno.EEXIST and os.path.isdir(path):
#             pass
#         else:
#             raise
#
# def safe_open_w(path):
#     ''' Open "path" for writing, creating any parent directories as needed.
#     '''
#     mkdir_p(os.path.dirname(path))
#     return open(path, 'w')

# Cover Grabbing
def get_epub_cover(epub_path):
    print("get_epub_cover of " + epub_path)
    book = epub.read_epub(epub_path)
    cover_data = book.get_item_with_id('cover-image').get_content()
    del book
    cover_image = Image.open(BytesIO(cover_data))
