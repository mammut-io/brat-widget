# coding=utf-8
import json

class JsonDumpable:
    def get_dict(self):
        return {}

    def set_from_dict(self, dict):
        pass

    @classmethod
    def to_json(cls, conf, widget_model):
        return json.dumps(conf.get_dict())

    @classmethod
    def from_json(cls, json_str, widget_model):
        dict = json.loads(json_str)
        res = cls()
        res.set_from_dict(dict)
        return res


class ProtocolError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        # TODO: just adding __str__ to ProtocolError, not all
        # currently support it, so falling back on this assumption
        # about how to make a (nearly) human-readable string. Once
        # __str__ added to all ProtocolErrors, raise
        # NotImplementedError instead.
        return 'ProtocolError: %s (TODO: __str__() method)' % self.__class__

    def json(self, json_dic):
        raise NotImplementedError()

class ProtocolArgumentError(ProtocolError):
    def json(self, json_dic):
        json_dic['exception'] = 'protocolArgumentError'

'''
class NoPrintJSONError(Exception):
    def __init__(self, hdrs, data):
        self.hdrs = hdrs
        self.data = data
'''

class NotImplementedError(ProtocolError):
    def json(self, json_dic):
        json_dic['exception'] = 'notImplemented'

'''
class CollectionNotAccessibleError(ProtocolError):
    def json(self, json_dic):
        json_dic['exception'] = 'collectionNotAccessible'

    def __str__(self):
        return 'Error: collection not accessible'
'''
