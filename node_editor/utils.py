# -*- coding: utf-8 -*-
# Time    : 2020/12/19 18:04
# Author  : LiaoKong
import os
from PySide2.QtCore import *
from PySide2.QtWidgets import *


def load_stylesheet(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        QApplication.instance().setStyleSheet(f.read())


# def load_stylesheet(*args):
#     res = ''
#     for arg in args:
#         file = QFile(arg)
#         file.open(QFile.ReadOnly | QFile.Text)
#         stylesheet = file.readAll()
#
#         res += '\n' + str(stylesheet)
#     print(res)
#     QApplication.instance().setStyleSheet(res)


def load_stylesheet(*args):
    res = ''
    for arg in args:
        with open(os.path.join(os.path.dirname(__file__), arg)) as f:
            res += f.read()

    QApplication.instance().setStyleSheet(res)
