'''The doc module provides decorator functions that will modify a
functions __apidoc__ object. For example, when using `method('GET')`
it will set the value of the functions method as 'get' on its __apidoc__'''

from http import HTTPStatus

from oapispec.core.utils import merge, not_none


def doc(**kwargs):
    '''A decorator to add documentation metadata to the decorated function'''
    def wrapper(documented):
        current_doc = getattr(documented, '__apidoc__', {})
        if 'name' not in current_doc:
            kwargs['name'] = documented.__name__
        documented.__apidoc__ = merge(current_doc, kwargs)
        return documented
    return wrapper

def route(endpoint):
    '''
    A decorator to route resources.
    '''
    return doc(route=endpoint)

def hide(func):
    '''A decorator to hide a resource or a method from specifications'''
    return doc()(func)

def expect(model, description=None):
    '''
    A decorator to Specify the expected input model

    :param ModelBase inputs: An expect model
    :param bool validate: whether to perform validation or not

    '''
    return doc(expect=[(model, description)])

def param(name, type=str, location='query', description=None, format=None, required=False, default=None):
    '''
    A decorator to specify one of the expected parameters

    :param str name: the parameter name
    :param str description: a small description
    :param str location: the parameter location `(query|header|formData|body|cookie)`
    '''
    return doc(params={
        name: not_none({
            'in': location,
            'type': type,
            'format': format,
            'default': default,
            'required': True if required else None,
            'description': description
        })
    })

def response(http_status: HTTPStatus, model=None, headers=None):
    '''
    A decorator to specify one of the expected responses

    :param HTTPStatus http_status: the HTTP status (or any object with a 'value' and 'description' property)
    :param ModelBase model: an optional response model
    :param dict<str, header> headers: an optional dict of headers that are returned with this response
    '''
    code = http_status.value
    description = http_status.description
    return doc(responses={str(code): (description, model, headers)})

def header(name, description=None, **kwargs):
    '''
    A decorator to specify one of the expected headers

    :param str name: the HTTP header name
    :param str description: a description about the header

    '''
    return doc(headers={
        name: {
            'description': description
        },
        **kwargs
    })

def produces(mimetypes):
    '''A decorator to specify the MIME types the API can produce'''
    return doc(produces=mimetypes)

def deprecated(func):
    '''A decorator to mark a resource or a method as deprecated'''
    return doc(deprecated=True)(func)

def vendor(*args, **kwargs):
    '''
    A decorator to expose vendor extensions.

    Extensions can be submitted as dict or kwargs.
    The ``x-`` prefix is optionnal and will be added if missing.

    See: http://swagger.io/specification/#specification-extensions-128
    '''
    for arg in args:
        kwargs.update(arg)
    return doc(vendor=kwargs)

def method(http_method):
    '''A decorator to set the method for the handler'''
    return doc(method=http_method.lower())

def namespace(name, description=None):
    '''A decorator that groups the decorated handler function in a namespace'''
    return doc(namespace=not_none({
        'name': name,
        'description': description
    }))
