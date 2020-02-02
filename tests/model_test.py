import copy

from collections import OrderedDict

import oapispec as oapi

def test_model_validate_succeedes():

    user_model = oapi.model.Model('User', {
        'user_id': oapi.fields.string(),
        'username': oapi.fields.string(required=True),
    })

    result = user_model.validate({
        'user_id': 'yolo',
        'username': 'yolo',
    })

    assert result is None

def test_model_returns_error():

    user_model = oapi.model.Model('User', {
        'user_id': oapi.fields.string(),
        'username': oapi.fields.string(required=True),
    })

    result = user_model.validate({
        'user_id': 'yolo'
    })

    assert result == {
        'username': "'username' is a required property"
    }

def test_model_as_nested_dict():

    address = oapi.model.Model('Address', {
        'road': oapi.fields.string(),
    })

    assert address.__schema__ == {
        'properties': {
            'road': {
                'type': 'string'
            },
        },
        'type': 'object'
    }

    person = oapi.model.Model('Person', {
        'name': oapi.fields.string(),
        'age': oapi.fields.integer(),
        'birthdate': oapi.fields.date_time(),
        'address': oapi.fields.nested(address)
    })

    assert person.__schema__ == {
        # 'required': ['address'],
        'properties': {
            'name': {
                'type': 'string'
            },
            'age': {
                'type': 'integer'
            },
            'birthdate': {
                'type': 'string',
                'format': 'date-time'
            },
            'address': {
                '$ref': '#/definitions/Address',
            }
        },
        'type': 'object'
    }


def test_model_as_dict_with_list():
    model = oapi.model.Model('Person', {
        'name': oapi.fields.string(),
        'age': oapi.fields.integer(),
        'tags': oapi.fields.array(oapi.fields.string()),
    })

    assert model.__schema__ == {
        'properties': {
            'name': {
                'type': 'string'
            },
            'age': {
                'type': 'integer'
            },
            'tags': {
                'type': 'array',
                'items': {
                    'type': 'string'
                }
            }
        },
        'type': 'object'
    }

def test_model_as_nested_dict_with_list():
    address = oapi.model.Model('Address', {
        'road': oapi.fields.string(),
    })

    person = oapi.model.Model('Person', {
        'name': oapi.fields.string(),
        'age': oapi.fields.integer(),
        'birthdate': oapi.fields.date_time(),
        'addresses': oapi.fields.array(oapi.fields.nested(address))
    })

    assert person.__schema__ == {
        # 'required': ['address'],
        'properties': {
            'name': {
                'type': 'string'
            },
            'age': {
                'type': 'integer'
            },
            'birthdate': {
                'type': 'string',
                'format': 'date-time'
            },
            'addresses': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/Address',
                }
            }
        },
        'type': 'object'
    }

    assert address.__schema__ == {
        'properties': {
            'road': {
                'type': 'string'
            },
        },
        'type': 'object'
    }

def test_model_with_required():
    model = oapi.model.Model('Person', {
        'name': oapi.fields.string(required=True),
        'age': oapi.fields.integer(),
        'birthdate': oapi.fields.date_time(required=True),
    })

    assert model.__schema__ == {
        'properties': {
            'name': {
                'type': 'string'
            },
            'age': {
                'type': 'integer'
            },
            'birthdate': {
                'type': 'string',
                'format': 'date-time'
            }
        },
        'required': ['birthdate', 'name'],
        'type': 'object'
    }

def test_model_as_nested_dict_and_required():
    address = oapi.model.Model('Address', {
        'road': oapi.fields.string(),
    })

    person = oapi.model.Model('Person', {
        'name': oapi.fields.string(),
        'age': oapi.fields.integer(),
        'birthdate': oapi.fields.date_time(),
        'address': oapi.fields.nested(address, required=True)
    })

    assert person.__schema__ == {
        'required': ['address'],
        'properties': {
            'name': {
                'type': 'string'
            },
            'age': {
                'type': 'integer'
            },
            'birthdate': {
                'type': 'string',
                'format': 'date-time'
            },
            'address': {
                '$ref': '#/definitions/Address',
            }
        },
        'type': 'object'
    }

    assert address.__schema__ == {
        'properties': {
            'road': {
                'type': 'string'
            },
        },
        'type': 'object'
    }

def test_model_with_discriminator():
    model = oapi.model.Model('Person', {
        'name': oapi.fields.string(discriminator=True),
        'age': oapi.fields.integer(),
    })

    assert model.__schema__ == {
        'properties': {
            'name': {'type': 'string'},
            'age': {'type': 'integer'},
        },
        'discriminator': 'name',
        'required': ['name'],
        'type': 'object'
    }

def test_model_with_discriminator_override_require():
    model = oapi.model.Model('Person', {
        'name': oapi.fields.string(discriminator=True, required=False),
        'age': oapi.fields.integer(),
    })

    assert model.__schema__ == {
        'properties': {
            'name': {'type': 'string'},
            'age': {'type': 'integer'},
        },
        'discriminator': 'name',
        'required': ['name'],
        'type': 'object'
    }


def test_inherit_from_instance():
    parent = oapi.model.Model('Parent', {
        'name': oapi.fields.string(),
        'age': oapi.fields.integer(),
    })

    child = parent.inherit('Child', {
        'extra': oapi.fields.string(),
    })

    assert parent.__schema__ == {
        'properties': {
            'name': {'type': 'string'},
            'age': {'type': 'integer'},
        },
        'type': 'object'
    }
    assert child.__schema__ == {
        'allOf': [
            {'$ref': '#/definitions/Parent'},
            {
                'properties': {
                    'extra': {'type': 'string'}
                },
                'type': 'object'
            }
        ]
    }

def test_inherit_from_class():
    parent = oapi.model.Model('Parent', {
        'name': oapi.fields.string(),
        'age': oapi.fields.integer()
    })

    child = parent.inherit('Child', {
        'extra': oapi.fields.string()
    })

    assert parent.__schema__ == {
        'properties': {
            'name': {'type': 'string'},
            'age': {'type': 'integer'}
        },
        'type': 'object'
    }
    print(child.__schema__)
    assert child.__schema__ == {
        'allOf': [
            {'$ref': '#/definitions/Parent'},
            {
                'properties': {
                    'extra': {'type': 'string'}
                },
                'type': 'object'
            }
        ]
    }

def test_inherit_from_multiple_parents():
    grand_parent = oapi.model.Model('GrandParent', {
        'grand_parent': oapi.fields.string()
    })

    parent = grand_parent.inherit('Parent', {
        'name': oapi.fields.string(),
        'age': oapi.fields.integer()
    })

    child = parent.inherit('Child', {
        'extra': oapi.fields.string()
    })

    print(child.__schema__)

    assert child.__schema__ == {
        'allOf': [
            {'$ref': '#/definitions/GrandParent'},
            {'$ref': '#/definitions/Parent'},
            {
                'properties': {
                    'extra': {'type': 'string'}
                },
                'type': 'object'
            }
        ]
    }

def test_model_str():
    model = oapi.model.Model('Car', {
        'color': oapi.fields.string()
    })

    result = str(model)
