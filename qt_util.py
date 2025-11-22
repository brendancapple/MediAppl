from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import QLayout, QPushButton, QSizePolicy, QWidget, QLabel, QTextEdit, QVBoxLayout, QDialog, \
    QDialogButtonBox, QScrollArea, QTabWidget, QLineEdit, QHBoxLayout, QFileDialog, QListWidgetItem
from functools import partial

import database as db


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margin, _, _, _ = self.getContentsMargins()

        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()

class EntryListing(QListWidgetItem):
    def __init__(self, main_window, entry: db.Entry):
        super().__init__()
        self.mw = main_window
        self.entry = entry

        self.setText("[" + self.entry.age_rating + "] " + self.entry.author + ": " + self.entry.name)


class ClickLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, ev):
        self.clicked.emit()

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
                                                                                .replace("\"", "")
                                                                                .replace("'", "").split("\n"))}
        self.database.app_associations = dict_apps
        self.database.save_as_file(self.database.file_dir)
        self.accept()


class FilterDialog(QDialog):
    def __init__(self, database: db.Database, start_tab: int, parent=None):
        super().__init__(parent)
        self.database = database

        self.authors = list(self.database.authors.keys())
        self.authors.sort()
        self.series = list(self.database.series.keys())
        self.series.sort()
        self.languages = list(self.database.languages.keys())
        self.languages.sort()
        self.ratings = list(self.database.age_ratings.keys())
        self.ratings.sort()
        self.tags = list(self.database.tags.keys())
        self.tags.sort()

        self.output = set()

        self.setWindowTitle("Filter")
        self.setFixedWidth(720)
        self.setFixedHeight(460)

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

        scroll_author = QScrollArea()
        widget_author = QWidget()
        widget_author.setObjectName("tags_tab")
        widget_author.setMinimumWidth(650)
        layout_author = FlowLayout()
        for key in self.authors:
            button_key = QPushButton(key)
            button_key.setCheckable(True)
            button_key.clicked.connect(partial(self.toggle_output, key))
            layout_author.addWidget(button_key)
        widget_author.setLayout(layout_author)
        scroll_author.setWidget(widget_author)

        scroll_series = QScrollArea()
        widget_series = QWidget()
        widget_series.setObjectName("tags_tab")
        widget_series.setMinimumWidth(650)
        layout_series = FlowLayout()
        for key in self.series:
            button_key = QPushButton(key)
            button_key.setCheckable(True)
            button_key.clicked.connect(partial(self.toggle_output, key))
            layout_series.addWidget(button_key)
        widget_series.setLayout(layout_series)
        scroll_series.setWidget(widget_series)

        scroll_languages = QScrollArea()
        widget_languages = QWidget()
        widget_languages.setObjectName("tags_tab")
        widget_languages.setMinimumWidth(650)
        layout_languages = FlowLayout()
        for key in self.languages:
            button_key = QPushButton(key)
            button_key.setCheckable(True)
            button_key.clicked.connect(partial(self.toggle_output, key))
            layout_languages.addWidget(button_key)
        widget_languages.setLayout(layout_languages)
        scroll_languages.setWidget(widget_languages)

        scroll_ratings = QScrollArea()
        widget_ratings = QWidget()
        widget_ratings.setObjectName("tags_tab")
        widget_ratings.setMinimumWidth(650)
        layout_ratings = FlowLayout()
        for key in self.ratings:
            button_key = QPushButton(key)
            button_key.setCheckable(True)
            button_key.clicked.connect(partial(self.toggle_output, key))
            layout_ratings.addWidget(button_key)
        widget_ratings.setLayout(layout_ratings)
        scroll_ratings.setWidget(widget_ratings)

        scroll_tags = QScrollArea()
        widget_tags = QWidget()
        widget_tags.setObjectName("tags_tab")
        widget_tags.setMinimumWidth(650)
        layout_tags = FlowLayout()
        for key in self.tags:
            button_key = QPushButton(key)
            button_key.setCheckable(True)
            button_key.clicked.connect(partial(self.toggle_output, key))
            layout_tags.addWidget(button_key)
        widget_tags.setLayout(layout_tags)
        scroll_tags.setWidget(widget_tags)

        tab_author = QWidget()
        tab_author.setObjectName("tags_tab")
        tab_layout_author = QVBoxLayout()
        tab_layout_author.addWidget(label_author)
        tab_layout_author.addWidget(scroll_author)
        tab_author.setLayout(tab_layout_author)

        tab_series = QWidget()
        tab_series.setObjectName("tags_tab")
        tab_layout_series = QVBoxLayout()
        tab_layout_series.addWidget(label_series)
        tab_layout_series.addWidget(scroll_series)
        tab_series.setLayout(tab_layout_series)

        tab_languages = QWidget()
        tab_languages.setObjectName("tags_tab")
        tab_layout_languages = QVBoxLayout()
        tab_layout_languages.addWidget(label_language)
        tab_layout_languages.addWidget(scroll_languages)
        tab_languages.setLayout(tab_layout_languages)

        tab_ratings = QWidget()
        tab_ratings.setObjectName("tags_tab")
        tab_layout_ratings = QVBoxLayout()
        tab_layout_ratings.addWidget(label_rating)
        tab_layout_ratings.addWidget(scroll_ratings)
        tab_ratings.setLayout(tab_layout_ratings)

        tab_tags = QWidget()
        tab_tags.setObjectName("tags_tab")
        tab_layout_tags = QVBoxLayout()
        tab_layout_tags.addWidget(label_tag)
        tab_layout_tags.addWidget(scroll_tags)
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
