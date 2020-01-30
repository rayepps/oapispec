import itertools
import re
from http import HTTPStatus
from inspect import isclass
from collections import OrderedDict
from collections.abc import Hashable
from urllib.parse import quote

from werkzeug.routing import parse_rule

from oapispec import fields
from oapispec.model import Model
from oapispec.core.reqparse import RequestParser
from oapispec.core.utils import merge, not_none, not_none_sorted



#: Maps Flask/Werkzeug rooting types to Swagger ones
PATH_TYPES = {
    'int': 'integer',
    'float': 'number',
    'string': 'string',
    'str': 'string',
    'default': 'string'
}


#: Maps Python primitives types to Swagger ones
PY_TYPES = {
    int: 'integer',
    float: 'number',
    str: 'string',
    bool: 'boolean',
    None: 'void'
}

RE_URL = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')


class OpenApi:
    '''
    A Swagger documentation wrapper for an API instance.
    '''
    def __init__(self, metadata, handlers):
        self.metadata = metadata
        self.handlers = handlers

    def as_dict(self):
        return create_openapi_spec_dict(self.metadata, self.handlers)


def create_openapi_spec_dict(metadata, handlers):
    '''
    Output the specification as a serializable ``dict``.

    :returns: the full Swagger specification in a serializable format
    :rtype: dict
    '''

    basepath = metadata.base_path
    if len(basepath) > 1 and basepath.endswith('/'):
        basepath = basepath[:-1]

    infos = {
        'title': metadata.title,
        'version': metadata.version
    }

    if metadata.description:
        infos['description'] = metadata.description

    if metadata.terms_url:
        infos['termsOfService'] = metadata.terms_url

    if metadata.contact and (metadata.contact_email or metadata.contact_url):
        infos['contact'] = {
            'name': metadata.contact,
            'email': metadata.contact_email,
            'url': metadata.contact_url,
        }

    if metadata.license:
        infos['license'] = {'name': metadata.license}
        if metadata.license_url:
            infos['license']['url'] = metadata.license_url

    tags = extract_tags(metadata, handlers)

    docs = [{ **getattr(handler, '__apidoc__', {}), 'handler': handler } for handler in handlers]

    paths = {}
    for apidoc in docs:
        route = apidoc.get('route')
        stripped_route = clean_route(route)

        current_route_obj = paths.get(stripped_route, {})
        current_route_obj[apidoc['method']] = apidoc
        paths[stripped_route] = current_route_obj

    for path, methods in paths.items():
        for method, doc in methods.items():
            paths[path][method] = serialize_operation(doc)

    models = find_models(handlers)

    specs = {
        'swagger': '2.0',
        'basePath': basepath,
        'paths': not_none_sorted(paths),
        'info': infos,
        'produces': metadata.representations,
        'consumes': ['application/json'],
        'securityDefinitions': metadata.authorizations or None,
        'security': security_requirements(metadata.security) or None,
        'tags': tags,
        'definitions': serialize_definitions(models) or None,
        'host': metadata.host,
    }
    return not_none(specs)

def ref(model):
    '''Return a reference to model in definitions'''
    name = model.name if isinstance(model, Model) else model
    return {'$ref': '#/definitions/{0}'.format(quote(name, safe=''))}

def strip_route_types(route):
    '''Takes a route ('/path/to/<str:id>') and removes the type
    parameters ('/path/to/<id>')'''
    match = re.search('\/\<([a-z]+):', route)
    if not match:
        return route
    typ = match.groups()[0]
    route = route.replace(f'/<{typ}:', '/<')
    return strip_route_types(route)

def convert_path_args_to_brackets(route):
    '''Takes a route ('/path/to/<id>') and converts the
    arrows to brackets ('/path/to/{id}')'''
    match = re.search('\/\<([a-z_]+)\>', route)
    if not match:
        return route
    param = match.groups()[0]
    route = route.replace(f'/<{param}>', f'/{{{param}}}')
    return convert_path_args_to_brackets(route)

