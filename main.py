# -*- coding: utf-8 -*-
# Time    : 2020/12/10 20:32
# Author  : LiaoKong

from PySide2.QtWidgets import *
from node_editor_window import NodeEditorWindow

if __name__ == '__main__':
    app =QApplication([])

    window = NodeEditorWindow()
    window.show()

    app.exec_()


