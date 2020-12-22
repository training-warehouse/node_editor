# -*- coding: utf-8 -*-
# Time    : 2020/12/12 18:31
# Author  : LiaoKong
import math

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from node_editor.node_socket import RIGHT_TOP, RIGHT_BUTTON, LEFT_TOP, LEFT_BUTTON

EDGE_CP_ROUNDNESS = 100


class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super(QDMGraphicsEdge, self).__init__(parent)

        self.edge = edge
        self._last_selected_state = False

        self.pos_source = [0, 0]
        self.pos_destination = [200, 100]

        self.init_assets()
        self.init_ui()

    def init_ui(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def init_assets(self):
        self._color = QColor('#001000')
        self._color_selected = QColor('#00ff00')
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen.setWidthF(2.0)
        self._pen_selected.setWidthF(2.0)
        self._pen_dragging.setWidthF(2.0)

    def on_selected(self):
        print('gr_edge on selected')
        self.edge.scene.gr_scene.item_selected.emit()

    def mouseReleaseEvent(self, event):
        super(QDMGraphicsEdge, self).mouseReleaseEvent(event)
        if self._last_selected_state != self.isSelected():
            self.edge.scene.reset_last_selected_states()
            self._last_selected_state = self.isSelected()
            self.on_selected()

    def set_source(self, x, y):
        self.pos_source = [x, y]

    def set_destination(self, x, y):
        self.pos_destination = [x, y]

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calc_path()

    def intersects_with(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calc_path()
        return cutpath.intersects(path)

    def paint(self, painter, option, widget=None):
        self.setPath(self.calc_path())

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def calc_path(self):
        raise NotImplementedError


class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    def calc_path(self):
        path = QPainterPath(QPointF(self.pos_source[0], self.pos_source[1]))
        path.lineTo(self.pos_destination[0], self.pos_destination[1])
        return path


class QDMGraphicsEdgeBezier(QDMGraphicsEdge):
    def calc_path(self):
        s = self.pos_source
        d = self.pos_destination
        dist = (d[0] - s[0]) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.edge.start_socket is not None:
            sspos = self.edge.start_socket.position
            if s[0] > d[0] and sspos in (RIGHT_TOP, RIGHT_BUTTON) or (s[0] < d[0] and sspos in (LEFT_TOP, LEFT_BUTTON)):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = ((s[1] - d[1]) / math.fabs(s[1] - d[1]) if s[1] - d[1] != 0 else 0.00001) * EDGE_CP_ROUNDNESS
                cpy_s = ((d[1] - s[1]) / math.fabs(d[1] - s[1]) if d[1] - s[1] != 0 else 0.00001) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.pos_source[0], self.pos_source[1]))
        path.cubicTo(s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d,
                     self.pos_destination[0], self.pos_destination[1])
        return path
