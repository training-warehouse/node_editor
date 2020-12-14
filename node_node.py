# -*- coding: utf-8 -*-
# Time    : 2020/12/12 15:27
# Author  : LiaoKong
from node_content_widget import QDMNodeContentWidget
from node_graphics_node import QDMGraphicsNode
from node_socket import *


class Node(object):
    def __init__(self, scene, title='Undefined Node', inputs=None, outputs=None):
        self.scene = scene
        self.title = title

        self.content = QDMNodeContentWidget(self)
        self.gr_node = QDMGraphicsNode(self)

        self.scene.add_node(self)
        self.scene.gr_scene.addItem(self.gr_node)

        # 接口间距
        self.socket_spacing = 22

        self.inputs = []
        self.outputs = []
        counter = 0
        for item in inputs:
            socket = Socket(self, counter, LEFT_BUTTON, item)
            self.inputs.append(socket)
            counter += 1

        counter = 0
        for item in outputs:
            socket = Socket(self, counter, RIGHT_TOP, item)
            self.outputs.append(socket)
            counter += 1

    def __str__(self):
        return '<Node %s...%s>' % (hex(id(self))[2:5], hex(id(self))[-3:])

    def set_pos(self, x, y):
        self.gr_node.setPos(x, y)

    @property
    def pos(self):
        return self.gr_node.pos()

    def get_socket_position(self, index, position):
        x = 0 if position in (LEFT_TOP, LEFT_BUTTON) else self.gr_node.width
        if position in (LEFT_BUTTON, RIGHT_BUTTON):
            y = self.gr_node.height - self.gr_node.edge_size - self.gr_node._padding - index * self.socket_spacing
        else:
            y = self.gr_node.title_height + self.gr_node._padding + self.gr_node.edge_size + index * self.socket_spacing

        return [x, y]

    def update_connected_edges(self):
        for socket in self.inputs + self.outputs:
            if socket.has_edge():
                socket.edge.update_positions()

    def remove(self):
        for socket in self.inputs+self.outputs:
            if socket.has_edge():
                socket.edge.remove()

        self.scene.gr_scene.removeItem(self.gr_node)
        self.gr_node = None
        self.scene.remove_node(self)
