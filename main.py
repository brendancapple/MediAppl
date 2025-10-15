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
# 15 Resolution
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
        self.app_associations = {a.split(":")[0]: a.split[1] for a in (header[3].replace("{", "")
                                                                                .replace("}", "")
                                                                                .replace("\"", "")
                                                                                .split(","))}

        print(self.file_dir)
        print(self.name)
        print(self.db_dir)
        print(self.app_associations)

    def validate_files(self):
        pass


#
#
# Program Loop
if __name__ == '__main__':
    print('Filepath to Database:')
    filepath = input()
    database = Database(filepath)
