
from oapispec.core.openapi import OpenApi
from oapispec.core.utils import immutable


def schema(handlers=None, metadata=None):

    handlers = handlers or []
    metadata = metadata or {}
    metadata = meta(**metadata)

    def register(handler):
        return schema(handlers=[*handlers, handler], metadata=metadata)

    def generate():
        return OpenApi(metadata, handlers).as_dict()

    return immutable(dict(
        register=register,
        generate=generate,
        handlers=handlers,
        metadata=metadata
    ))


def meta(
    version='1.0',
    title='API',
    host=None,
    description=None,
    terms_url=None,
    contact=None,
    contact_url=None,
    contact_email=None,
    license=None,
    license_url=None,
    authorizations=None,
    security=None,
    tags=None,
    base_path='/',
    representations=None):

    return immutable(dict(
        version=version,
        title=title,
        host=host,
        description=description,
        terms_url=terms_url,
        contact=contact,
        contact_url=contact_url,
        contact_email=contact_email,
        license=license,
        license_url=license_url,
        authorizations=authorizations,
        security=security,
        tags=tags or [],
        base_path=base_path,
        representations=representations or ['application/json']
    ))
