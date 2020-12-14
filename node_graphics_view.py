# -*- coding: utf-8 -*-
# Time    : 2020/12/10 21:42
# Author  : LiaoKong
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from node_edge import EDGE_TYPE_BEZIER, Edge, QDMGraphicsEdge
from node_graphics_cutline import QDMCutLine
from node_graphics_socket import QDMGraphicsSocket

MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3

EDGE_DRAG_START_THRESHOLD = 10


class QDMGraphicsView(QGraphicsView):
    def __init__(self, gr_scene, parent=None):
        super(QDMGraphicsView, self).__init__(parent)

        self.gr_scene = gr_scene
        self.init_ui()

        self.setScene(self.gr_scene)

        self.mode = MODE_NOOP
        self.editing_flag = False

        self.zoom_in_factor = 1.25
        self.zoom_clamp = True
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = [0, 10]

        self.cutline = QDMCutLine()
        self.gr_scene.addItem(self.cutline)

    def init_ui(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setDragMode(QDMGraphicsView.RubberBandDrag)

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

        # 多选设置
        if hasattr(item, 'node') or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fake_event = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                         Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                         event.modifiers() | Qt.ControlModifier)

                super(QDMGraphicsView, self).mousePressEvent(fake_event)
                return

        if isinstance(item, QDMGraphicsSocket):
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edge_drag_start(item)
                return

        if self.mode == MODE_EDGE_DRAG:
            res = self.edge_drag_end(item)
            if res: return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fake_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                         Qt.LeftButton, Qt.NoButton, event.modifiers())
                super(QDMGraphicsView, self).mousePressEvent(fake_event)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return

        super(QDMGraphicsView, self).mousePressEvent(event)

    def edge_drag_start(self, item):
        print('start dragging edge')
        print('assign start socket')
        self.previous_edge = item.socket.edge
        self.last_start_socket = item.socket
        self.drag_edge = Edge(self.gr_scene.scene, item.socket, None, EDGE_TYPE_BEZIER)

    def edge_drag_end(self, item):
        self.mode = MODE_NOOP
        if isinstance(item, QDMGraphicsSocket):
            if item.socket != self.last_start_socket:
                if item.socket.has_edge():
                    item.socket.edge.remove()

                if self.previous_edge is not None:
                    self.previous_edge.remove()

                self.drag_edge.start_socket = self.last_start_socket
                self.drag_edge.end_socket = item.socket
                self.drag_edge.start_socket.set_connected_edge(self.drag_edge)
                self.drag_edge.end_socket.set_connected_edge(self.drag_edge)
                self.drag_edge.update_positions()
                return True

        self.drag_edge.remove()
        self.drag_edge = None

        if self.previous_edge is not None:
            self.previous_edge.start_socket.edge = self.previous_edge

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

        # 多选设置
        if hasattr(item, 'node') or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                         Qt.LeftButton, Qt.NoButton,
                                         event.modifiers() | Qt.ControlModifier)

                super(QDMGraphicsView, self).mouseReleaseEvent(fake_event)
                return

        if self.mode == MODE_EDGE_DRAG:
            if self.distance_between_click_and_release_is_off(event):
                res = self.edge_drag_end(item)
                if res: return

        if self.mode == MODE_EDGE_CUT:
            self.cut_intersecting_edges()
            self.cutline.line_points = []
            self.cutline.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP
            return

        super(QDMGraphicsView, self).mouseReleaseEvent(event)

    def cut_intersecting_edges(self):
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix - 1]

            for edge in self.gr_scene.scene.edges:
                if edge.gr_edge.intersects_with(p1, p2):
                    edge.remove()

    def right_mouse_button_press(self, event):
        super(QDMGraphicsView, self).mousePressEvent(event)
        item = self.get_item_at_click(event)

    def right_mouse_button_release(self, event):
        return super(QDMGraphicsView, self).mouseReleaseEvent(event)

    def get_item_at_click(self, event):
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            if not self.editing_flag:
                self.delete_selected()
            else:
                super(QDMGraphicsView, self).keyPressEvent(event)

        elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            self.gr_scene.scene.save_to_file('graph.json.txt')

        elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
            self.gr_scene.scene.load_from_file('graph.json.txt')

        else:
            super(QDMGraphicsView, self).keyPressEvent(event)

    def delete_selected(self):
        for item in self.gr_scene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()

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

    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.drag_edge.gr_edge.set_destination(pos.x(), pos.y())
            self.drag_edge.gr_edge.update()

        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.line_points.append(pos)
            self.cutline.update()

        super(QDMGraphicsView, self).mouseMoveEvent(event)

    def debug_modifiers(self, event):
        out = 'MODES: '
        if event.modifiers() & Qt.ShiftModifier: out += 'SHIFT '
        if event.modifiers() & Qt.ControlModifier: out += 'CTRL '
        if event.modifiers() & Qt.AltModifier: out += 'SHIFT '
        return out
