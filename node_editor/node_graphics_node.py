# -*- coding: utf-8 -*-
# Time    : 2020/12/12 15:31
# Author  : LiaoKong
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *


class QDMGraphicsNode(QGraphicsItem):
    def __init__(self, node, parent=None):
        super(QDMGraphicsNode, self).__init__(parent)
        self.node = node
        self.content = self.node.content
        self._was_moved = False
        self._last_selected_state = False

        self.init_sizes()
        self.init_assets()

        self.init_ui()

    def init_sizes(self):
        self.width = 180
        self.height = 240
        self.edge_size = 10.0
        self.title_height = 24.0
        self._padding = 5.0

    def init_assets(self):
        self._title_color = Qt.white
        self._title_font = QFont('Ubuntu', 10)

        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor('#FFFFA637'))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor('#E3212121'))

    def init_ui(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.init_title()
        self.title = self.node.title

        self.init_sockets()
        self.init_content()

    def init_title(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self._padding)

    def init_sockets(self):
        pass

    def init_content(self):
        self.gr_content = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.edge_size, self.title_height + self.edge_size,
                                 self.width - 2 * self.edge_size, self.height - 2 * self.edge_size - self.title_height)
        self.gr_content.setWidget(self.content)

    def on_selected(self):
        self.node.scene.gr_scene.item_selected.emit()

    def mouseMoveEvent(self, event):
        super(QDMGraphicsNode, self).mouseMoveEvent(event)

        for node in self.scene().scene.nodes:
            if node.gr_node.isSelected():
                node.update_connected_edges()
        self._was_moved = True

    def mouseReleaseEvent(self, event):
        super(QDMGraphicsNode, self).mouseReleaseEvent(event)

        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.store_history('Node Move', set_modified=True)

            self.node.scene.reset_last_selected_states()
            self._last_selected_state = True

            self.node.scene._last_selected_items = self.node.scene.get_selected_items()
            return

        if self._last_selected_state != self.isSelected() or self.node.scene._last_selected_items != self.node.scene.get_selected_items():
            self.node.scene.reset_last_selected_states()
            self._last_selected_state = self.isSelected()
            self.on_selected()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def paint(self, painter, style_option_graphics_item, widget=None):
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size, self.edge_size,
                           self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size,
                                    self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height).normalized()
