# -*- coding: utf-8 -*-
# Time    : 2020/12/10 20:34
# Author  : LiaoKong
import os

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from node_graphics_view import QDMGraphicsView
from node_node import Node
from node_edge import *
from node_scene import Scene


class NodeEditorWind(QWidget):
    def __init__(self, parent=None):
        super(NodeEditorWind, self).__init__(parent)

        self.stylesheet_filename = 'qss/node_style.css'
        self.load_stylesheet(self.stylesheet_filename)

        self.init_ui()

    def init_ui(self):
        self.setGeometry(200, 200, 800, 600)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scene = Scene()
        # self.gr_scene = self.scene.gr_scene

        self.add_nodes()

        self.view = QDMGraphicsView(self.scene.gr_scene, self)
        self.layout.addWidget(self.view)

        self.setWindowTitle('Node Editor')
        self.show()

        # self.add_debug_content()

    def add_nodes(self):
        node1 = Node(self.scene, "My Awesome Node1", inputs=[1, 2, 3], outputs=[1])
        node2 = Node(self.scene, "My Awesome Node2", inputs=[1, 2, 3], outputs=[1])
        node3 = Node(self.scene, "My Awesome Node3", inputs=[1, 2, 3], outputs=[1])
        node1.set_pos(-350, -250)
        node2.set_pos(-75, 0)
        node3.set_pos(200, -150)

        edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[0], EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[0], EDGE_TYPE_BEZIER)

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

    def load_stylesheet(self, filename):
        with open(os.path.join(os.path.dirname(__file__), filename)) as f:
            QApplication.instance().setStyleSheet(f.read())
