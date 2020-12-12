# -*- coding: utf-8 -*-
# Time    : 2020/12/10 20:34
# Author  : LiaoKong
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from node_graphics_scene import QDMGraphicsScene
from node_graphics_view import QDMGraphicsView


class NodeEditorWind(QWidget):
    def __int__(self, parent=None):
        super(NodeEditorWind, self).__int__(parent)

    def init_ui(self):
        self.setGeometry(200, 200, 800, 600)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.gr_scene = QDMGraphicsScene()

        self.view = QDMGraphicsView(self.gr_scene, self)
        self.layout.addWidget(self.view)

        self.setWindowTitle('Node Editor')
        self.show()

        self.add_debug_content()

    def add_debug_content(self):
        """绘制节点测试"""
        green_brush = QBrush(Qt.green)
        outline_pen = QPen(Qt.black)
        outline_pen.setWidth(2)

        rect = self.gr_scene.addRect(-100, -100, 80, 100, outline_pen, green_brush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.gr_scene.addText("Hello Node!", QFont('Ubuntu'))
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1.0, 1.0, 1.0))

        widget1 = QPushButton('hello world')
        proxy1 = self.gr_scene.addWidget(widget1)
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 30)

        widget2 = QLineEdit()
        proxy2 = self.gr_scene.addWidget(widget2)
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setPos(0, 60)

        line = self.gr_scene.addLine(-200, -200, 400, -100, outline_pen)
        line.setFlag(QGraphicsItem.ItemIsMovable)
        line.setFlag(QGraphicsItem.ItemIsSelectable)
