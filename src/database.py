import os
import json
import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QProgressBar, QLabel

import src.util as util

CACHE_DIR = ".cache"
SUPPORTED_IMAGE_FORMATS = {"bmp", "png", "jpg", "jpeg", "gif", "cur", "ico", "jfif", "pbm", "pgm", "ppm", "svg", "svgz",
                           "xbm", "xpm"}
SUPPORTED_VIDEO_FORMATS = {"mp4", "mov", "avi", "flv", "mkv"}
SUPPORTED_AUDIO_FORMATS = {"mp3", "m4a", "ogg", "wav", "flac", "aiff"}
SUPPORTED_TEXT_FORMATS = {"txt", "md"}


#
#
# Entry Class
#
# Relative Path
# Cover Art Path (Plus Cover Art Thumbnail Cache)
# Name
# Author
# Series, Vol
# Language, Age Rating
# Release Date
# Resolution
# Isekai, Fantasy, Sci-Fi, Male-lead
#
class Entry:
    def __init__(self,
                 path,
                 cover_path,
                 name,
                 author,
                 series,
                 vol,
                 language,
                 age_rating,
                 release,
                 resolution,
                 tags):
        self.path = path
        self.cover_path = cover_path
        self.name = name
        self.author = author
        self.series = series
        self.vol = vol
        self.language = language
        self.age_rating = age_rating
        self.release = release
        self.resolution = resolution
        self.tags = tags
        self.cover_cache = None

    def __str__(self):
        return ('path: ' + self.path +
                '   cover: ' + self.cover_path +
                '   name: ' + self.name +
                '   author: ' + self.author +
                '   series: ' + self.series +
                '   vol: ' + str(self.vol) +
                '   language: ' + self.language +
                '   age_rating: ' + self.age_rating +
                '   release: ' + str(self.release) +
                '   resolution: ' + str(self.resolution) +
                '   tags: ' + str(self.tags)
                )

    @staticmethod
    def from_file(db, file: str):
        entry_name = file[file.rfind("/") + 1:file.rfind(".")]
        entry_ext = file[file.rfind(".") + 1:]
        entry_cover = "unknown"
        entry_lang = None
        entry_author = None
        entry_series = None
        entry_vol = 0
        entry_year = 0
        entry_res = (0, 0)
        entry_tags = []

        if entry_ext.lower() in SUPPORTED_VIDEO_FORMATS:
            entry_name, entry_author, entry_year, entry_genre = util.get_video_metadata(file)
            entry_cover = util.cache_video_cover(db.db_dir, CACHE_DIR, file)
            entry_res = util.get_video_resolution(file)
            entry_tags = ['Video', entry_genre] if entry_genre is not None else ['Video']
        elif entry_ext.lower() == "epub":
            entry_cover = util.cache_epub_cover(db.db_dir, CACHE_DIR, file)
            entry_name, entry_author, entry_lang = util.get_epub_metadata(file)
            entry_tags = ['Book']
        elif entry_ext.lower() in SUPPORTED_IMAGE_FORMATS:
            entry_cover = file
            entry_res = util.get_image_resolution(file)
            entry_tags = ['Image']
        elif entry_ext in SUPPORTED_AUDIO_FORMATS:
            entry_name, entry_author, entry_series, entry_vol, entry_year, entry_genre = util.get_audio_metadata(
                file)
            entry_cover = util.cache_audio_cover(db.db_dir, CACHE_DIR, file)
            entry_tags = ['Audio', entry_genre] if entry_genre is not None else ['Audio']
        elif entry_ext.lower() in SUPPORTED_TEXT_FORMATS:
            entry_tags = ['Text']

        if file[file.rfind("/") + 1:file.rfind(".")].strip().replace("_", "").replace(".", "").isdigit():
            file = file[:file.rfind("/")]
            entry_name = file[file.rfind("/") + 1:]

        if entry_name is None:
            print("fix name")
            entry_name = file[file.rfind("/") + 1:file.rfind(".")]
        if entry_lang is None:
            print("fix lang")
            entry_lang = "unknown"
        if entry_author is None:
            print("fix author")
            entry_author = "unknown"
        if entry_series is None:
            print("fix series")
            entry_series = "unknown"
        if entry_vol is None or not isinstance(entry_vol, int):
            print("fix vol")
            entry_vol = 0
        if entry_year is None:
            print("fix year")
            entry_year = 0
        elif not isinstance(entry_year, int):
            print("fix string year")
            entry_year = int(re.sub("[^0-9]", "", entry_year)[:4])
        if len(entry_tags) <= 0:
            print("fix tags")
            entry_tags = ['Unknown']

        entry_name = entry_name.replace("_", " ")

        print(entry_name, entry_lang, entry_author, entry_series, entry_vol, entry_lang, entry_year, entry_res,
              entry_tags)
        return Entry(file[len(db.db_dir):], entry_cover, entry_name, entry_author, entry_series, int(entry_vol),
                     entry_lang, "NA", int(entry_year), entry_res, entry_tags)

    def get_cover_icon(self, width, height):
        if self.cover_cache is None:
            small_pixmap = QPixmap(self.cover_path).scaled(width, height, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.cover_cache = QIcon(small_pixmap)
        return self.cover_cache

    def create_sorting_string(self, elements: int):
        print(elements)
        output = ""
        if (elements & util.SortingElements.PATH.value) != 0:
            print("path")
            output += self.path.lower()
        if (elements & util.SortingElements.LANGUAGE.value) != 0:
            print("lang")
            output += self.language.lower()
        if (elements & util.SortingElements.AUTHOR.value) != 0:
            print("author")
            output += self.author.lower()
        if (elements & util.SortingElements.SERIES.value) != 0:
            print("series")
            output += self.series.lower()
        if (elements & util.SortingElements.VOL.value) != 0:
            print("vol")
            output += str(self.vol).lower()
        if (elements & util.SortingElements.RATING.value) != 0:
            print("rating")
            output += self.age_rating.lower()
        if (elements & util.SortingElements.NAME.value) != 0:
            print("name")
            output += self.name.lower()
        if (elements & util.SortingElements.RESOLUTION.value) != 0:
            print("res")
            output += str(self.resolution).lower()
        if (elements & util.SortingElements.TAGS.value) != 0:
            print("tags")
            output += str(self.tags).lower()

        return output

    def dictionary(self):
        return {'path': self.path,
                'cover': self.cover_path,
                'name': self.name,
                'author': self.author,
                'series': self.series,
                'vol': self.vol,
                'language': self.language,
                'age_rating': self.age_rating,
                'release': self.release,
                'resolution': str(self.resolution),
                'tags': str(self.tags)
                }


#
#
# Database Class
#
# .APPL Structure:
#
# 0  Collection Name
# 1  Collection Directory
# 2
# 3  {"mp3":"vlc", "txt":"vim", ...}
# 4  Entry Count
# 5
# 6  ---
# 7
# 8  Relative Path
# 9  Cover Art Path
# 10 Name
# 11 Author
# 12 Series, Vol
# 13 Language, Age Rating
# 14 Release Date
# 15 1920x1080
# 16 Isekai, Fantasy, Sci-Fi, Male-lead, ...
# 17
#
class Database:
    # Initializes the DB
    def __init__(self, directory):
        content = ""
        with open(directory, "r", encoding="utf-8") as file:
            content = file.read()

        content = content.split("---")
        header = content[0].split("\n")
        entries = content[1:]

        self.file_dir = directory
        self.name = header[0]  # Collection Name
        self.db_dir = header[1]  # Collection Directory

        # App Associations
        self.app_associations = {a.split(":")[0].strip(): a.split(":")[1].strip() for a in (header[3]
                                                                                            .replace("{", "").replace(
            "}", "")
                                                                                            .replace("\"", "").replace(
            "'", "").split(","))}
        self.entry_count = int(header[4].strip())

        # Dictionary Setups
        self.tags = dict()
        self.authors = dict()
        self.series = dict()
        self.languages = dict()
        self.age_ratings = dict()
        self.filepaths = dict()
        self.extensions = dict()
        self.directories = util.Trie()

        self.loading_total = 0
        self.loading_current = 0

        # Items
        self.entries: [Entry] = []
        for e in entries:
            lines = e.split("\n")[1:]

            # print(lines)
            entry = Entry(
                path=lines[1],
                cover_path=lines[2],
                name=lines[3],
                author=lines[4],
                series=",".join(lines[5].split(",")[0:-1]).strip(),
                vol=int(lines[5].split(",")[-1].strip()),
                language=lines[6].split(",")[0].strip(),
                age_rating=lines[6].split(",")[-1].strip(),
                release=int(lines[7].strip()),
                resolution=(int(lines[8].split("x")[0]), int(lines[8].split("x")[1])),
                tags=[t.strip() for t in lines[9].split(",")]
            )
            # print(str(entry))
            self.entries.append(entry)

            util.dictionary_list_add(self.authors, entry.author.lower(), entry)
            util.dictionary_list_add(self.series, entry.series.lower(), entry)
            util.dictionary_list_add(self.languages, entry.language.lower(), entry)
            util.dictionary_list_add(self.age_ratings, entry.age_rating.lower(), entry)
            self.filepaths[entry.path] = entry
            self.directories.add(entry.path, "/", entry)
            for tag in entry.tags:
                util.dictionary_list_add(self.tags, tag.lower(), entry)
            if "." in entry.path:
                util.dictionary_list_add(self.extensions, entry.path[entry.path.rfind(".") + 1:], entry)

    def add_entry(self, entry):
        self.entries.append(entry)
        self.entry_count += 1

        util.dictionary_list_add(self.authors, entry.author.lower(), entry)
        util.dictionary_list_add(self.series, entry.series.lower(), entry)
        util.dictionary_list_add(self.languages, entry.language.lower(), entry)
        util.dictionary_list_add(self.age_ratings, entry.age_rating.lower(), entry)
        self.directories.add(entry.path, "/", entry)
        self.filepaths[entry.path] = entry
        for tag in entry.tags:
            util.dictionary_list_add(self.tags, tag.lower(), entry)

    def clean_entries(self):
        for e in self.entries:
            if not os.path.exists(self.db_dir + e.path):
                self.remove_entry(e)

    def load_files(self, bar: QProgressBar, label: QLabel):
        # print(os.listdir(self.db_dir))
        all_files = []
        for root, _, files in os.walk(self.db_dir):
            for file in files:
                all_files.append(os.path.join(root, file))
        print(all_files)

        total_files = len(all_files)
        print(total_files)
        current_file = 0
        if bar is not None:
            print("preset")
            bar.setMaximum(total_files)
            bar.setValue(current_file)
            label.setText(str(current_file) + "/" + str(total_files))
            print("post-set")

        for file in all_files:
            current_file += 1
            file = file.replace("\\", "/")
            print(file)
            if ("/" + CACHE_DIR + "/") in file:
                print("cached")
                continue
            if "._" in file:
                print("found ._ in " + file)
                continue
            if file[len(self.db_dir):] in self.filepaths:
                print("skip file -- known" + file)
                continue

            entry = Entry.from_file(self, file)
            print("created entry")

            self.add_entry(entry)
            print("added to entries")
            if bar is not None:
                bar.setValue(current_file)
                label.setText(str(current_file) + "/" + str(total_files))
        print("FILES LOADED")

    def save_as_file(self, filepath: str):
        text = (
                self.name + "\n" +
                self.db_dir + "\n\n" +
                str(self.app_associations) + "\n" +
                str(self.entry_count) + "\n"
        )

        for entry in self.entries:
            text = (
                    text + "\n---\n\n"
                    + entry.path + "\n"
                    + entry.cover_path + "\n"
                    + entry.name + "\n"
                    + entry.author + "\n"
                    + entry.series + ", " + str(entry.vol) + "\n"
                    + entry.language + ", " + entry.age_rating + "\n"
                    + str(entry.release) + "\n"
                    + str(entry.resolution[0]) + "x" + str(entry.resolution[1]) + "\n"
                    + str(entry.tags)[1:-1].replace("'", "") + "\n"
            )

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(text)

    def merge_metadata(self, target: Entry, source: Entry):
        if util.judge_better_result(target.path, target.name, source.name) < 0:
            print("  change name")
            self.set_name(target, source.name)
        if util.judge_better_result(target.path, target.cover_path, source.cover_path) < 0:
            print("  change cover")
            self.set_cover(target, source.cover_path)
        if util.judge_better_result(target.path, target.author, source.author) < 0:
            print("  change author")
            self.set_author(target, source.author)
        if util.judge_better_result(target.path, target.series, source.series) < 0:
            print("  change series")
            self.set_series(target, source.series)
        if util.judge_better_result(target.path, target.language, source.language) < 0:
            print("  change language")
            self.set_language(target, source.language)
        if util.judge_better_result(target.path, target.age_rating, source.age_rating) < 0:
            print("  change rating")
            self.set_rating(target, source.age_rating)
        if source.vol != 0:
            print("  change volume")
            self.set_vol(target, source.vol)
        if source.release != 0:
            print("  change release")
            self.set_release(target, source.release)

        for tag in source.tags:
            if tag not in target.tags:
                self.add_tag(target, tag)
        if "unknown" in target.tags and len(target.tags) > 1:
            self.remove_tag(target, "unknown")

    @staticmethod
    def create_database_from_json(filepath: str) -> str:
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
            print("File data =", data)

            text = (
                    data["name"] + "\n" +
                    data["db_dir"] + "\n\n" +
                    str(data["app_associations"]) + "\n" +
                    str(data["entry_count"]) + "\n"
            )

            for entry in data["entries"]:
                resolution = entry["resolution"].replace("(", "").replace(")", "").split(",")
                text = (
                        text + "\n---\n\n"
                        + entry["path"] + "\n"
                        + entry["cover"] + "\n"
                        + entry["name"] + "\n"
                        + entry["author"] + "\n"
                        + entry["series"] + ", " + str(entry["vol"]) + "\n"
                        + entry["language"] + ", " + entry["age_rating"] + "\n"
                        + str(entry["release"]) + "\n"
                        + resolution[0].strip() + "x" + resolution[1].strip() + "\n"
                        + str(entry["tags"])[1:-1].replace("'", "") + "\n"
                )

            output_filepath = filepath[:-5] + "_json.appl"
            with open(output_filepath, "w", encoding="utf-8") as file:
                file.write(text)
            return output_filepath
        except:
            return "unknown"

    def export_json(self, filepath: str):
        dictionary = {
            "file_dir": self.file_dir,
            "name": self.name,
            "db_dir": self.db_dir,

            "app_associations": self.app_associations,
            "entry_count": self.entry_count,
            "entries": [e.dictionary() for e in self.entries]
        }

        with open(filepath, 'w') as file:
            output = json.dumps(dictionary)
            print(output)
            file.write(output)

    def export_csv(self, filepath: str):
        rows = []
        for e in self.entries:
            row = str(self.db_dir + e.path +
                      ', ' + str(e.cover_path) +
                      ', "' + str(e.name).replace('"', '\\"') +
                      '", "' + str(e.author).replace('"', '\\"') +
                      '", "' + str(e.series).replace('"', '\\"') +
                      '", ' + str(e.vol).replace('"', '\\"') +
                      ', ' + str(e.language).replace('"', '\\"') +
                      ', ' + str(e.age_rating) +
                      ', ' + str(e.release) +
                      ', ' + str(e.resolution[0]) +
                      ', ' + str(e.resolution[1]) +
                      ', "' + str(e.tags)[1:-1] + '"'
                      )
            rows.append(row)
        output = '\n'.join(rows)
        print(output)

        with open(filepath, 'w') as file:
            file.write(output)

    def import_metadata_from_database(self, other):
        for entry in other.entries:
            if entry.path not in self.filepaths:
                continue

            print(entry.path)
            target = self.filepaths.get(entry.path)
            print(target.path)

            self.merge_metadata(target, entry)
            print("merged metadata")

    def import_metadata_from_csv(self, csv: str):
        with open(csv, "r") as file:
            contents = file.read()
            rows = contents.split("\n")

        print("pulled from file")

        db_path = ""
        for i in range(rows[0].index(",")):
            same = True
            for row in rows:
                if row[i] != rows[0][i]:
                    same = False
            if not same:
                break
            db_path = db_path + rows[0][i]

        print(db_path)

        for row in rows:
            cols = [c.strip() for c in row.split(",")]
            metadata = []
            combine = False
            for col in cols:
                print(col)
                if combine:
                    metadata[-1] = metadata[-1] + ", " + col
                else:
                    metadata.append(col)

                if len(col) == 0:
                    continue
                if col[-1] == '"':
                    combine = False
                if col[0] == '"':
                    combine = True
                if col[-1] == '"' and len(col) > 1:
                    if col[-1] == '\\':
                        continue
                    combine = False

            print("columns split: ", metadata)
            entry = Entry(
                metadata[0][len(db_path):],
                metadata[1],
                metadata[2][1:-1],
                metadata[3][1:-1],
                metadata[4][1:-1],
                int(metadata[5]),
                metadata[6],
                metadata[7],
                int(metadata[8]),
                (int(metadata[9]), int(metadata[10])),
                [t.replace("'", "").replace('"', "").strip() for t in metadata[11][1:-1].split(",")]
            )
            print("entry: ", entry)

            if entry.path not in self.filepaths:
                continue

            print(entry.path)
            target = self.filepaths.get(entry.path)
            print(target.path)

            self.merge_metadata(target, entry)
            print("merged metadata")

    def set_app_associations(self, extension: str, app: str):
        self.app_associations[extension] = app

    def set_cover(self, entry: Entry, cover: str):
        entry.cover_path = cover

    def set_name(self, entry: Entry, name: str):
        entry.name = name

    def set_author(self, entry: Entry, author: str):
        util.dictionary_list_remove(self.authors, entry.author.lower(), entry)
        entry.author = author
        util.dictionary_list_add(self.authors, entry.author.lower(), entry)

    def set_series(self, entry: Entry, series: str):
        util.dictionary_list_remove(self.series, entry.series.lower(), entry)
        entry.series = series
        util.dictionary_list_add(self.series, entry.series.lower(), entry)

    def set_vol(self, entry: Entry, vol: int):
        entry.vol = vol

    def set_language(self, entry: Entry, language: str):
        util.dictionary_list_remove(self.languages, entry.language.lower(), entry)
        entry.language = language
        util.dictionary_list_add(self.languages, entry.language.lower(), entry)

    def set_rating(self, entry: Entry, age_rating: str):
        util.dictionary_list_remove(self.age_ratings, entry.age_rating.lower(), entry)
        entry.age_rating = age_rating
        util.dictionary_list_add(self.age_ratings, entry.age_rating.lower(), entry)

    def set_release(self, entry: Entry, release: int):
        entry.release = release

    def set_resolution(self, entry: Entry, x: int, y: int):
        entry.resolution = (x, y)

    def add_tag(self, entry: Entry, tag: str):
        util.dictionary_list_add(self.tags, tag.lower(), entry)
        entry.tags.append(tag)

    def remove_tag(self, entry: Entry, tag: str):
        util.dictionary_list_remove(self.tags, tag.lower(), entry)
        entry.tags.remove(tag)

    def set_tags(self, entry: Entry, tags: str):
        for t in entry.tags:
            util.dictionary_list_remove(self.tags, t.lower(), entry)
        entry.tags = []
        new_tags = [t.strip() for t in tags.split(",")]
        for t in new_tags:
            self.add_tag(entry, t)

    def remove_entry(self, entry: Entry):
        self.entries.remove(entry)
        util.dictionary_list_remove(self.authors, entry.author, entry)
        util.dictionary_list_remove(self.series, entry.series, entry)
        util.dictionary_list_remove(self.languages, entry.language, entry)
        util.dictionary_list_remove(self.age_ratings, entry.age_rating, entry)
        for tag in entry.tags:
            util.dictionary_list_remove(self.tags, tag, entry)
        self.entry_count -= 1

    def search(self, query: str):
        filters = [item.lower().strip() for item in query.split("]")]

        final_filter_index = -1
        for i in range(len(filters)):
            print(filters[i])
            if filters[i] == "":
                continue
            if filters[i][0] != "[":
                final_filter_index = i
                break
            filters[i] = filters[i].replace("[", "")
        print(str(final_filter_index))

        query = " ".join(filters[final_filter_index:])
        filters = filters[:final_filter_index]
        print(filters)
        print(query)

        words = list(util.powerset(query.split(" "))[1:])
        print(words)

        output_dict = dict()
        filtered_set = set(self.entries)

        for filt in filters:
            temp_filtered_set = set()
            if filt in self.tags:
                for entry in self.tags[filt]:
                    if entry not in filtered_set:
                        continue
                    temp_filtered_set.add(entry)
                    util.dictionary_force_increment(output_dict, entry)
            if filt in self.languages:
                for entry in self.languages[filt]:
                    if entry not in filtered_set:
                        continue
                    temp_filtered_set.add(entry)
                    util.dictionary_force_increment(output_dict, entry)
            if filt in self.authors:
                for entry in self.authors[filt]:
                    if entry not in filtered_set:
                        continue
                    temp_filtered_set.add(entry)
                    util.dictionary_force_increment(output_dict, entry)
            if filt in self.series:
                for entry in self.series[filt]:
                    if entry not in filtered_set:
                        continue
                    temp_filtered_set.add(entry)
                    util.dictionary_force_increment(output_dict, entry)
            if filt in self.age_ratings:
                for entry in self.age_ratings[filt]:
                    if entry not in filtered_set:
                        continue
                    temp_filtered_set.add(entry)
                    util.dictionary_force_increment(output_dict, entry)
            if filt in self.extensions:
                for entry in self.extensions[filt]:
                    if entry not in filtered_set:
                        continue
                    temp_filtered_set.add(entry)
                    util.dictionary_force_increment(output_dict, entry)
            filtered_set = temp_filtered_set
        print("o: " + str(output_dict))
        print("s: " + str(filtered_set))

        for word in words:
            if word in self.tags:
                for entry in self.tags[word]:
                    util.dictionary_force_increment(output_dict, entry)
            if word in self.languages:
                for entry in self.languages[word]:
                    util.dictionary_force_increment(output_dict, entry)
            if word in self.authors:
                for entry in self.authors[word]:
                    util.dictionary_force_increment(output_dict, entry)
            if word in self.series:
                for entry in self.series[word]:
                    util.dictionary_force_increment(output_dict, entry)
            if word in self.age_ratings:
                for entry in self.age_ratings[word]:
                    util.dictionary_force_increment(output_dict, entry)
            if word in self.extensions:
                for entry in self.extensions[word]:
                    util.dictionary_force_increment(output_dict, entry)

            for entry in self.entries:
                name = entry.name.lower()
                if word in name:
                    util.dictionary_force_increment(output_dict, entry)
                path = entry.path.lower()
                if word in path:
                    util.dictionary_force_increment(output_dict, entry)

        output_dict = {key: value for key, value in sorted(output_dict.items(), key=lambda item: item[1], reverse=True)}
        print(output_dict)
        output_list = []
        for k in output_dict.keys():
            if k in filtered_set:
                output_list.append(k)
        print(output_list)

        return output_list

    def print(self):
        print(self.file_dir)
        print(self.name)
        print(self.db_dir)
        print(self.app_associations)
        print(self.entries)
        print("-")
        print("Tags: ", self.tags)
        print("Authors: ", self.authors)
        print("Series: ", self.series)
        print("Languages: ", self.languages)
        print("Ratings: ", self.age_ratings)
        print("---")
