# -*- coding: utf-8 -*-
# Time    : 2020/12/19 16:52
# Author  : LiaoKong
from PySide2.QtCore import *

from node_editor.node_editor_widget import NodeEditorWidget


class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self, parent=None):
        super(CalculatorSubWindow, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.set_title()

        self.scene.add_has_been_modified_listeners(self.set_title)

    def set_title(self):
        self.setWindowTitle(self.get_user_friendly_filename())
