# -*- coding: utf-8 -*-
# Time    : 2020/12/12 16:43
# Author  : LiaoKong
from PySide2.QtWidgets import *


class QDMNodeContentWidget(QWidget):
    def __init__(self, parent=None):
        super(QDMNodeContentWidget, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.wdg_label = QLabel('Some title')
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QTextEdit('foo'))
