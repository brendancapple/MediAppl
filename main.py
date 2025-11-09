#################
#   MediAppl    #
# Brendan Apple #
#################
#
# Media Organizer for Local Files w/o Changing File Structures
#
#
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QWidget,
    QStatusBar, QToolBar, QAction,
    QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QCheckBox, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem,
    QFileDialog, QInputDialog
)
import sys
import os

import database as db

ENTRY_LISTING_HEIGHT = 60
DEFAULT_APP_ASSOCIATIONS = {"mp3": "vlc", "txt": "vim"}


class EntryListing(QListWidgetItem):
    def __init__(self, main_window, entry: db.Entry):
        super().__init__()
        self.mw = main_window
        self.entry = entry

        self.setText("[" + self.entry.age_rating + "] " + self.entry.author + ": " + self.entry.name)
        # self.clickedItem.connect(self.on_click)
        # self.button.setFixedHeight(ENTRY_LISTING_HEIGHT)

        # layout = QVBoxLayout()
        # layout.addWidget(self.button)
        # self.setLayout(layout)
        # self.show()

    # def on_click(self):
        # self.mw.entry = self.entry
        # self.mw.update_entry_vbox()


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):
        super().__init__()
        self.database: db.Database = db.Database("test.appl")
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

        # Create Toolbar
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction(button_load)
        toolbar.addAction(button_save)

        # Create Menu
        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_new)
        file_menu.addAction(button_load)
        file_menu.addAction(button_save)
        file_menu.addAction(button_reload)

        entry_menu = menu.addMenu("&Entry")
        entry_menu.addAction(button_open)
        entry_menu.addAction(button_edit)

        # Create Status Bar
        self.setStatusBar(QStatusBar(self))

        # Create UI
        button = QPushButton("Press Me!")
        button.setCheckable(True)
        button.clicked.connect(self.the_button_was_clicked)

        self.label_dbName = QLabel("Unknown")
        self.input_dbSearchbar = QLineEdit("")
        self.input_dbSearchbar.setPlaceholderText("Search")
        self.input_dbSearchbar.returnPressed.connect(self.search_entries)

        self.list_dbEntries = QListWidget()
        self.list_dbEntries.itemClicked.connect(self.switch_entry)

        self.vbox_db = QVBoxLayout()
        self.vbox_db.addWidget(self.label_dbName)
        self.vbox_db.addWidget(self.input_dbSearchbar)
        self.vbox_db.addWidget(self.list_dbEntries)

        image_entryCover = QPixmap('res/placeholder.png')
        self.label_entryCover = QLabel()
        self.label_entryCover.setPixmap(image_entryCover)
        self.label_entryCover.setScaledContents(True)
        self.label_entryCover.resize(500, 500)

        self.label_entryName = QLabel("Name Unknown")
        self.label_entryFilepath = QLabel("(Path Unknown)")
        self.label_entryAuthor = QLabel("Author: Unknown")
        self.label_entrySeries = QLabel("Series: Unknown, 0")
        self.label_entryLanguage = QLabel("Language: Unknown [Unrated]")
        self.label_entryRelease = QLabel("Release: Unknown")
        self.label_entryResolution = QLabel("Resolution: 0x0")
        self.label_entryTags = QLabel("[]")
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

    def the_button_was_clicked(self):
        print("button!")

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

    def load_database(self):
        print("Load Database")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Databases (*.appl)")
        if dialog.exec_():
            filepath = dialog.selectedFiles()[0]
            self.database = db.Database(filepath)
            self.entry = self.database.entries[0]
            self.update_ui()

    def save_database(self):
        print("Save Database")
        dialoge = QFileDialog(self)
        dialoge.setFileMode(QFileDialog.FileMode.AnyFile)
        dialoge.setNameFilter("Databases (*.appl)")
        if dialoge.exec_():
            filepath = dialoge.selectedFiles()[0]
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

    def open_entry(self):
        print("Open Entry")

    def edit_entry(self):
        print("Edit Entry")

    def update_ui(self):
        print("Update UI")
        self.input_dbSearchbar.setText("")
        self.label_dbName.setText(self.database.name)
        self.update_entries_scroll(self.database.entries)
        self.update_entry_vbox()

    def switch_entry(self, entry_item: EntryListing):
        self.entry = entry_item.entry
        self.update_entry_vbox()

    def update_entry_vbox(self):
        entry = self.entry
        if os.path.isfile(entry.cover_path):
            image = QPixmap(entry.cover_path)
            self.label_entryCover.setPixmap(image)
        else:
            print("Unknown Cover")
        self.label_entryName.setText(entry.name)
        self.label_entryFilepath.setText("(" + entry.path + ")")
        self.label_entryAuthor.setText("Author:" + entry.author)
        self.label_entrySeries.setText("Series: " + entry.series + ", " + str(entry.vol))
        self.label_entryLanguage.setText(entry.language + "[" + entry.age_rating + "]")
        self.label_entryRelease.setText(str(entry.release))
        self.label_entryResolution.setText("Resolution: " + str(entry.resolution[0]) + "x" + str(entry.resolution[1]))
        self.label_entryTags.setText("Tags: " + str(entry.tags))

    def update_entries_scroll(self, entries):
        self.list_dbEntries.clear()

        for e in entries:
            widget = EntryListing(self, e)
            self.list_dbEntries.addItem(widget)


#
# Initialize Window
application = QApplication(sys.argv)

# Create Window
window = MainWindow(application)
window.show()

# Start the Program.
application.exec()