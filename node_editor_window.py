# -*- coding: utf-8 -*-
# Time    : 2020/12/15 20:31
# Author  : LiaoKong
import json
import os

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super(NodeEditorWindow, self).__init__(parent)
        self.filename = None

        self.init_ui()

    def create_act(self, name, shortcut, tooltip, callback):
        act = QAction(name, self)
        act.setShortcut(shortcut)
        act.setToolTip(tooltip)
        act.triggered.connect(callback)
        return act

    def init_ui(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('&File')
        file_menu.addAction(self.create_act('&New', 'Ctrl+N', 'Create New Graph', self.on_file_new))
        file_menu.addSeparator()
        file_menu.addAction(self.create_act('&Open', 'Ctrl+O', 'Open File', self.on_file_open))
        file_menu.addAction(self.create_act('&Save', 'Ctrl+S', 'Save File', self.on_file_save))
        file_menu.addAction(self.create_act('Save &As...', 'Ctrl+Shift+S', 'Save File As...', self.on_file_save_as))
        file_menu.addSeparator()
        file_menu.addAction(self.create_act('&Exit', 'Ctrl+Q', 'Exit', self.close))

        edit_menu = menubar.addMenu('&Edit')
        edit_menu.addAction(self.create_act('&Undo', 'Ctrl+Z', 'Undo Last Operation', self.on_edit_undo))
        edit_menu.addAction(self.create_act('&Redo', 'Ctrl+Shift+Z', 'Redo Last Operation', self.on_edit_redo))
        edit_menu.addSeparator()
        edit_menu.addAction(self.create_act('&Cut', 'Ctrl+X', 'Cut to clipboard', self.on_edit_cut))
        edit_menu.addAction(self.create_act('&Copy', 'Ctrl+C', 'Copy to clipboard', self.on_edit_copy))
        edit_menu.addAction(self.create_act('&Paste', 'Ctrl+V', 'Paste from clipboard', self.on_edit_paste))
        edit_menu.addSeparator()
        edit_menu.addAction(self.create_act('&Delete', 'Del', 'Delete Selected Items', self.on_edit_del))

        node_editor = NodeEditorWidget(self)
        node_editor.scene.add_has_been_modified_listeners(self.change_title)
        self.setCentralWidget(node_editor)

        self.statusBar().showMessage('')
        self.status_mouse_pos = QLabel('')
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        node_editor.view.scenePosChanged.connect(self.on_scene_pos_changed)

        self.setGeometry(200, 200, 800, 600)

        self.change_title()
        self.show()

    def change_title(self):
        title = 'Node Editor - '
        if self.filename is None:
            title += "New"
        else:
            title += os.path.basename(self.filename)

        if self.centralWidget().scene.has_been_modified:
            title += '*'

        self.setWindowTitle(title)

    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

    def is_modified(self):
        return self.centralWidget().scene.has_been_modified

    def maybe_save(self):
        if not self.is_modified():
            return True
        res = QMessageBox.warning(self, 'About to loose your work?',
                                  'The document has been modified.\n Do you want to save your changes?',
                                  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if res == QMessageBox.Save:
            return self.on_file_save()
        elif res == QMessageBox.Cancel:
            return False

        return True

    def on_scene_pos_changed(self, x, y):
        self.status_mouse_pos.setText('ScenePos： [{}, {}]'.format(x, y))

    def on_file_new(self):
        if self.maybe_save():
            self.centralWidget().scene.clear()
            self.filename = None
            self.change_title()

    def on_file_open(self):
        if self.maybe_save():
            filename, file_filter = QFileDialog.getOpenFileName(self, 'Open graph form file')
            if not filename:
                return
            if os.path.isfile(filename):
                self.centralWidget().scene.load_from_file(filename)
                self.filename = filename
                self.change_title()

    def on_file_save(self):
        if not self.filename:
            return self.on_file_save_as()
        self.centralWidget().scene.save_to_file(self.filename)
        self.statusBar().showMessage('Successfully saved ' + self.filename)
        return True

    def on_file_save_as(self):
        filename, file_filter = QFileDialog.getSaveFileName(self, 'Save graph form file')
        if not filename:
            return False

        self.filename = filename
        self.on_file_save()
        return True

    def on_edit_undo(self):
        self.centralWidget().scene.history.undo()

    def on_edit_redo(self):
        self.centralWidget().scene.history.redo()

    def on_edit_del(self):
        self.centralWidget().scene.gr_scene.views()[0].delete_selected()

    def on_edit_cut(self):
        data = self.centralWidget().scene.clipboard.serialize_selected(delete=True)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def on_edit_copy(self):
        data = self.centralWidget().scene.clipboard.serialize_selected(delete=False)
        str_data = json.dumps(data, indent=4)
        print(str_data)
        QApplication.instance().clipboard().setText(str_data)

    def on_edit_paste(self):
        raw_data = QApplication.instance().clipboard().text()
        try:
            data = json.loads(raw_data)
        except ValueError as e:
            return

        if 'nodes' not in data:
            return

        self.centralWidget().scene.clipboard.deserialize_from_clipboard(data)
