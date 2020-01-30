import copy
import re
import warnings

from collections import OrderedDict
from collections.abc import MutableMapping
from werkzeug.utils import cached_property

from jsonschema import Draft4Validator
from jsonschema.exceptions import ValidationError

from oapispec.core.utils import not_none


RE_REQUIRED = re.compile(r'u?\'(?P<name>.*)\' is a required property', re.I | re.U)

def instance(cls):
    if isinstance(cls, type):
        return cls()
    return cls

def _format_error(error):
    path = list(error.path)
    if error.validator == 'required':
        name = RE_REQUIRED.match(error.message).group('name')
        path.append(name)
    key = '.'.join(str(p) for p in path)
    return key, error.message

class Model:
    '''
    Handles validation and swagger style inheritance for both subclasses.
    Subclass must define `schema` attribute.

    :param str name: The model public name
    '''

    def __init__(self, name, attributes):
        self.attributes = attributes

        self.__apidoc__ = {
            'name': name
        }
        self.name = name
        self.__parents__ = []

        def instance_inherit(name, *parents):
            return self.__class__.inherit(name, self, *parents)

        self.inherit = instance_inherit

    @property
    def ancestors(self):
        '''
        Return the ancestors tree
        '''
        ancestors = [p.ancestors for p in self.__parents__]
        return set.union(set([self.name]), *ancestors)

    def get_parent(self, name):
        if self.name == name:
            return self
        for parent in self.__parents__:
            found = parent.get_parent(name)
            if found:
                return found
        raise ValueError('Parent ' + name + ' not found')

    @property
    def __schema__(self):
        schema = self._schema

        if self.__parents__:
            refs = [
                {'$ref': '#/definitions/{0}'.format(parent.name)}
                for parent in self.__parents__
            ]

            return {
                'allOf': refs + [schema]
            }
        return schema

    @classmethod
    def inherit(cls, name, *parents):
        '''
        Inherit this model (use the Swagger composition pattern aka. allOf)
        :param str name: The new model name
        :param dict fields: The new model extra fields
        '''
        model = cls(name, parents[-1])
        model.__parents__ = parents[:-1]
        return model

    def validate(self, data):
        validator = Draft4Validator(self.__schema__)
        try:
            validator.validate(data)
        except ValidationError:
            return dict(_format_error(e) for e in validator.iter_errors(data))
        return None

    def __str__(self):
        return 'Model({name},{{{fields}}})'.format(name=self.name, fields=','.join(self.attributes.keys()))

    @property
    def _schema(self):
        properties = {}
        required = set()
        discriminator = None
        for name, field in self.attributes.items():
            field = instance(field)
            properties[name] = field.__schema__
            if field.required:
                required.add(name)
            if getattr(field, 'discriminator', False):
                discriminator = name

        return not_none({
            'required': sorted(list(required)) or None,
            'properties': properties,
            'discriminator': discriminator,
            'type': 'object',
        })

    @cached_property
    def resolved(self):
        '''
        Resolve real fields before submitting them to marshal
        '''
        # Duplicate fields
        resolved = copy.deepcopy(self)

        # Recursively copy parent fields if necessary
        for parent in self.__parents__:
            resolved.update(parent.resolved)

        # Handle discriminator
        candidates = [f for f in resolved.values() if getattr(f, 'discriminator', None)]
        # Ensure the is only one discriminator
        if len(candidates) > 1:
            raise ValueError('There can only be one discriminator by schema')
        # Ensure discriminator always output the model name
        if len(candidates) == 1:
            candidates[0].default = self.name

        return resolved
