# -*- coding: utf-8 -*-
# Time    : 2020/12/12 16:43
# Author  : LiaoKong
from collections import OrderedDict

from PySide2.QtWidgets import *

from node_derializable import Serializable


class QDMNodeContentWidget(QWidget, Serializable):
    def __init__(self, node, parent=None):
        super(QDMNodeContentWidget, self).__init__(parent)
        self.node = node
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.wdg_label = QLabel('Some title')
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QDMTextEdit('foo'))

    def set_editing_flag(self, value):
        self.node.scene.gr_scene.views()[0].editing_flag = value

    def serialize(self):
        return OrderedDict([])

    def deserialize(self, data, hashmap=None):
        return False


class QDMTextEdit(QTextEdit):
    def focusInEvent(self, e):
        self.parentWidget().set_editing_flag(True)
        super(QDMTextEdit, self).focusInEvent(e)

    def focusOutEvent(self, e):
        self.parentWidget().set_editing_flag(False)
        super(QDMTextEdit, self).focusOutEvent(e)
