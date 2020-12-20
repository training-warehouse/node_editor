# -*- coding: utf-8 -*-
# Time    : 2020/12/15 21:35
# Author  : LiaoKong
from collections import OrderedDict

from node_editor.node_edge import Edge
from node_editor.node_graphics_edge import QDMGraphicsEdge
from node_editor.node_node import Node


class SceneClipboard(object):
    def __init__(self, scene):
        self.scene = scene

    def serialize_selected(self, delete=False):
        sel_nodes, sel_edges, sel_sockets = [], [], {}

        for item in self.scene.gr_scene.selectedItems():
            if hasattr(item, 'node'):
                sel_nodes.append(item.node.serialize())
                for socket in item.node.inputs + item.node.outputs:
                    sel_sockets[socket.id] = socket
            elif isinstance(item, QDMGraphicsEdge):
                sel_edges.append(item.edge)

        edges_to_remove = []
        for edge in sel_edges:
            if edge.start_socket.id in sel_sockets and edge.end_socket.id in sel_sockets:
                pass
            else:
                edges_to_remove.append(edge)
        for edge in edges_to_remove:
            sel_edges.remove(edge)

        edge_final = []
        for edge in sel_edges:
            edge_final.append(edge.serialize())

        data = OrderedDict([
            ('nodes', sel_nodes),
            ('edges', edge_final),
        ])
        if delete:
            self.scene.gr_scene.views()[0].delete_selected()
            self.scene.history.store_history('Cut out elements from scene', set_modified=True)

        return data

    def deserialize_from_clipboard(self, data):
        hashmap = {}

        view = self.scene.gr_scene.views()[0]
        mouse_scene_pos = view.last_scene_mouse_position

        minx, miny, maxx, maxy = 0, 0, 0, 0
        for node_data in data['nodes']:
            x, y = node_data['pos_x'], node_data['pos_y']
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y
        bbox_center_x = (minx + maxx) / 2
        bbox_center_y = (miny + maxy) / 2

        # center = view.mapToScene(view.rect().center())

        offset_x = mouse_scene_pos.x() - bbox_center_x
        offset_y = mouse_scene_pos.y() - bbox_center_y

        for node_data in data['nodes']:
            new_node = Node(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False)

            pos = new_node.pos
            new_node.set_pos(pos.x() + offset_x, pos.y() + offset_y)

        if 'edges' in data:
            for edge_data in data['edges']:
                new_edge = Edge(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False)

        self.scene.history.store_history('Pasted elements in center', set_modified=True)
