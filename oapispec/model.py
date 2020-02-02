import re

from jsonschema import Draft4Validator
from jsonschema.exceptions import ValidationError

from oapispec.core.utils import not_none


RE_REQUIRED = re.compile(r'u?\'(?P<name>.*)\' is a required property', re.I | re.U)

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

    def inherit(self, name, attributes):
        '''
        Inherit this model (use the Swagger composition pattern aka. allOf)
        :param str name: The new model name
        :param dict fields: The new model extra fields
        '''
        model = Model(name, attributes)
        model.__parents__ = [*self.__parents__, self]
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
