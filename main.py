#################
#   MediAppl    #
# Brendan Apple #
#################
#
# Media Organizer for Local Files w/o Changing File Structures
#
#
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QWidget,
    QStatusBar, QToolBar, QAction,
    QLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QCheckBox, QPushButton, QLineEdit, QTextEdit,
    QListWidget, QListWidgetItem, QAbstractItemView, QTabWidget,
    QDialog, QFileDialog, QInputDialog, QDialogButtonBox
)
from PIL import Image
from PIL import ImageQt
from functools import partial
import subprocess
import sys
import os

import database as db
import util
import qt_util

ENTRY_LISTING_HEIGHT = 60
DEFAULT_APP_ASSOCIATIONS = {"mp3": "vlc", "txt": "vim"}


class EntryListing(QListWidgetItem):
    def __init__(self, main_window, entry: db.Entry):
        super().__init__()
        self.mw = main_window
        self.entry = entry

        self.setText("[" + self.entry.age_rating + "] " + self.entry.author + ": " + self.entry.name)


class PreferencesDialog(QDialog):
    def __init__(self, database: db.Database, parent=None):
        super().__init__(parent)
        self.database = database

        self.setWindowTitle(self.database.name + " Preferences")
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.apply)
        self.buttonBox.rejected.connect(self.reject)

        label_name = QLabel("Name: ")
        self.input_name = QLineEdit(self.database.name)
        self.input_name.setPlaceholderText("Name")
        layout_name = QHBoxLayout()
        layout_name.addWidget(label_name)
        layout_name.addWidget(self.input_name)
        row_name = QWidget()
        row_name.setLayout(layout_name)

        label_apps = QLabel("App Associations")
        str_apps = "\n".join([k + ": " + v for k, v in self.database.app_associations.items()])
        print(str_apps)
        self.text_apps = QTextEdit()
        self.text_apps.setText(str_apps)

        layout = QVBoxLayout()
        layout.addWidget(row_name)
        layout.addWidget(label_apps)
        layout.addWidget(self.text_apps)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def apply(self):
        self.database.name = self.input_name.text()
        dict_apps = {a.split(":")[0].strip(): a.split(":")[1].strip() for a in (self.text_apps.toPlainText()
                                          .replace("\"", "").replace("'", "").split("\n"))}
        self.database.app_associations = dict_apps
        self.database.save_as_file(self.database.file_dir)
        self.accept()


