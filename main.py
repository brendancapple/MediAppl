#################
#   MediAppl    #
# Brendan Apple #
#################
#
# Media Organizer for Local Files w/o Changing File Structures
#
#
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QWidget,
    QStatusBar, QAction,
    QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QListWidget, QAbstractItemView,
    QFileDialog, QInputDialog,
)
from functools import partial
import threading
import subprocess
import sys
import os

import src.database as db
import src.qt_util as qt_util
import src.util as util

ENTRY_LISTING_HEIGHT = 60
DEFAULT_APP_ASSOCIATIONS = {"mp3": "vlc", "txt": "vim"}


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):
        super().__init__()
        self.screen = app.primaryScreen()
        self.database: db.Database = db.Database("default.appl")
        self.entries = []
        self.entry: db.Entry = self.database.entries[0]

        self.sorting = int(util.SortingElements.PATH.value)
        self.view: qt_util.EntryView = qt_util.EntryView.COMPACT
        self.lazy_load_bounds = (0, 0)

        self.setWindowTitle("MediAppl")
        self.setWindowIcon(QIcon('res/Icon.png'))

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

        button_export_json = QAction("Export JSON", self)
        button_export_json.setStatusTip("Export current database as a JSON file")
        button_export_json.triggered.connect(self.export_json)

        button_export_csv = QAction("Export CSV", self)
        button_export_csv.setStatusTip("Export current database as a CSV file")
        button_export_csv.triggered.connect(self.export_csv)

        button_clean = QAction("Clean Database", self)
        button_clean.setStatusTip("Remove all files that don't exist on the disk")
        button_clean.setShortcut(QKeySequence("Ctrl+j"))
        button_clean.triggered.connect(self.clean_database)

        button_open = QAction("Open", self)
        button_open.setStatusTip("Open Current Entry")
        button_open.setShortcut(QKeySequence("Ctrl+enter"))
        button_open.triggered.connect(self.open_entry)

        button_delete = QAction("Delete", self)
        button_delete.setStatusTip("Delete Current Entry")
        button_delete.setShortcut(QKeySequence("Del"))
        button_delete.triggered.connect(self.delete_entry)

        button_view_shrink = QAction("Shrink", self)
        button_view_shrink.setStatusTip("Shrink the List Entries")
        button_view_shrink.setShortcut(QKeySequence("Ctrl+["))
        button_view_shrink.triggered.connect(lambda: self.increment_view(-1))

        button_view_grow = QAction("Grow", self)
        button_view_grow.setStatusTip("Grow the List Entries")
        button_view_grow.setShortcut(QKeySequence("Ctrl+]"))
        button_view_grow.triggered.connect(lambda: self.increment_view(1))

        button_view_compact = QAction("Compact", self)
        button_view_compact.setStatusTip("Change to Compact View")
        button_view_compact.triggered.connect(lambda: self.change_view(qt_util.EntryView.COMPACT))

        button_view_icon = QAction("Icon", self)
        button_view_icon.setStatusTip("Change to Icon View")
        button_view_icon.triggered.connect(lambda: self.change_view(qt_util.EntryView.ICON))

        button_view_extended = QAction("Extended", self)
        button_view_extended.setStatusTip("Change to Extended View")
        button_view_extended.triggered.connect(lambda: self.change_view(qt_util.EntryView.EXTENDED))

        button_view_everything = QAction("Everything", self)
        button_view_everything.setStatusTip("Change to Everything View")
        button_view_everything.triggered.connect(lambda: self.change_view(qt_util.EntryView.EVERYTHING))

        button_view_image = QAction("Thumbnail", self)
        button_view_image.setStatusTip("Change to Thumbnail View")
        button_view_image.triggered.connect(lambda: self.change_view(qt_util.EntryView.THUMBNAIL))

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

        button_sort = QAction("Sort", self)
        button_sort.setStatusTip("Sort Entries")
        button_sort.setShortcut(QKeySequence("Ctrl+alt+g"))
        button_sort.triggered.connect(self.sort_entries)

        button_quick_sort = QAction("Quick Sort", self)
        button_quick_sort.setStatusTip("Sort Entries without opening the menu")
        button_quick_sort.setShortcut(QKeySequence("Ctrl+g"))
        button_quick_sort.triggered.connect(self.quick_sort_entries)

        button_reverse = QAction("Reverse", self)
        button_reverse.setStatusTip("Reverse Entries")
        button_reverse.setShortcut(QKeySequence("Ctrl+h"))
        button_reverse.triggered.connect(self.reverse_entries)

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
        file_menu.addAction(button_export_json)
        file_menu.addAction(button_export_csv)
        file_menu.addSeparator()
        file_menu.addAction(button_clean)
        file_menu.addSeparator()
        file_menu.addAction(button_preferences)

        entry_menu = menu.addMenu("&Entry")
        entry_menu.addAction(button_open)
        entry_menu.addAction(button_edit)
        entry_menu.addAction(button_delete)

        view_menu = menu.addMenu("&View")
        view_menu.addAction(button_view_shrink)
        view_menu.addAction(button_view_grow)
        view_menu.addSeparator()
        view_menu.addAction(button_view_compact)
        view_menu.addAction(button_view_icon)
        view_menu.addAction(button_view_extended)
        view_menu.addAction(button_view_everything)
        view_menu.addAction(button_view_image)

        filter_menu = menu.addMenu("&Filter")
        filter_menu.addAction(button_filter)
        filter_menu.addSeparator()
        filter_menu.addAction(button_authors)
        filter_menu.addAction(button_series)
        filter_menu.addAction(button_languages)
        filter_menu.addAction(button_ratings)
        filter_menu.addAction(button_tags)

        sort_menu = menu.addMenu("&Sort")
        sort_menu.addAction(button_sort)
        sort_menu.addAction(button_quick_sort)
        sort_menu.addSeparator()
        sort_menu.addAction(button_reverse)

        # Create Status Bar
        self.setStatusBar(QStatusBar(self))

        # Create UI
        self.label_dbName = QLabel("Unknown")
        self.input_dbSearchbar = QLineEdit("")
        self.input_dbSearchbar.setPlaceholderText("Search")
        self.input_dbSearchbar.returnPressed.connect(self.search_entries)

        self.list_dbEntries = QListWidget()
        self.list_dbEntries.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_dbEntries.setMouseTracking(True)
        self.list_dbEntries.itemActivated.connect(self.open_entry)
        self.list_dbEntries.itemDoubleClicked.connect(self.open_entry)
        self.list_dbEntries.itemSelectionChanged.connect(self.switch_entry_keyboard)
        self.list_dbEntries.itemEntered.connect(self.check_lazy_load)
        qt_util.EntryListing.DEFAULT_COVER = QIcon("res/placeholder.png")
        self.DEFAULT_ICON_SIZE = self.list_dbEntries.iconSize()

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

        self.label_entryName = qt_util.ClickLabel("Name Unknown")
        self.label_entryFilepath = qt_util.ClickLabel("(Path Unknown)")
        self.label_entryAuthor = qt_util.ClickLabel("Author: Unknown")
        self.label_entrySeries = qt_util.ClickLabel("Series: Unknown, 0")
        self.label_entryLanguage = qt_util.ClickLabel("Language: Unknown [Unrated]")
        self.label_entryRelease = qt_util.ClickLabel("Release: Unknown")
        self.label_entryResolution = qt_util.ClickLabel("Resolution: 0x0")
        self.label_entryTags = qt_util.ClickLabel("[]")
        self.label_entryName.setWordWrap(True)
        self.label_entryFilepath.setWordWrap(True)
        self.label_entryAuthor.setWordWrap(True)
        self.label_entrySeries.setWordWrap(True)
        self.label_entryLanguage.setWordWrap(True)
        self.label_entryRelease.setWordWrap(True)
        self.label_entryResolution.setWordWrap(True)
        self.label_entryTags.setWordWrap(True)
        self.label_entryName.clicked.connect(lambda: self.search_selection(0))
        self.label_entryAuthor.clicked.connect(lambda: self.search_selection(1))
        self.label_entrySeries.clicked.connect(lambda: self.search_selection(2))
        self.label_entryLanguage.clicked.connect(lambda: self.search_selection(3))
        # self.label_entryTags.clicked.connect()
        button_entryOpen = QPushButton("Open")
        button_entryOpen.clicked.connect(self.open_entry)
        button_entryEdit = QPushButton("Edit")
        button_entryEdit.clicked.connect(self.edit_entry)
        button_entryDelete = QPushButton("Delete")
        button_entryDelete.clicked.connect(self.delete_entry)
        layout_entry_buttons = QHBoxLayout()
        layout_entry_buttons.addWidget(button_entryOpen)
        layout_entry_buttons.addWidget(button_entryEdit)
        layout_entry_buttons.addWidget(button_entryDelete)
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
        with open(appl_path, "w", encoding="utf-8") as f:
            f.write(name+"\n"+db_path+"/\n\n"+str(DEFAULT_APP_ASSOCIATIONS)+"\n0\n")
        self.database = db.Database(appl_path)
        loading_dialog = qt_util.LoadingDialog(self.database)
        loading_dialog.exec()
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
            self.entry = self.database.entries[0]
            print("pre update")
            self.update_ui()

    def clean_database(self):
        dialog = qt_util.ConfirmationDialog("Are you sure you want to clean the database?\n"
                                            "Any deleted files cannot be recovered.")
        if dialog.exec_():
            print("Clean Database")
            self.database.clean_entries()

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

    def export_json(self):
        print("Export JSON")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("JSON (*.json)")
        dialog.setDirectory(self.database.db_dir)
        if dialog.exec_():
            filepath = dialog.selectedFiles()[0]
            print(filepath)
            self.database.export_json(filepath)

    def export_csv(self):
        print("Export CSV")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("Comma Separated Values (*.csv)")
        dialog.setDirectory(self.database.db_dir)
        if dialog.exec_():
            filepath = dialog.selectedFiles()[0]
            print(filepath)
            self.database.export_csv(filepath)

    def reload_database(self):
        print("Reload Database From Disk")
        loading_dialog = qt_util.LoadingDialog(self.database)
        loading_dialog.exec()
        self.update_ui()

    def search_entries(self):
        query = self.input_dbSearchbar.text().strip()
        print("Search: " + query)

        self.sorting = 0  # Clear Sorting to allow for search relevance ordering

        if query == "":
            self.entries = self.database.entries
            print("empty query")
        else:
            self.entries = self.database.search(query)
            print("searched " + query)
        print("Update entries")
        self.quick_sort_entries()
        print("Updated entries")

    def search_filter(self):
        print("Search Filter")
        tag_dialog = qt_util.FilterDialog(self.database, 0)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(tag_dialog.get_output() + " " + self.input_dbSearchbar.text())
            self.search_entries()

    def search_authors(self):
        print("Search Authors")
        tag_dialog = qt_util.FilterDialog(self.database, 0)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            self.search_entries()

    def search_series(self):
        print("Search Series")
        tag_dialog = qt_util.FilterDialog(self.database, 1)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            self.search_entries()

    def search_languages(self):
        print("Search Languages")
        tag_dialog = qt_util.FilterDialog(self.database, 2)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            self.search_entries()

    def search_ratings(self):
        print("Search Age Ratings")
        tag_dialog = qt_util.FilterDialog(self.database, 3)
        if tag_dialog.exec_():
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            self.search_entries()

    def search_tags(self):
        print("Search Tags")
        tag_dialog = qt_util.FilterDialog(self.database, 4)
        if tag_dialog.exec_():
            print("got string")
            self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + tag_dialog.get_output())
            print("string in searchbar")
            self.search_entries()
            print("searched entries")

    def search_selection(self, category: int):
        match category:
            case 0:
                self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " " + self.entry.name)
            case 1:
                self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " [" + self.entry.author + "]")
            case 2:
                self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " [" + self.entry.series + "]")
            case 3:
                self.input_dbSearchbar.setText(self.input_dbSearchbar.text() + " [" + self.entry.language + "]")

        self.search_entries()

    def sort_entries(self):
        dialog = qt_util.SortDialog(self.sorting)
        if dialog.exec_():
            self.sorting = dialog.get_output()
            print(self.entry.create_sorting_string(self.sorting))
            self.entries.sort(key=lambda e: e.create_sorting_string(self.sorting))
            self.update_entries_scroll()

    def quick_sort_entries(self):
        self.entries.sort(key=lambda e: e.create_sorting_string(self.sorting))
        self.update_entries_scroll()

    def reverse_entries(self):
        self.entries.reverse()
        self.update_entries_scroll()

    def increment_view(self, amount: int):
        val = (self.view.value + amount) % len(qt_util.EntryView)
        self.view = qt_util.EntryView(val)
        self.update_entries_scroll()

    def change_view(self, view: qt_util.EntryView):
        self.view = view
        self.update_entries_scroll()

    def open_entry(self):
        print("Open Entry")
        path = self.database.db_dir + self.entry.path
        if "." not in path:
            path = path + "/" + os.listdir(path)[0]
        ext = path[path.rfind(".")+1:].lower()
        print(self.database.app_associations[ext] + " \'" + path + "\'")
        subprocess.Popen([self.database.app_associations[ext], path])

    def edit_entry(self):
        print("Edit Entry")
        edit_dialog = qt_util.EditDialog(self.database, self.entry)
        if edit_dialog.exec_():
            self.update_entry_vbox()
            self.update_entries_scroll()

    def delete_entry(self):
        dialog = qt_util.ConfirmationDialog("Are you sure you want to delete this entry?\n"
                                            "The file's metadata cannot be recovered.")
        if dialog.exec_():
            print("Delete Entry")
            self.database.entries.remove(self.entry)
            self.update_entry_vbox()
            self.update_entries_scroll()

    def edit_preferences(self):
        print("Edit Preferences")
        preferences_dialog = qt_util.PreferencesDialog(self.database)
        if preferences_dialog.exec_():
            self.update_ui()

    def check_lazy_load(self):
        # print("Check lazy load")
        if self.view == qt_util.EntryView.ICON or self.view == qt_util.EntryView.EVERYTHING or self.view == qt_util.EntryView.THUMBNAIL:
            # print("Load Icons")
            rect = self.list_dbEntries.viewport().contentsRect()
            indices = [self.list_dbEntries.indexAt(rect.topLeft()).row(),
                       self.list_dbEntries.indexAt(rect.bottomLeft()).row()]
            if indices[1] < 0:
                indices[1] = self.list_dbEntries.count()

            if (self.lazy_load_bounds[0] - indices[0]) > 0:
                indices[1] = self.lazy_load_bounds[0]
                self.lazy_load_bounds = (indices[0], self.lazy_load_bounds[1])
            elif (indices[1] - self.lazy_load_bounds[1]) > 0:
                indices[0] = self.lazy_load_bounds[1]
                self.lazy_load_bounds = (self.lazy_load_bounds[0], indices[1])
            else:
                return

            # print(" Bounds: " + str(indices[0]) + " : " + str(indices[1]))
            threading.Thread(target=self.update_icons, args=(indices[0], indices[1])).start()

    def update_icons(self, lower_bound: int, upper_bound: int):
        # print("Recieved Bounds: " + str(lower_bound) + " : " + str(upper_bound))
        for i in range(lower_bound, upper_bound):
            path = self.entries[i].cover_path
            item = self.list_dbEntries.item(i)
            if item is None:
                continue
            if not os.path.exists(path):
                item.setIcon(qt_util.EntryListing.DEFAULT_COVER)
            else:
                item.setIcon(self.entries[i].get_cover_icon(int(self.screen.size().width()/6), int(self.screen.size().height())))

    def update_ui(self):
        print("Update UI")
        self.input_dbSearchbar.setText("")
        self.label_dbName.setText(self.database.name + " (" + str(self.database.entry_count) + ")")
        self.entries = self.database.entries
        self.quick_sort_entries()
        self.update_entry_vbox()

    def switch_entry(self, entry_item: qt_util.EntryListing):
        self.entry = entry_item.entry
        self.update_entry_vbox()

    def switch_entry_keyboard(self):
        if len(self.entries) < 1:
            return
        index = self.list_dbEntries.currentIndex().row()
        self.entry = self.entries[index]
        success = self.update_entry_vbox()
        self.check_lazy_load()
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

    def update_entries_scroll(self):
        if self.entries is None:
            self.entries = self.database.entries
            self.sort_entries()
            print("error no self.entries")

        print("Update Entries")
        print(self.entries)
        self.label_dbName.setText(self.database.name + " (" + str(len(self.entries)) + ")")
        print("Label Updated")
        if len(self.list_dbEntries.children()) > 0:
            print("Attempt clear")
            self.list_dbEntries.clear()
            # print("Entries cleared")
        else:
            print("needn't clear entries")

        match self.view:
            case qt_util.EntryView.THUMBNAIL:
                self.list_dbEntries.setIconSize(QSize(int(self.list_dbEntries.width()/6),
                                                      int(self.list_dbEntries.height()/6)))
                self.list_dbEntries.setSpacing(10)
            case qt_util.EntryView.EVERYTHING:
                self.list_dbEntries.setIconSize(QSize(64, 64))
                self.list_dbEntries.setSpacing(0)
            case _:
                self.list_dbEntries.setIconSize(self.DEFAULT_ICON_SIZE)
                self.list_dbEntries.setSpacing(0)

        self.lazy_load_bounds = (0, 0)

        for e in self.entries:
            widget = qt_util.EntryListing(self, e, self.view)
            self.list_dbEntries.addItem(widget)

        self.check_lazy_load()
        print("entry list updated")


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