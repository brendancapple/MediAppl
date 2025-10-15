#################
#   MediAppl    #
# Brendan Apple #
#################
#
# Media Organizer for Local Files w/o Changing File Structures
#
#

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
        with open(filepath, "r", encoding="utf-8") as file:
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
                                .replace("\"", "").split(","))}

        # Items
        self.files: [Entry] = []
        for e in entries:
            lines = e.split("\n")[1:]
            # print(lines)
            entry = Entry(
                lines[1],
                lines[2],
                lines[3],
                lines[4],
                lines[5].split(",")[0].strip(),
                lines[5].split(",")[1].strip(),
                lines[6].split(",")[0].strip(),
                lines[6].split(",")[1].strip(),
                lines[7],
                (int(lines[8].split("x")[0]), int(lines[8].split("x")[1])),
                [t.strip() for t in lines[9].split(",")]
            )
            # print(str(entry))
            self.files.append(entry)

        print(self.file_dir)
        print(self.name)
        print(self.db_dir)
        print(self.app_associations)
        print(self.files)

    def validate_files(self):
        pass


#
#
# Program Loop
if __name__ == '__main__':
    print('Filepath to Database:')
    filepath = input()
    database = Database(filepath)