def clean_route(route):
    return convert_path_args_to_brackets(strip_route_types(route))

def extract_path_params(path):
    '''
    Extract Flask-style parameters from an URL pattern as Swagger ones.
    '''
    params = OrderedDict()
    for converter, _, variable in parse_rule(path):
        if not converter:
            continue
        param = {
            'name': variable,
            'in': 'path',
            'required': True
        }

        if converter in PATH_TYPES:
            param['type'] = PATH_TYPES[converter]
        else:
            raise ValueError(f'Unsupported type converter: {converter}')
        params[variable] = param
    return params

def create_header_object(header):
    if isinstance(header, str):
        header = {'description': header}
    typedef = header.get('type', 'string')
    if isinstance(typedef, Hashable) and typedef in PY_TYPES:
        header['type'] = PY_TYPES[typedef]
    elif isinstance(typedef, (list, tuple)) and len(typedef) == 1 and typedef[0] in PY_TYPES:
        header['type'] = 'array'
        header['items'] = {'type': PY_TYPES[typedef[0]]}
    elif hasattr(typedef, '__schema__'):
        header.update(typedef.__schema__)
    else:
        header['type'] = typedef
    return not_none(header)

def extract_tags(metadata, handlers):

    tags = []
    by_name = {}

    for tag in metadata.tags:
        if isinstance(tag, str):
            tag = {'name': tag}
        if isinstance(tag, dict) and 'name' in tag:
            tags.append(tag)
            by_name[tag['name']] = tag

    namespaces = [getattr(h, '__apidoc__', {}).get('namespace', {}) for h in handlers]

    for ns in namespaces:
        name = ns.get('name')
        if name not in by_name:
            tags.append(ns)
            by_name[name] = True

    return tags

def expected_params(apidoc):
    params = OrderedDict()

    for model, description in apidoc.get('expect', []):

        if isinstance(model, RequestParser):
            parser_params = OrderedDict((p['name'], p) for p in model.__schema__)
            params.update(parser_params)
            continue

        if isinstance(model, Model):
            params['payload'] = not_none({
                'name': 'payload',
                'required': True,
                'in': 'body',
                'schema': serialize_schema(model)
            })
            continue

        params['payload'] = not_none({
            'name': 'payload',
            'required': True,
            'in': 'body',
            'schema': serialize_schema(model),
            'description': description
        })

    return params

def serialize_operation(apidoc):

    operation = {
        'responses': responses_for(apidoc) or None,
        # 'summary': 'TODO-ray parse docstirng from here', # doc[method]['docstring']['summary'],
        'description': apidoc.get('description') or None,
        'operationId': apidoc.get('name'),
        'parameters': parameters_for(apidoc) or None,
        'security': security_for(apidoc)
    }

    if 'namespace' in apidoc:
        operation['tags'] = [apidoc['namespace']['name']]

    # Handle 'produces' mimetypes documentation
    if 'produces' in apidoc:
        operation['produces'] = apidoc['produces']

    # Handle deprecated annotation
    if apidoc.get('deprecated'):
        operation['deprecated'] = True

    if operation.get('parameters', False) and any(p['in'] == 'formData' for p in operation.get('parameters')):
        if any(p['type'] == 'file' for p in operation.get('parameters')):
            operation['consumes'] = ['multipart/form-data']
        else:
            operation['consumes'] = ['application/x-www-form-urlencoded', 'multipart/form-data']

    operation.update(vendor_fields(apidoc))

    return not_none(operation)

def vendor_fields(apidoc):
    '''
    Extract custom 3rd party Vendor fields prefixed with ``x-``

    See: http://swagger.io/specification/#specification-extensions-128
    '''
    return dict(
        (k if k.startswith('x-') else 'x-{0}'.format(k), v)
        for k, v in apidoc.get('vendor', {}).items()
    )

