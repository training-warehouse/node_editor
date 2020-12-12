# -*- coding: utf-8 -*-
# Time    : 2020/12/10 21:42
# Author  : LiaoKong
from PySide2.QtWidgets import QGraphicsView
from PySide2.QtGui import *
from PySide2.QtCore import *

from node_graphics_socket import QDMGraphicsSocket

MODE_NOOP = 1
MODE_EDGE_DRAG = 2

EDGE_DRAG_START_THRESHOLD = 10


class QDMGraphicsView(QGraphicsView):
    def __init__(self, gr_scene, parent=None):
        super(QDMGraphicsView, self).__init__(parent)

        self.gr_scene = gr_scene
        self.init_ui()

        self.setScene(self.gr_scene)

        self.mode = MODE_NOOP

        self.zoom_in_factor = 1.25
        self.zoom_clamp = True
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = [0, 10]

    def init_ui(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            # 设置中间平移背景
            self.middle_mouse_button_press(event)
        elif event.button() == Qt.LeftButton:
            self.left_mouse_button_press(event)
        elif event.button() == Qt.RightButton:
            self.right_mouse_button_press(event)
        else:
            super(QDMGraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middle_mouse_button_release(event)
        elif event.button() == Qt.LeftButton:
            self.left_mouse_button_release(event)
        elif event.button() == Qt.RightButton:
            self.right_mouse_button_release(event)
        else:
            super(QDMGraphicsView, self).mouseReleaseEvent(event)

    def middle_mouse_button_press(self, event):
        release_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                    Qt.LeftButton, Qt.NoButton, event.modifiers())
        super(QDMGraphicsView, self).mouseReleaseEvent(release_event)

        self.setDragMode(QGraphicsView.ScrollHandDrag)

        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                 Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super(QDMGraphicsView, self).mousePressEvent(fake_event)

    def middle_mouse_button_release(self, event):
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                 Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super(QDMGraphicsView, self).mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.NoDrag)

    def left_mouse_button_press(self, event):
        item = self.get_item_at_click(event)
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

        if isinstance(item, QDMGraphicsSocket):
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edge_drag_start(item)
                return

        if self.mode == MODE_EDGE_DRAG:
            res = self.edge_drag_end(item)
            if res: return

        super(QDMGraphicsView, self).mousePressEvent(event)

    def edge_drag_start(self, item):
        print('start dragging edge')
        print('assign start socket')

    def edge_drag_end(self, item):
        self.mode = MODE_NOOP
        print('end dragging edge')

        if isinstance(item, QDMGraphicsSocket):
            print('assign end socket')
            return True

        return False

    def distance_between_click_and_release_is_off(self, event):
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        # fixme 这里是不是应该可以直接用press item和release item对比
        # fixme 而且socket是不是应该分类两种类型（input output），input类型的不能连input，output类型的不能连output
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD * EDGE_DRAG_START_THRESHOLD
        return (dist_scene.x() * dist_scene.x() + dist_scene.y() * dist_scene.y()) > edge_drag_threshold_sq

    def left_mouse_button_release(self, event):
        item = self.get_item_at_click(event)
        if self.mode == MODE_EDGE_DRAG:

            if self.distance_between_click_and_release_is_off(event):
                res = self.edge_drag_end(item)
                if res: return

        super(QDMGraphicsView, self).mouseReleaseEvent(event)

    def right_mouse_button_press(self, event):
        return super(QDMGraphicsView, self).mousePressEvent(event)

    def right_mouse_button_release(self, event):
        return super(QDMGraphicsView, self).mouseReleaseEvent(event)

    def get_item_at_click(self, event):
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def wheelEvent(self, event):
        """设置滚轮缩放"""
        zoom_out_factor = 1 / self.zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step

        clamped = False
        if self.zoom < self.zoom_range[0]: self.zoom, clamped = self.zoom_range[0], True
        if self.zoom > self.zoom_range[-1]: self.zoom, clamped = self.zoom_range[-1], True

        if not clamped or not self.zoom_clamp:
            self.scale(zoom_factor, zoom_factor)
