# -*- coding: utf-8 -*-
# Time    : 2020/12/12 18:24
# Author  : LiaoKong
from collections import OrderedDict

from node_editor.node_derializable import Serializable
from node_editor.node_graphics_edge import *

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2


class Edge(Serializable):
    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EDGE_TYPE_DIRECT):
        super(Edge, self).__init__()
        self.scene = scene

        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type

        self.scene.add_edge(self)

    @property
    def start_socket(self):
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        if self._start_socket is not None:
            self._start_socket.remove_edge(self)

        self._start_socket = value
        if self.start_socket is not None:
            self.start_socket.add_edge(self)

    @property
    def end_socket(self):
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        if self._end_socket is not None:
            self._end_socket.remove_edge(self)

        self._end_socket = value
        if self.end_socket is not None:
            self.end_socket.add_edge(self)

    @property
    def edge_type(self):
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        if hasattr(self, 'gr_edge') and self.gr_edge is not None:
            self.scene.gr_scene.removeItem(self.gr_edge)

        self._edge_type = value
        if self._edge_type == EDGE_TYPE_DIRECT:
            self.gr_edge = QDMGraphicsEdgeDirect(self)
        elif self._edge_type == EDGE_TYPE_BEZIER:
            self.gr_edge = QDMGraphicsEdgeBezier(self)
        else:
            self.gr_edge = QDMGraphicsEdgeBezier(self)

        self.scene.gr_scene.addItem(self.gr_edge)

        if self.start_socket is not None:
            self.update_positions()

    def update_positions(self):
        source_pos = self.start_socket.get_socket_position()
        source_pos[0] += self.start_socket.node.gr_node.pos().x()
        source_pos[1] += self.start_socket.node.gr_node.pos().y()
        self.gr_edge.set_source(*source_pos)
        if self.end_socket is not None:
            end_pos = self.end_socket.get_socket_position()
            end_pos[0] += self.end_socket.node.gr_node.pos().x()
            end_pos[1] += self.end_socket.node.gr_node.pos().y()
            self.gr_edge.set_destination(*end_pos)
        else:
            self.gr_edge.set_destination(*source_pos)

        self.gr_edge.update()

    def remove_from_sockets(self):
        # if self.start_socket is not None:
        #     self.start_socket.remove_edge(None)
        # if self.end_socket is not None:
        #     self.end_socket.remove_edge(None)
        self.end_socket = None
        self.start_socket = None

    def remove(self):
        self.remove_from_sockets()
        self.scene.gr_scene.removeItem(self.gr_edge)
        self.gr_edge = None
        try:
            self.scene.remove_edge(self)
        except ValueError:
            pass

    def __str__(self):
        return '<Edge %s...%s>' % (hex(id(self))[2:5], hex(id(self))[-3:])

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.id),
            ('end', self.end_socket.id)
        ])

    def deserialize(self, data, hashmap=None, restore_id=True):
        if restore_id: self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']
