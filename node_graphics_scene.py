# -*- coding: utf-8 -*-
# Time    : 2020/12/10 20:42
# Author  : LiaoKong
import math

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *


class QDMGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(QDMGraphicsScene, self).__init__(parent)

        self.grid_size = 20
        self.grid_squares = 5

        self._color_background = QColor('#393939')
        self._color_light = QColor('#2f2f2f')
        self._color_dark = QColor('#292929')

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)

        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.scene_width, self.scene_height = 64000, 64000
        self.setSceneRect(-self.scene_width // 2, -self.scene_height // 2, self.scene_width, self.scene_height)

        self.setBackgroundBrush(self._color_background)

    def drawBackground(self, painter, rect):
        # 设置背景网格
        super(QDMGraphicsScene, self).drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            (lines_light.append(QLine(x, top, x, bottom)) if x % (self.grid_size * self.grid_squares) != 0
             else lines_dark.append(QLine(x, top, x, bottom)))

        for y in range(first_top, bottom, self.grid_size):
            (lines_light.append(QLine(left, y, right, y)) if y % (self.grid_size * self.grid_squares) != 0
             else lines_dark.append(QLine(left, y, right, y)))

        painter.setPen(self._pen_light)
        painter.drawLines(lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(lines_dark)
