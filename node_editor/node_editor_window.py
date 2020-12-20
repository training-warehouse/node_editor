# -*- coding: utf-8 -*-
# Time    : 2020/12/15 20:31
# Author  : LiaoKong
import json
import os

from PySide2.QtWidgets import *
from PySide2.QtCore import *

from node_editor.node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super(NodeEditorWindow, self).__init__(parent)

        self.name_company = 'LiaoKong'
        self.name_product = 'NodeEditor'

        self.init_ui()

    def init_ui(self):
        self.create_actions()
        self.create_menus()

        self.node_editor = NodeEditorWidget(self)
        self.node_editor.scene.add_has_been_modified_listeners(self.set_title)
        self.setCentralWidget(self.node_editor)

        self.setGeometry(200, 200, 800, 600)

        self.set_title()
        self.show()

    def create_status_bar(self):
        self.statusBar().showMessage('')
        self.status_mouse_pos = QLabel('')
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        self.node_editor.view.scenePosChanged.connect(self.on_scene_pos_changed)

    def create_menus(self):
        menubar = self.menuBar()

        self.file_menu = menubar.addMenu('&File')
        self.file_menu.addAction(self.action_new)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_open)
        self.file_menu.addAction(self.action_save)
        self.file_menu.addAction(self.action_save_as)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_exit)

        self.edit_menu = menubar.addMenu('&Edit')
        self.edit_menu.addAction(self.action_undo)
        self.edit_menu.addAction(self.action_redo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_cut)
        self.edit_menu.addAction(self.action_copy)
        self.edit_menu.addAction(self.action_paste)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_del)

    def create_actions(self):
        self.action_new = QAction('&New', self, shortcut='Ctrl+N', statusTip='Create New Graph', triggered=self.on_file_new)
        self.action_open = QAction('&Open', self, shortcut='Ctrl+O', statusTip='Open File', triggered=self.on_file_open)
        self.action_save = QAction('&Save', self, shortcut='Ctrl+S', statusTip='Save File', triggered=self.on_file_save)
        self.action_save_as = QAction('Save &As...', self, shortcut='Ctrl+Shift+S', statusTip='Save File As...',
                                      triggered=self.on_file_save_as)
        self.action_exit = QAction('&Exit', self, shortcut='Ctrl+Q', statusTip='Exit', triggered=self.close)

        self.action_undo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip='Undo Last Operation',
                                   triggered=self.on_edit_undo)
        self.action_redo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', statusTip='Redo Last Operation',
                                   triggered=self.on_edit_redo)
        self.action_cut = QAction('&Cut', self, shortcut='Ctrl+X', statusTip='Cut to clipboard', triggered=self.on_edit_cut)
        self.action_copy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip='Copy to clipboard', triggered=self.on_edit_copy)
        self.action_paste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip='Paste from clipboard',
                                    triggered=self.on_edit_paste)
        self.action_del = QAction('&Delete', self, shortcut='Del', statusTip='Delete Selected Items', triggered=self.on_edit_del)

    def set_title(self):
        title = 'Node Editor - '
        title += self.node_editor.get_user_friendly_filename()

        self.setWindowTitle(title)

    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

    def is_modified(self):
        return self.get_current_node_editor_widget().scene.has_been_modified

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
            self.get_current_node_editor_widget().scene.clear()
            self.filename = None
            self.set_title()

    def get_current_node_editor_widget(self):
        return self.centralWidget()

    def on_file_open(self):
        if self.maybe_save():
            filename, file_filter = QFileDialog.getOpenFileName(self, 'Open graph form file')
            if not filename:
                return
            if os.path.isfile(filename):
                self.get_current_node_editor_widget().scene.load_from_file(filename)
                self.filename = filename
                self.set_title()

    def on_file_save(self):
        if not self.filename:
            return self.on_file_save_as()
        self.get_current_node_editor_widget().scene.save_to_file(self.filename)
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
        self.get_current_node_editor_widget().scene.history.undo()

    def on_edit_redo(self):
        self.get_current_node_editor_widget().scene.history.redo()

    def on_edit_del(self):
        self.get_current_node_editor_widget().scene.gr_scene.views()[0].delete_selected()

    def on_edit_cut(self):
        data = self.get_current_node_editor_widget().scene.clipboard.serialize_selected(delete=True)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def on_edit_copy(self):
        data = self.get_current_node_editor_widget().scene.clipboard.serialize_selected(delete=False)
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

        self.get_current_node_editor_widget().scene.clipboard.deserialize_from_clipboard(data)

    def read_settings(self):
        settings = QSettings(self.name_company, self.name_product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def write_settings(self):
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
