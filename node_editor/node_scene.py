# -*- coding: utf-8 -*-
# Time    : 2020/12/12 15:12
# Author  : LiaoKong
import json
import os
from collections import OrderedDict

from node_editor.node_derializable import Serializable
from node_editor.node_graphics_scene import QDMGraphicsScene
from node_editor.node_scene_history import SceneHistory
from node_editor.node_scene_clipboard import SceneClipboard
from node_editor.node_node import Node
from node_editor.node_edge import Edge


class Scene(Serializable):
    def __init__(self):
        super(Scene, self).__init__()
        self.nodes = []
        self.edges = []

        self.scene_width, self.scene_height = 64000, 64000
        self._has_been_modified = False
        self._last_selected_items = []

        self._has_been_modified_listeners = []
        self._item_selected_listeners = []
        self._item_deselected_listeners = []

        self.init_ui()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

        self.gr_scene.item_selected.connect(self.on_item_selected)
        self.gr_scene.item_deselected.connect(self.on_item_deselected)

    def on_item_selected(self):
        print('SCENE: on item selected')
        current_selected_items = self.get_selected_items()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            self.history.store_history('Selection Changed')

            for callback in self._item_selected_listeners:
                callback()

    def on_item_deselected(self):
        print('SCENE: on item deselected')
        self.reset_last_selected_states()
        if self._last_selected_items:
            self._last_selected_items = []
            self.history.store_history('Deselected Everything')

            for callback in self._item_deselected_listeners:
                callback()

    def is_modified(self):
        return self.has_been_modified

    def get_selected_items(self):
        return self.gr_scene.selectedItems()

    @property
    def has_been_modified(self):
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            self._has_been_modified = value

            for callback in self._has_been_modified_listeners:
                callback()

        self._has_been_modified = value

    def add_has_been_modified_listeners(self, callback):
        self._has_been_modified_listeners.append(callback)

    def add_item_selected_listener(self, callback):
        self._item_selected_listeners.append(callback)

    def add_item_deselected_listener(self, callback):
        self._item_deselected_listeners.append(callback)

    def init_ui(self):
        self.gr_scene = QDMGraphicsScene(self)
        self.gr_scene.set_gr_scene(self.scene_width, self.scene_height)

    def reset_last_selected_states(self):
        for node in self.nodes:
            node.gr_node._last_selected_state = False
        for edge in self.edges:
            edge.gr_edge._last_selected_state = False

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            file.write(json.dumps(self.serialize(), indent=4))
            self.has_been_modified = False

    def load_from_file(self, filename):
        with open(filename) as file:
            raw_data = file.read()
            try:
                data = json.loads(raw_data, encoding='utf8')

                self.deserialize(data)
                self.has_been_modified = False
            except json.JSONDecodeError:
                raise Exception('%s is not a valid JSON file' % os.path.basename(filename))

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

    def deserialize(self, data, hashmap=None, restore_id=True):
        self.clear()
        hashmap = {}

        if restore_id: self.id = data['id']

        for node_data in data['nodes']:
            Node(self).deserialize(node_data, hashmap, restore_id)

        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap, restore_id)

        return True
