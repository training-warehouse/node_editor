# -*- coding: utf-8 -*-
# Time    : 2020/12/10 20:32
# Author  : LiaoKong

from PySide2.QtWidgets import *
from node_editor_wnd import NodeEditorWind

if __name__ == '__main__':
    app =QApplication([])

    window = NodeEditorWind()
    window.init_ui()

    app.exec_()


