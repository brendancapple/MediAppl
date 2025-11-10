import os
import util

SUPPORTED_IMAGE_FORMATS = {"bmp", "png", "jpg", "jpeg", "gif", "cur", "ico", "jfif", "pbm", "pgm", "ppm", "svg", "svgz", "xbm", "xpm"}

#
#
# Entry Class
#
# Relative Path
# Cover Art Path
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

    def __str__(self):
        return ('path: ' + self.path +
                '   cover: ' + self.cover_path +
                '   name: ' + self.name +
                '   author: ' + self.author +
                '   series: ' + self.series +
                '   vol: ' + self.vol +
                '   language: ' + self.language +
                '   age_rating: ' + self.age_rating +
                '   release: ' + self.release +
                '   resolution: ' + str(self.resolution) +
                '   tags: ' + str(self.tags)
                )


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
                                .replace("{", "").replace("}", "")
                                .replace("\"", "").replace("'", "").split(","))}
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
                series=lines[5].split(",")[0].strip(),
                vol=int(lines[5].split(",")[1].strip()),
                language=lines[6].split(",")[0].strip(),
                age_rating=lines[6].split(",")[1].strip(),
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
                util.dictionary_list_add(self.tags, tag, entry)
            if "." in entry.path:
                util.dictionary_list_add(self.extensions, entry.path[entry.path.rfind(".")+1:], entry)

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

    def load_files(self):
        # print(os.listdir(self.db_dir))
        all_files = []
        for root, _, files in os.walk(self.db_dir):
            for file in files:
                all_files.append(os.path.join(root, file))
        print(all_files)

        for file in all_files:
            file = file.replace("\\", "/")
            entry_name = file[file.rfind("/")+1:file.rfind(".")]
            entry_ext = file[file.rfind(".")+1:]
            entry_cover = "unknown"
            if entry_ext in SUPPORTED_IMAGE_FORMATS:
                entry_cover = file
            if entry_name.strip().replace("_", "").replace(".", "").isdigit():
                file = file[:file.rfind("/")]
                entry_name = file[file.rfind("/")+1:]
            entry = Entry(file[len(self.db_dir):], entry_cover, entry_name,
                          "unknown", "unknown", 1, "unknown", "NA", 0,
                          (0, 0), ["unknown"])

            if entry.path in self.filepaths:
                print("skip file")
                continue
            self.add_entry(entry)

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

    def set_resolution(self, entry: Entry, x: int, y:int):
        entry.resolution = (x, y)

    def add_tag(self, entry: Entry, tag: str):
        util.dictionary_list_add(self.tags, tag.lower(), entry)
        entry.tags.append(tag)

    def remove_tag(self, entry: Entry, tag: str):
        util.dictionary_list_remove(self.tags, tag.lower(), entry)
        entry.tags.remove(tag)

    def set_tags(self, entry: Entry, tags: str):
        for t in entry.tags:
            self.remove_tag(entry, t)
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
        query = query.strip()
        words = util.powerset(query.split(" "))[1:]
        print(words)

        output_dict = dict()

        for word in words:
            word = word.lower().strip()
            if word in self.tags:
                for entry in self.tags[word]:
                    if entry not in output_dict:
                        output_dict[entry] = 1
                    else:
                        output_dict[entry] += 1
            if word in self.languages:
                for entry in self.languages[word]:
                    if entry not in output_dict:
                        output_dict[entry] = 1
                    else:
                        output_dict[entry] += 1
            if word in self.authors:
                for entry in self.authors[word]:
                    if entry not in output_dict:
                        output_dict[entry] = 1
                    else:
                        output_dict[entry] += 1
            if word in self.series:
                for entry in self.series[word]:
                    if entry not in output_dict:
                        output_dict[entry] = 1
                    else:
                        output_dict[entry] += 1
            if word in self.age_ratings:
                for entry in self.age_ratings[word]:
                    if entry not in output_dict:
                        output_dict[entry] = 1
                    else:
                        output_dict[entry] += 1
            if word in self.extensions:
                for entry in self.extensions[word]:
                    if entry not in output_dict:
                        output_dict[entry] = 1
                    else:
                        output_dict[entry] += 1

            for entry in self.entries:
                name = entry.name.lower()
                if word in name:
                    if entry not in output_dict:
                        output_dict[entry] = 1
                    else:
                        output_dict[entry] += 1
                path = entry.path.lower()
                if word in path:
                    if entry not in output_dict:
                        output_dict[entry] = 1
                    else:
                        output_dict[entry] += 1

        output_dict = {key: value for key, value in sorted(output_dict.items(), key=lambda item: item[1], reverse=True)}
        print(output_dict)

        return output_dict.keys()

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


#
#
# Program Loop
if __name__ == '__main__':
    print('Filepath to Database:')
    filepath = input()
    database = Database(filepath)
    database.load_files()
    database.print()
    print()

    # database.set_app_associations("txt", "nano")
    # database.set_name(database.entries[1], "Lol1")
    # database.set_author(database.entries[1], "Lol Master")
    # database.add_tag(database.entries[1], "Meme")
    # database.print()
    # print()

    # database.remove_entry(database.entries[1])
    # database.print()

    print('Filepath to Save:')
    savepath = input()
    database.save_as_file(savepath)
