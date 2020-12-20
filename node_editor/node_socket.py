# -*- coding: utf-8 -*-
# Time    : 2020/12/12 17:24
# Author  : LiaoKong
from collections import OrderedDict

from node_editor.node_derializable import Serializable
from node_editor.node_graphics_socket import QDMGraphicsSocket

LEFT_TOP = 1
LEFT_BUTTON = 2
RIGHT_TOP = 3
RIGHT_BUTTON = 4


class Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socket_type=1, multi_edges=True):
        super(Socket, self).__init__()
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.is_multi_edges = multi_edges

        self.gr_socket = QDMGraphicsSocket(self, self.socket_type)
        self.gr_socket.setPos(*self.node.get_socket_position(self.index, self.position))

        self.edges = []

    def get_socket_position(self):
        print('gsp:', self.index, self.position)
        res = self.node.get_socket_position(self.index, self.position)
        print('res:', res)
        return res

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_edge(self,edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def remove_all_edges(self):
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove()

    # def has_edge(self):
    #     return self.edge is not None

    def __str__(self):
        return '<Socket %s...%s>' % (hex(id(self))[2:5], hex(id(self))[-3:])

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('multi_edges', self.is_multi_edges),
            ('position', self.position),
            ('socket_type', self.socket_type)
        ])

    def deserialize(self, data, hashmap=None, restore_id=True):
        if restore_id: self.id = data['id']
        self.is_multi_edges = data['multi_edges']
        hashmap[data['id']] = self

        return True
