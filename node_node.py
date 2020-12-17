# -*- coding: utf-8 -*-
# Time    : 2020/12/12 15:27
# Author  : LiaoKong
from collections import OrderedDict

from node_derializable import Serializable
from node_content_widget import QDMNodeContentWidget
from node_graphics_node import QDMGraphicsNode
from node_socket import *


class Node(Serializable):
    def __init__(self, scene, title='Undefined Node', inputs=None, outputs=None):
        super(Node, self).__init__()
        self._title = title
        self.scene = scene

        self.content = QDMNodeContentWidget(self)
        self.gr_node = QDMGraphicsNode(self)
        self.title = title

        self.scene.add_node(self)
        self.scene.gr_scene.addItem(self.gr_node)

        # 接口间距
        self.socket_spacing = 22

        self.inputs = []
        self.outputs = []
        counter = 0
        for item in inputs or []:
            socket = Socket(self, counter, LEFT_BUTTON, item, multi_edges=False)
            self.inputs.append(socket)
            counter += 1

        counter = 0
        for item in outputs or []:
            socket = Socket(self, counter, RIGHT_TOP, item, multi_edges=True)
            self.outputs.append(socket)
            counter += 1

    def __str__(self):
        return '<Node %s...%s>' % (hex(id(self))[2:5], hex(id(self))[-3:])

    def set_pos(self, x, y):
        self.gr_node.setPos(x, y)

    @property
    def pos(self):
        return self.gr_node.pos()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.gr_node.title = self._title

    def get_socket_position(self, index, position):
        x = 0 if position in (LEFT_TOP, LEFT_BUTTON) else self.gr_node.width
        if position in (LEFT_BUTTON, RIGHT_BUTTON):
            y = self.gr_node.height - self.gr_node.edge_size - self.gr_node._padding - index * self.socket_spacing
        else:
            y = self.gr_node.title_height + self.gr_node._padding + self.gr_node.edge_size + index * self.socket_spacing

        return [x, y]

    def update_connected_edges(self):
        for socket in self.inputs + self.outputs:
            # if socket.has_edge():
            for edge in socket.edges:
                edge.update_positions()

    def remove(self):
        for socket in self.inputs + self.outputs:
            # if socket.has_edge():
            for edge in socket.edges:
                edge.remove()

        self.scene.gr_scene.removeItem(self.gr_node)
        self.gr_node = None
        self.scene.remove_node(self)

    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())

        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.gr_node.scenePos().x()),
            ('pos_y', self.gr_node.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', self.content.serialize())
        ])

    def deserialize(self, data, hashmap=None, restore_id=True):
        if restore_id: self.id = data['id']
        hashmap[data['id']] = self

        self.title = data['title']
        self.set_pos(data['pos_x'], data['pos_y'])

        data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
        data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)

        self.inputs = []
        for socket_data in data['inputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                socket_type=socket_data['socket_type'])
            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.inputs.append(new_socket)

        self.outputs = []
        for socket_data in data['outputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                socket_type=socket_data['socket_type'])
            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.outputs.append(new_socket)

        return True
