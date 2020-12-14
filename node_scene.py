# -*- coding: utf-8 -*-
# Time    : 2020/12/12 15:12
# Author  : LiaoKong
import json
from collections import OrderedDict

from node_derializable import Serializable
from node_graphics_scene import QDMGraphicsScene
from node_node import Node
from node_edge import Edge


class Scene(Serializable):
    def __init__(self):
        super(Scene, self).__init__()
        self.nodes = []
        self.edges = []

        self.scene_width, self.scene_height = 64000, 64000

        self.init_ui()

    def init_ui(self):
        self.gr_scene = QDMGraphicsScene(self)
        self.gr_scene.set_gr_scene(self.scene_width, self.scene_height)

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_node(self, node):
        self.nodes.remove(node)

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            file.write(json.dumps(self.serialize(), indent=4))

    def load_from_file(self, filename):
        with open(filename) as file:
            raw_data = file.read()
            data = json.loads(raw_data, encoding='utf8')

            self.deserialize(data)

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())

        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges)
        ])

    def deserialize(self, data, hashmap=None):
        self.clear()
        hashmap = {}

        for node_data in data['nodes']:
            Node(self).deserialize(node_data, hashmap)

        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap)

        return True