class FilterDialog(QDialog):
    def __init__(self, database: db.Database, start_tab: int, parent=None):
        super().__init__(parent)
        self.database = database

        self.authors = list(self.database.authors.keys())
        self.series = list(self.database.series.keys())
        self.languages = list(self.database.languages.keys())
        self.ratings = list(self.database.age_ratings.keys())
        self.tags = list(self.database.tags.keys())

        self.output = set()

        self.setWindowTitle("Filter")
        self.setMinimumWidth(620)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        label_author = QLabel("Author")
        label_series = QLabel("Series")
        label_language = QLabel("Languages")
        label_rating = QLabel("Ratings")
        label_tag = QLabel("Tags")
        self.label_output = QLabel("")

        widget_author = QWidget()
        layout_author = qt_util.FlowLayout()
        for key in self.authors:
            button_key = QPushButton(key)
            button_key.setCheckable(True)
            button_key.clicked.connect(partial(self.toggle_output, key))
            layout_author.addWidget(button_key)
        widget_author.setLayout(layout_author)

        widget_series = QWidget()
        layout_series = qt_util.FlowLayout()
        for key in self.series:
            button_key = QPushButton(key)
            button_key.setCheckable(True)
            button_key.clicked.connect(partial(self.toggle_output, key))
            layout_series.addWidget(button_key)
        widget_series.setLayout(layout_series)

        widget_languages = QWidget()
        layout_languages = qt_util.FlowLayout()
        for key in self.languages:
            button_key = QPushButton(key)
            button_key.setCheckable(True)
            button_key.clicked.connect(partial(self.toggle_output, key))
            layout_languages.addWidget(button_key)
        widget_languages.setLayout(layout_languages)

        widget_ratings = QWidget()
        layout_ratings = qt_util.FlowLayout()
        for key in self.ratings:
            button_key = QPushButton(key)
            button_key.setCheckable(True)
            button_key.clicked.connect(partial(self.toggle_output, key))
            layout_ratings.addWidget(button_key)
        widget_ratings.setLayout(layout_ratings)

        widget_tags = QWidget()
        layout_tags = qt_util.FlowLayout()
        for key in self.tags:
            button_key = QPushButton(key)
            button_key.setCheckable(True)
            button_key.clicked.connect(partial(self.toggle_output, key))
            layout_tags.addWidget(button_key)
        widget_tags.setLayout(layout_tags)

        tab_author = QWidget()
        tab_author.setObjectName("tags_tab")
        tab_layout_author = QVBoxLayout()
        tab_layout_author.addWidget(label_author)
        tab_layout_author.addWidget(widget_author)
        tab_author.setLayout(tab_layout_author)

        tab_series = QWidget()
        tab_series.setObjectName("tags_tab")
        tab_layout_series = QVBoxLayout()
        tab_layout_series.addWidget(label_series)
        tab_layout_series.addWidget(widget_series)
        tab_series.setLayout(tab_layout_series)

        tab_languages = QWidget()
        tab_languages.setObjectName("tags_tab")
        tab_layout_languages = QVBoxLayout()
        tab_layout_languages.addWidget(label_language)
        tab_layout_languages.addWidget(widget_languages)
        tab_languages.setLayout(tab_layout_languages)

        tab_ratings = QWidget()
        tab_ratings.setObjectName("tags_tab")
        tab_layout_ratings = QVBoxLayout()
        tab_layout_ratings.addWidget(label_rating)
        tab_layout_ratings.addWidget(widget_ratings)
        tab_ratings.setLayout(tab_layout_ratings)

        tab_tags = QWidget()
        tab_tags.setObjectName("tags_tab")
        tab_layout_tags = QVBoxLayout()
        tab_layout_tags.addWidget(label_tag)
        tab_layout_tags.addWidget(widget_tags)
        tab_tags.setLayout(tab_layout_tags)

        tabs = QTabWidget()
        tabs.addTab(tab_author, "Authors")
        tabs.addTab(tab_series, "Series")
        tabs.addTab(tab_languages, "Languages")
        tabs.addTab(tab_ratings, "Ratings")
        tabs.addTab(tab_tags, "Tags")
        tabs.setCurrentIndex(start_tab)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(self.label_output)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        print("combined")

    def toggle_output(self, key: str):
        if key in self.output:
            self.output.remove(key)
        else:
            self.output.add(key)
        self.label_output.setText(self.get_output())

    def get_output(self) -> str:
        output = ""
        for key in list(self.output):
            output = output + "[" + key + "] "
        return output


