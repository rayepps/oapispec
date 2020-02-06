import re
from collections import OrderedDict
from collections.abc import Hashable
from urllib.parse import quote

from werkzeug.routing import parse_rule

from oapispec.model import Model
from oapispec.core.utils import merge, not_none



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

    paths = build_paths(handlers)
    models = find_models(handlers)

    return not_none({
        'swagger': '2.0',
        'basePath': parse_base_path(metadata.base_path),
        'paths': not_none(paths),
        'info': build_infos(metadata),
        'produces': metadata.representations,
        'consumes': ['application/json'],
        'securityDefinitions': metadata.authorizations or None,
        'security': security_requirements(metadata.security) or None,
        'tags': extract_tags(metadata, handlers),
        'definitions': serialize_definitions(models) or None,
        'host': metadata.host,
    })

def parse_base_path(base_path):
    if len(base_path) > 1 and base_path.endswith('/'):
        base_path = base_path[:-1]
    return base_path

def build_infos(metadata):
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

    return infos

def build_paths(handlers):
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

    return paths

def ref(model):
    '''Return a reference to model in definitions'''
    name = model.name if isinstance(model, Model) else model
    return {'$ref': '#/definitions/{0}'.format(quote(name, safe=''))}

def strip_route_types(route):
    '''Takes a route ('/path/to/<str:id>') and removes the type
    parameters ('/path/to/<id>')'''
    match = re.search(r'\/\<([a-z]+):', route)
    if not match:
        return route
    typ = match.groups()[0]
    route = route.replace(f'/<{typ}:', '/<')
    return strip_route_types(route)

def convert_path_args_to_brackets(route):
    '''Takes a route ('/path/to/<id>') and converts the
    arrows to brackets ('/path/to/{id}')'''
    match = re.search(r'\/\<([a-z_]+)\>', route)
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

        if isinstance(model, Model):
            params['payload'] = not_none({
                'name': 'payload',
                'required': True,
                'in': 'body',
                'schema': ref(model)
            })
            continue

        params['payload'] = not_none({
            'name': 'payload',
            'required': True,
            'in': 'body',
            'schema': ref(model),
            'description': description
        })

    return params

def get_operation_consumes(parameters):
    if not parameters:
        return None
    if not any(p['in'] == 'formData' for p in parameters):
        return None
    if any(p['type'] == 'file' for p in parameters):
        return ['multipart/form-data']
    return ['application/x-www-form-urlencoded', 'multipart/form-data']

def get_operation_namespace(apidoc):
    return [apidoc['namespace']['name']] if 'namespace' in apidoc else None

def get_operation_produces(apidoc):
    return [apidoc['produces']] if 'produces' in apidoc else None

def serialize_operation(apidoc):

    parameters = parameters_for(apidoc)

    operation = {
        'responses': responses_for(apidoc) or None,
        # 'summary': 'TODO-ray parse docstirng from here', # doc[method]['docstring']['summary'],
        'description': apidoc.get('description') or None,
        'operationId': apidoc.get('name'),
        'parameters': parameters,
        'security': security_for(apidoc),
        'consumes': get_operation_consumes(parameters),
        'produces': get_operation_produces(apidoc),
        'tags': get_operation_namespace(apidoc),
        'deprecated': True if apidoc.get('deprecated', False) else None
    }

    operation.update(vendor_fields(apidoc))

    return not_none(operation)

def vendor_fields(apidoc):
    '''
    Extract custom 3rd party Vendor fields prefixed with ``x-``

    See: http://swagger.io/specification/#specification-extensions-128
    '''
    return dict(
        (k if k.startswith('x-') else f'x-{k}', v)
        for k, v in apidoc.get('vendor', {}).items()
    )

def create_parameter(name, param):
    param['name'] = name

    if 'type' in param and 'schema' not in param:
        ptype = param.get('type', None)
        if isinstance(ptype, (type, type(None))) and ptype in PY_TYPES:
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

    all_params = merge(merge(expected_paramaters, doc_params), path_params)

    for name, param in all_params.items():
        param = create_parameter(name, param)
        params.append(param)

    return params if len(params) > 0 else None

def responses_for(apidoc):

    responses = {}
    global_headers = apidoc.get('headers', {})

    for code, (description, model, headers) in apidoc.get('responses', {}).items():

        description = description or 'Success'
        headers = headers or {}

        responses[code] = {'description': description}

        if model is not None:
            schema = ref(model)
            responses[code]['schema'] = schema

        responses[code] = attatch_headers(responses[code], global_headers, headers)

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

def find_models(handlers):
    models = {}
    apidoc_list = [getattr(h, '__apidoc__') for h in handlers]
    for apidoc in apidoc_list:
        for expect, _ in apidoc.get('expect', []):
            if isinstance(expect, Model):
                models[expect.name] = expect
        for _, (_, model, _) in apidoc.get('responses', {}).items():
            if isinstance(model, Model):
                models[model.name] = model
    return models

def security_for(apidoc):
    security = apidoc.get('security', None)
    return security if security is None else security_requirements(security)

def security_requirements(value):
    if not value:
        return []
    return [{value: []}]
