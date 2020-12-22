# -*- coding: utf-8 -*-
# Time    : 2020/12/14 22:05
# Author  : LiaoKong
from node_editor.node_graphics_edge import QDMGraphicsEdge

DEBUG = True


class SceneHistory(object):
    def __init__(self, scene):
        self.scene = scene

        self.clear()
        self.history_limit = 32

        self._history_modified_listeners = []

    def clear(self):
        self.history_stack = []
        self.history_current_step = -1

    def store_initial_history_stamp(self):
        self.store_history('Initial History Stamp')

    def can_undo(self):
        return self.history_current_step > 0

    def can_redo(self):
        return self.history_current_step + 1 < len(self.history_stack)

    def undo(self):
        if DEBUG: print('UNDO')
        if self.can_undo():
            self.history_current_step -= 1
            self.restore_history()
            self.scene.has_been_modified = True

    def redo(self):
        if DEBUG: print('REDO')
        if self.can_redo():
            self.history_current_step += 1
            self.restore_history()
            self.scene.has_been_modified = True

    def add_history_modified_listener(self, callback):
        self._history_modified_listeners.append(callback)

    def restore_history(self):
        if DEBUG: print('restore_history... current_step:', self.history_current_step, len(self.history_stack))

        self.restore_history_stamp(self.history_stack[self.history_current_step])

        for callback in self._history_modified_listeners:
            callback()

    def store_history(self, desc, set_modified=False):
        if set_modified:
            self.scene.has_been_modified = True

        if DEBUG: print('store_history... current_step:', self.history_current_step, len(self.history_stack))

        if self.history_current_step + 1 < len(self.history_stack):
            self.history_stack = self.history_stack[0:self.history_current_step + 1]

        if self.history_current_step + 1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1

        hs = self.create_history_stamp(desc)
        self.history_stack.append(hs)
        self.history_current_step += 1

        for callback in self._history_modified_listeners:
            callback()

    def create_history_stamp(self, desc):
        sel_obj = {
            'nodes': [],
            'edges': [],
        }

        for item in self.scene.gr_scene.selectedItems():
            if hasattr(item, 'node'):
                sel_obj['nodes'].append(item.node.id)
            elif isinstance(item, QDMGraphicsEdge):
                sel_obj['edges'].append(item.edge.id)

        history_stamp = {
            'desc': desc,
            'snapshot': self.scene.serialize(),
            'selection': sel_obj
        }

        return history_stamp

    def restore_history_stamp(self, history_stamp):
        if DEBUG: print('RHS: ', history_stamp)

        self.scene.deserialize(history_stamp['snapshot'])

        for edge_id in history_stamp['selection']['edges']:
            for edge in self.scene.edges:
                if edge.id == edge_id:
                    edge.gr_edge.setSelected(True)
                    break

        for node_id in history_stamp['selection']['nodes']:
            for node in self.scene.nodes:
                if node.id == node_id:
                    node.gr_node.setSelected(True)
                    break
