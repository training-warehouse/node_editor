# -*- coding: utf-8 -*-
# Time    : 2020/12/10 20:32
# Author  : LiaoKong
import os
import inspect

from PySide2.QtWidgets import *
from node_editor.node_editor_window import NodeEditorWindow
from node_editor.utils import load_stylesheet

if __name__ == '__main__':
    app = QApplication([])

    window = NodeEditorWindow()
    module_path = os.path.dirname(inspect.getfile(window.__class__))

    load_stylesheet(os.path.join(module_path, 'qss/node_style.css'))

    window.show()

    app.exec_()