class EditDialog(QDialog):
    def __init__(self, database: db.Database, entry: db.Entry, parent=None):
        super().__init__(parent)
        self.database = database
        self.entry = entry

        self.setWindowTitle("Edit " + self.entry.name)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.apply)
        self.buttonBox.rejected.connect(self.reject)

        message = QLabel("Edit Entry")

        label_name = QLabel("Name: ")
        self.input_name = QLineEdit(entry.name)
        self.input_name.setPlaceholderText("Name")
        layout_name = QHBoxLayout()
        layout_name.addWidget(label_name)
        layout_name.addWidget(self.input_name)
        row_name = QWidget()
        row_name.setLayout(layout_name)

        label_cover = QLabel("Cover: ")
        self.input_cover = QLineEdit(entry.cover_path)
        self.input_cover.setPlaceholderText("Cover Path")
        button_cover = QPushButton("...")
        button_cover.clicked.connect(self.find_cover)
        layout_cover = QHBoxLayout()
        layout_cover.addWidget(label_cover)
        layout_cover.addWidget(self.input_cover)
        layout_cover.addWidget(button_cover)
        row_cover = QWidget()
        row_cover.setLayout(layout_cover)

        label_author = QLabel("Author: ")
        self.input_author = QLineEdit(entry.author)
        self.input_author.setPlaceholderText("Author")
        layout_author = QHBoxLayout()
        layout_author.addWidget(label_author)
        layout_author.addWidget(self.input_author)
        row_author = QWidget()
        row_author.setLayout(layout_author)

        label_series = QLabel("Series: ")
        self.input_series = QLineEdit(entry.series)
        self.input_series.setPlaceholderText("Series")
        self.input_vol = QLineEdit(str(entry.vol))
        self.input_vol.setPlaceholderText("vol")
        layout_series = QHBoxLayout()
        layout_series.addWidget(label_series)
        layout_series.addWidget(self.input_series)
        layout_series.addWidget(self.input_vol)
        row_series = QWidget()
        row_series.setLayout(layout_series)

        label_language = QLabel("Language: ")
        self.input_language = QLineEdit(entry.language)
        self.input_language.setPlaceholderText("Language")
        label_rating = QLabel("Rating: ")
        self.input_rating = QLineEdit(entry.age_rating)
        self.input_rating.setPlaceholderText("Rating")
        layout_language = QHBoxLayout()
        layout_language.addWidget(label_language)
        layout_language.addWidget(self.input_language)
        layout_language.addWidget(label_rating)
        layout_language.addWidget(self.input_rating)
        row_language = QWidget()
        row_language.setLayout(layout_language)

        label_release = QLabel("Release: ")
        self.input_release = QLineEdit(str(entry.release))
        self.input_release.setPlaceholderText("Release Date")
        layout_release = QHBoxLayout()
        layout_release.addWidget(label_release)
        layout_release.addWidget(self.input_release)
        row_release = QWidget()
        row_release.setLayout(layout_release)

        label_resolution = QLabel("Resolution: ")
        self.input_res1 = QLineEdit(str(entry.resolution[0]))
        self.input_res1.setPlaceholderText("x")
        self.input_res2 = QLineEdit(str(entry.resolution[1]))
        self.input_res2.setPlaceholderText("y")
        layout_resolution = QHBoxLayout()
        layout_resolution.addWidget(label_resolution)
        layout_resolution.addWidget(self.input_res1)
        layout_resolution.addWidget(self.input_res2)
        row_resolution = QWidget()
        row_resolution.setLayout(layout_resolution)

        label_tags = QLabel("Tags: ")
        self.input_tags = QLineEdit(str(entry.tags)[1:-1].replace("'", ""))
        self.input_tags.setPlaceholderText("Tag1, Tag2, Tag3, ...")
        layout_tags = QHBoxLayout()
        layout_tags.addWidget(label_tags)
        layout_tags.addWidget(self.input_tags)
        row_tags = QWidget()
        row_tags.setLayout(layout_tags)

        layout = QVBoxLayout()
        layout.addWidget(message)
        layout.addWidget(row_name)
        layout.addWidget(row_cover)
        layout.addWidget(row_author)
        layout.addWidget(row_series)
        layout.addWidget(row_language)
        layout.addWidget(row_release)
        layout.addWidget(row_resolution)
        layout.addWidget(row_tags)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def find_cover(self):
        print("Find Cover")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Image (*.png *.jpg *.jpeg *.bmp *.gif *.svg)")
        if dialog.exec_():
            filepath = dialog.selectedFiles()[0]
            self.input_cover.setText(filepath)

    def apply(self):
        self.database.set_name(self.entry, self.input_name.text())
        self.entry.cover_path = self.input_cover.text()
        self.database.set_author(self.entry, self.input_author.text())
        self.database.set_series(self.entry, self.input_series.text())
        self.entry.vol = int(self.input_vol.text())
        self.database.set_language(self.entry, self.input_language.text())
        self.database.set_rating(self.entry, self.input_rating.text())
        self.entry.release = int(self.input_release.text())
        self.entry.resolution = (int(self.input_res1.text()), int(self.input_res2.text()))
        self.database.set_tags(self.entry, self.input_tags.text())
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):
        super().__init__()
        self.screen = app.primaryScreen()
        self.database: db.Database = db.Database("test.appl")
        self.entries = []
        self.entry: db.Entry = self.database.entries[0]

        self.setWindowTitle("MediAppl")

        # Create Actions
        button_new = QAction("New", self)
        button_new.setStatusTip("New Database")
        button_new.setShortcut(QKeySequence("Ctrl+n"))
        button_new.triggered.connect(self.new_database)

        button_load = QAction("Load", self)
        button_load.setStatusTip("Load Database")
        button_load.setShortcut(QKeySequence("Ctrl+o"))
        button_load.triggered.connect(self.load_database)

        button_save = QAction("Save", self)
        button_save.setStatusTip("Save Database")
        button_save.setShortcut(QKeySequence("Ctrl+s"))
        button_save.triggered.connect(self.save_database)

        button_save_as = QAction("Save As", self)
        button_save_as.setStatusTip("Save Database as a New File")
        button_save_as.setShortcut(QKeySequence("Ctrl+alt+s"))
        button_save_as.triggered.connect(self.save_as_database)

        button_reload = QAction("Reload", self)
        button_reload.setStatusTip("Reload Database From Disk")
        button_reload.setShortcut(QKeySequence("Ctrl+r"))
        button_reload.triggered.connect(self.reload_database)

        button_edit = QAction("Edit", self)
        button_edit.setStatusTip("Edit Current Entry")
        button_edit.setShortcut(QKeySequence("Ctrl+e"))
        button_edit.triggered.connect(self.edit_entry)

        button_open = QAction("Open", self)
        button_open.setStatusTip("Open Current Entry")
        button_open.setShortcut(QKeySequence("Ctrl+enter"))
        button_open.triggered.connect(self.open_entry)

        button_preferences = QAction("Preferences", self)
        button_preferences.setStatusTip("Edit Database Preferences")
        button_preferences.setShortcut(QKeySequence("Ctrl+p"))
        button_preferences.triggered.connect(self.edit_preferences)

        button_filter = QAction("Filter", self)
        button_filter.setStatusTip("Filter Entries")
        button_filter.setShortcut(QKeySequence("Ctrl+f"))
        button_filter.triggered.connect(self.search_filter)

        button_authors = QAction("Authors", self)
        button_authors.setStatusTip("Filter Authors")
        button_authors.triggered.connect(self.search_authors)

        button_series = QAction("Series", self)
        button_series.setStatusTip("Filter Series")
        button_series.triggered.connect(self.search_series)

        button_languages = QAction("Languages", self)
        button_languages.setStatusTip("Filter Languages")
        button_languages.triggered.connect(self.search_languages)

        button_ratings = QAction("Ratings", self)
        button_ratings.setStatusTip("Filter Age Ratings")
        button_ratings.triggered.connect(self.search_ratings)

        button_tags = QAction("Tags", self)
        button_tags.setStatusTip("Filter Tags")
        button_tags.triggered.connect(self.search_tags)

        # Create Toolbar
        # toolbar = QToolBar("Toolbar")
        # self.addToolBar(toolbar)
        #
        # toolbar.addAction(button_load)
        # toolbar.addAction(button_save)
        # toolbar.addSeparator()
        # toolbar.addAction(button_open)
        # toolbar.addAction(button_edit)
        # toolbar.addSeparator()
        # toolbar.addAction(button_filter)
        # toolbar.addSeparator()

        # Create Menu
        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_new)
        file_menu.addAction(button_load)
        file_menu.addSeparator()
        file_menu.addAction(button_save)
        file_menu.addAction(button_save_as)
        file_menu.addAction(button_reload)
        file_menu.addSeparator()
        file_menu.addAction(button_preferences)

        entry_menu = menu.addMenu("&Entry")
        entry_menu.addAction(button_open)
        entry_menu.addAction(button_edit)

        filter_menu = menu.addMenu("&Filter")
        filter_menu.addAction(button_filter)
        filter_menu.addSeparator()
        filter_menu.addAction(button_authors)
        filter_menu.addAction(button_series)
        filter_menu.addAction(button_languages)
        filter_menu.addAction(button_ratings)
        filter_menu.addAction(button_tags)

        # Create Status Bar
        self.setStatusBar(QStatusBar(self))

        # Create UI
        self.label_dbName = QLabel("Unknown")
        self.input_dbSearchbar = QLineEdit("")
        self.input_dbSearchbar.setPlaceholderText("Search")
        self.input_dbSearchbar.returnPressed.connect(self.search_entries)

        self.list_dbEntries = QListWidget()
        self.list_dbEntries.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.list_dbEntries.itemClicked.connect(self.switch_entry)
        self.list_dbEntries.itemActivated.connect(self.open_entry)
        self.list_dbEntries.itemDoubleClicked.connect(self.open_entry)
        self.list_dbEntries.itemSelectionChanged.connect(self.switch_entry_keyboard)

        self.vbox_db = QVBoxLayout()
        self.vbox_db.addWidget(self.label_dbName)
        self.vbox_db.addWidget(self.input_dbSearchbar)
        self.vbox_db.addWidget(self.list_dbEntries)

        image_entryCover = QPixmap('res/placeholder.png').scaled(int(self.screen.size().width()*0.25),
                                                                 int(self.screen.size().height()*0.25), Qt.KeepAspectRatio)
        self.label_entryCover = QLabel()
        self.label_entryCover.setPixmap(image_entryCover)
        # self.label_entryCover.setScaledContents(True)
        self.label_entryCover.resize(500, 500)

        self.label_entryName = QLabel("Name Unknown")
        self.label_entryFilepath = QLabel("(Path Unknown)")
        self.label_entryFilepath.setWordWrap(True)
        self.label_entryAuthor = QLabel("Author: Unknown")
        self.label_entrySeries = QLabel("Series: Unknown, 0")
        self.label_entryLanguage = QLabel("Language: Unknown [Unrated]")
        self.label_entryRelease = QLabel("Release: Unknown")
        self.label_entryResolution = QLabel("Resolution: 0x0")
        self.label_entryTags = QLabel("[]")
        self.label_entryTags.setWordWrap(True)
        button_entryOpen = QPushButton("Open")
        button_entryOpen.clicked.connect(self.open_entry)
        button_entryEdit = QPushButton("Edit")
        button_entryEdit.clicked.connect(self.edit_entry)
        layout_entry_buttons = QHBoxLayout()
        layout_entry_buttons.addWidget(button_entryOpen)
        layout_entry_buttons.addWidget(button_entryEdit)
        widget_entry_buttons = QWidget()
        widget_entry_buttons.setLayout(layout_entry_buttons)

        self.vbox_entry = QVBoxLayout()
        self.vbox_entry.addWidget(self.label_entryCover)
        self.vbox_entry.addWidget(self.label_entryName)
        self.vbox_entry.addWidget(self.label_entryFilepath)
        self.vbox_entry.addWidget(self.label_entryAuthor)
        self.vbox_entry.addWidget(self.label_entrySeries)
        self.vbox_entry.addWidget(self.label_entryLanguage)
        self.vbox_entry.addWidget(self.label_entryRelease)
        self.vbox_entry.addWidget(self.label_entryResolution)
        self.vbox_entry.addWidget(self.label_entryTags)
        self.vbox_entry.addWidget(widget_entry_buttons)

        hbox_main = QHBoxLayout()
        hbox_main.addLayout(self.vbox_db)
        hbox_main.addLayout(self.vbox_entry)

        # Set the central widget of the Window.
        layout_container = QWidget()
        layout_container.setLayout(hbox_main)
        self.setCentralWidget(layout_container)

    def new_database(self):
        print("New Database")
        db_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        print(db_path)
        name, ok = QInputDialog.getText(self, 'Database Creation', 'Name:')
        if not ok:
            return

        appl_path = db_path+"/"+name+".appl"
        with open(appl_path, "w", encoding="utf-8") as file:
            file.write(name+"\n"+db_path+"/\n\n"+str(DEFAULT_APP_ASSOCIATIONS)+"\n0\n")
        self.database = db.Database(appl_path)
        self.database.load_files()
        self.database.save_as_file(appl_path)
        self.update_ui()

    def load_database(self):
        print("Load Database")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Databases (*.appl)")
        if dialog.exec_():
            filepath = dialog.selectedFiles()[0]
            self.database = db.Database(filepath)
            self.database.clean_entries()
            self.entry = self.database.entries[0]
            self.update_ui()

    def save_database(self):
        print("Save Database")
        self.database.save_as_file(self.database.file_dir)

    def save_as_database(self):
        print("Save As Database")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("Databases (*.appl)")
        dialog.setDirectory(self.database.db_dir)
        if dialog.exec_():
            filepath = dialog.selectedFiles()[0]
            self.database.save_as_file(filepath)

    def reload_database(self):
        print("Reload Database From Disk")
        self.database.load_files()
        self.update_ui()

    def search_entries(self):
        query = self.input_dbSearchbar.text().strip()
        print("Search: " + query)

        if query == "":
            output = self.database.entries
        else:
            output = self.database.search(query)
        self.update_entries_scroll(output)

    def search_filter(self):
        print("Search Filter")
        tag_dialog = FilterDialog(self.database, 0)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            self.search_entries()

    def search_authors(self):
        print("Search Authors")
        tag_dialog = FilterDialog(self.database, 0)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            self.search_entries()

    def search_series(self):
        print("Search Series")
        tag_dialog = FilterDialog(self.database, 1)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            self.search_entries()

    def search_languages(self):
        print("Search Languages")
        tag_dialog = FilterDialog(self.database, 2)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            self.search_entries()

    def search_ratings(self):
        print("Search Age Ratings")
        tag_dialog = FilterDialog(self.database, 3)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            self.search_entries()

    def search_tags(self):
        print("Search Tags")
        tag_dialog = FilterDialog(self.database, 4)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            self.search_entries()

    def open_entry(self):
        print("Open Entry")
        path = self.database.db_dir + self.entry.path
        if "." not in path:
            path = path + "/" + os.listdir(path)[0]
        ext = path[path.rfind(".")+1:].lower()
        print(self.database.app_associations[ext] + " \'" + path + "\'")
        subprocess.call([self.database.app_associations[ext], path])

    def edit_entry(self):
        print("Edit Entry")
        edit_dialog = EditDialog(self.database, self.entry)
        if edit_dialog.exec_():
            self.update_entry_vbox()

    def edit_preferences(self):
        print("Edit Preferences")
        preferences_dialog = PreferencesDialog(self.database)
        if preferences_dialog.exec_():
            self.update_ui()

    def update_ui(self):
        print("Update UI")
        self.input_dbSearchbar.setText("")
        self.label_dbName.setText(self.database.name + " (" + str(self.database.entry_count) + ")")
        self.update_entries_scroll(self.database.entries)
        self.update_entry_vbox()

    def switch_entry(self, entry_item: EntryListing):
        self.entry = entry_item.entry
        self.update_entry_vbox()

    def switch_entry_keyboard(self):
        if len(self.entries) < 1:
            return
        index = self.list_dbEntries.currentIndex().row()
        self.entry = self.entries[index]
        success = self.update_entry_vbox()
        print("entry Updated ", success)

    def update_entry_vbox(self):
        entry = self.entry
        self.label_entryName.setText(entry.name)
        self.label_entryFilepath.setText("(" + entry.path + ")")
        self.label_entryAuthor.setText("Author: " + entry.author)
        self.label_entrySeries.setText("Series: " + entry.series + ", " + str(entry.vol))
        self.label_entryLanguage.setText(entry.language + " [" + entry.age_rating + "]")
        self.label_entryRelease.setText("Release: " + str(entry.release))
        self.label_entryResolution.setText("Resolution: " + str(entry.resolution[0]) + "x" + str(entry.resolution[1]))
        self.label_entryTags.setText("Tags: " + str(entry.tags))

        if os.path.isfile(entry.cover_path):
            image = QPixmap(entry.cover_path).scaled(int(self.screen.size().width()*0.25),
                                                     int(self.screen.size().height()*0.25), Qt.KeepAspectRatio)
            self.label_entryCover.setPixmap(image)
            self.label_entryCover.setScaledContents(True)
            return True

        image = QPixmap("res/placeholder.png").scaled(int(self.screen.size().width()*0.25),
                                                          int(self.screen.size().height()*0.25), Qt.KeepAspectRatio)
        self.label_entryCover.setPixmap(image)
        self.label_entryCover.setScaledContents(True)
        # print("Unknown Cover")
        return False

    def update_entries_scroll(self, entries):
        print("Update Entries")
        self.entries = entries
        print(self.entries)
        self.label_dbName.setText(self.database.name + " (" + str(len(self.entries)) + ")")
        self.list_dbEntries.clear()

        for e in entries:
            widget = EntryListing(self, e)
            self.list_dbEntries.addItem(widget)


#
# Initialize Window
application = QApplication(sys.argv)

with open("style.qss", "r") as file:
    stylesheet = file.read()
    print(stylesheet)
    application.setStyleSheet(stylesheet)

# Create Window
window = MainWindow(application)
window.show()

# Start the Program.
application.exec()