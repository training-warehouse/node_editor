# -*- coding: utf-8 -*-
# Time    : 2020/12/14 20:42
# Author  : LiaoKong


class Serializable(object):
    def __init__(self):
        self.id = id(self)

    def serialize(self):
        raise NotImplementedError

    def deserialize(self, data, hashmap=None):
        raise NotImplementedError