def create_parameter(name, param):
    param['name'] = name

    if 'type' not in param and 'schema' not in param:
        param['type'] = 'string'

    if 'in' not in param:
        param['in'] = 'query'

    if 'type' in param and 'schema' not in param:
        ptype = param.get('type', None)
        if isinstance(ptype, (list, tuple)):
            typ = ptype[0]
            param['type'] = 'array'
            param['items'] = {'type': PY_TYPES.get(typ, typ)}

        elif isinstance(ptype, (type, type(None))) and ptype in PY_TYPES:
            param['type'] = PY_TYPES[ptype]

    return param

def parameters_for(apidoc):

    params = []

    route = apidoc.get('route')

    if route is None:
        raise ValueError('route value cannot be empty. Every function must be decorated with @doc.route("/route/path")')

    expected_paramaters = expected_params(apidoc)
    doc_params = apidoc.get('params', {})
    path_params = extract_path_params(route)

    params = list(merge(merge(expected_paramaters, doc_params), path_params).values())

    for name, param in doc_params.items():
        param = create_parameter(name, param)
        params.append(param)

    return params

def responses_for(apidoc):

    responses = {}
    global_headers = apidoc.get('headers', {})

    for code, (description, model, headers) in apidoc.get('responses', {}).items():

        description = description or 'Success'
        headers = headers or {}

        if code in responses:
            responses[code].update(description=description)
        else:
            responses[code] = {'description': description}
        if model is not None:
            schema = serialize_schema(model)
            responses[code]['schema'] = schema
        responses[code] = attatch_headers(responses[code], global_headers, headers)

    if 'model' in apidoc:
        code = str(apidoc.get('default_code', HTTPStatus.OK))
        if code not in responses:
            responses[code] = attatch_headers({'description': 'Success'}, global_headers, {})
        responses[code]['schema'] = serialize_schema(apidoc['model'])

    return responses

def attatch_headers(response, global_headers, response_headers):
    all_headers = { **global_headers, **response_headers }
    if not all_headers:
        return response
    return {
        **response,
        'headers': dict((k, create_header_object(v)) for k, v in all_headers.items())
    }

def serialize_definitions(registered_models):
    return dict(
        (name, model.__schema__)
        for name, model in registered_models.items()
    )

def serialize_schema(model):

    if isinstance(model, (list, tuple)):
        model = model[0]
        return {
            'type': 'array',
            'items': serialize_schema(model),
        }

    if isinstance(model, Model):
        # register_model(model)
        return ref(model)

    if isinstance(model, str):
        # register_model(model)
        return ref(model)

    if isclass(model) and issubclass(model, fields.Raw):
        return serialize_schema(model())

    if isinstance(model, fields.Raw):
        return model.__schema__

    if isinstance(model, (type, type(None))) and model in PY_TYPES:
        return {'type': PY_TYPES[model]}

    raise ValueError('Model {0} not registered'.format(model))

def find_models(handlers):
    models = {}
    apidoc_list = [getattr(h, '__apidoc__') for h in handlers]
    for apidoc in apidoc_list:
        for expect in apidoc.get('expect', []):
            if isinstance(expect, Model):
                models[expect.name] = expect
        for _, (_, model, _) in apidoc.get('responses', {}).items():
            if isinstance(model, Model):
                models[model.name] = model
    return models

def security_for(apidoc):
    security = None

    if 'security' in apidoc:
        auth = apidoc['security']
        security = security_requirements(auth)

    return security

def security_requirements(value):
    if isinstance(value, (list, tuple)):
        return [security_requirement(v) for v in value]
    if value:
        requirement = security_requirement(value)
        return [requirement] if requirement else None
    return []

def security_requirement(value):
    if isinstance(value, (str)):
        return {value: []}
    if isinstance(value, dict):
        return dict(
            (k, v if isinstance(v, (list, tuple)) else [v])
            for k, v in value.items()
        )
    return None
