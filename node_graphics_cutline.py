# -*- coding: utf-8 -*-
# Time    : 2020/12/13 17:24
# Author  : LiaoKong
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *


class QDMCutLine(QGraphicsItem):
    def __init__(self, parent=None):
        super(QDMCutLine, self).__init__(parent)

        self.line_points = []

        self._pen = QPen(Qt.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)

    def boundingRect(self):
        return QRectF(0, 0, 1, 1)

    def paint(self, painter, option, widget=None):
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)
