import inspect
import datetime

from oapispec.model import Model
from oapispec import fields


def get_annotations(klass):
    return getattr(klass, '__annotations__', {})

def get_model_attribute_type(attr_type):
    if attr_type == str:
        return fields.string()
    if attr_type == bool:
        return fields.boolean()
    if attr_type == dict:
        return fields.raw()
    if attr_type == int:
        return fields.integer()
    if attr_type == datetime.date:
        return fields.date()
    if attr_type == datetime.datetime:
        return fields.date_time()

    type_str = str(type(attr_type))
    is_list = 'Generic' in type_str

    if is_list:
        child_type = attr_type.__args__[0]
        return fields.array(get_model_attribute_type(child_type))

    return fields.nested(build_model(attr_type))

def get_model_attribute_dict(attribute_map):
    return dict([
        (name, get_model_attribute_type(attr_type)) for name, attr_type in attribute_map.items()
    ])

def build_model(klass):
    members = get_annotations(klass)
    return Model(klass.__name__, get_model_attribute_dict(members))
