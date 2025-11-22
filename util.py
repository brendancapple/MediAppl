import os.path

import cv2
import numpy as np
from ebooklib import epub

LANGUAGE_CODES = {
    'en': 'English',
    'en-US': 'English',
    'en-UK': 'English',
    'es': 'Español',
    'jp': '日本語',
    'de': 'Deutsch',
    'he': 'עברית',
    'hi': 'हिंदी',
    'ko': '한국어',
    'fr': 'Français',
    'zh': '中文',
    'ru': 'русский',
}


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


def dictionary_list_remove(d: dict, k, e):
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
    result = set()

    # Iterate through all subsets (represented by 0 to 2^n - 1)
    for i in range(1 << n):
        subset = ""
        for j in range(n):
            # Check if the j-th bit is set in i
            if i & (1 << j):
                subset += " " + s[j]

        result.add(subset.strip())

    return list(result)


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
def get_epub_metadata(epub_path: str):
    print("get_epub_metadata of " + epub_path)
    try:
        book = epub.read_epub(epub_path)
    except:
        return "unknown", "unknown", "unknown"
    name = book.get_metadata('DC', 'title')[0][0]
    print(name)
    author = book.get_metadata('DC', 'creator')[0][0]
    print(author)
    language = book.get_metadata('DC', 'language')[0][0]
    if language in LANGUAGE_CODES:
        language = LANGUAGE_CODES[language]
    print(language)
    del book
    return name, author, language


def cache_epub_cover(db_dir: str, cache: str, epub_path: str) -> str:
    print("cache_epub_cover of " + epub_path)
    book = epub.read_epub(epub_path)
    try:
        cover_data = book.get_item_with_id('cover-image').get_content()
    except:
        return "unknown"
    del book
    nparr = np.frombuffer(cover_data, np.uint8)
    del cover_data

    if not os.path.exists(db_dir + cache):
        os.mkdir(db_dir + cache)
    epub_name = epub_path[epub_path.rfind("/")+1:epub_path.rfind(".")]
    image_path = db_dir + cache + "/" + epub_name + ".jpg"
    print("Cached Image Path " + image_path)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite(image_path, image)
    return image_path


def cache_video_cover(db_dir: str, cache: str, vid_path: str) -> str:
    print("cache_video_cover of " + vid_path)

    try:
        video = cv2.VideoCapture(vid_path)
    except:
        return "unknown"
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    mid_frame = int(total_frames/3)
    print(mid_frame, "/", total_frames)

    video.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
    ret, frame = video.read()
    print(ret)

    if not os.path.exists(db_dir + cache):
        os.mkdir(db_dir + cache)
    epub_name = vid_path[vid_path.rfind("/")+1:vid_path.rfind(".")]
    image_path = db_dir + cache + "/" + epub_name + ".jpg"
    print("Cached Image Path " + image_path)
    cv2.imwrite(image_path, frame)
    video.release()
    del video
    return image_path


def get_video_resolution(vid_path):
    try:
        video = cv2.VideoCapture(vid_path)
    except:
        return 0, 0
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
    res = (int(width), int(height))
    return res


def get_image_resolution(img_path):
    print("get img res")
    res = (0, 0)
    try:
        image = cv2.imread(img_path)
        print("read")
        shape = image.shape
        print("unwrap")
        res = (int(shape[1]), int(shape[0]))
    except:
        print(img_path)
        print("get img res failed: " + str(res))
        return res
    return res
