from oapispec.core.utils import immutable, not_none


def _eval(value):
    '''Evaluates a value - returning it or its result if its callable'''
    return value() if callable(value) else value

def create_schema(
    type='object',
    default=None,
    format=None,
    title=None,
    description=None,
    readonly=None,
    example=None,
    **kwargs):

    required = kwargs.pop('required', False)
    discriminator = kwargs.pop('discriminator', None)

    schema = not_none({
        'type': type,
        'format': format,
        'title': title,
        'description': description,
        'readOnly': readonly,
        'default': _eval(default),
        'example': example,
        **kwargs
    })

    return immutable({
        '__schema__': schema,
        'schema': lambda: schema,
        'required': required,
        'discriminator': discriminator,
        'description': description
    })

def raw(**kwargs):
    return create_schema(**kwargs)

def nested(model, as_list=False, **kwargs):

    nested_name = getattr(model, 'resolved', model).name
    ref = { '$ref': f'#/definitions/{nested_name}' }

    return create_schema(
        type='array' if as_list else None,
        **ref,
        **kwargs)

def array(item_type, min_items=None, max_items=None, unique=None, **kwargs):
    return create_schema(
        type='array',
        minItems=_eval(min_items),
        maxItems=_eval(max_items),
        uniqueItems=_eval(unique),
        items=item_type.schema(),
        **kwargs)

def string(enum=None, min_length=None, max_length=None, pattern=None, **kwargs):
    enum = _eval(enum)
    if enum and 'example' not in kwargs:
        kwargs['example'] = enum[0]

    # If a discriminator was provided
    # attempt to set required
    if kwargs.get('discriminator', False):
        # Set required True unless caller passed
        # it explicitly as False
        kwargs['required'] = True

    return create_schema(
        type='string',
        minLength=_eval(min_length),
        maxLength=_eval(max_length),
        pattern=_eval(pattern),
        enum=enum if enum else None,
        **kwargs)

def integer(minimum=None, exclusive_minimum=None, maximum=None, exclusive_maximum=None, **kwargs):
    return create_schema(
        type='integer',
        minimum=_eval(minimum),
        exclusiveMinimum=_eval(exclusive_minimum),
        maximum=_eval(maximum),
        exclusiveMaximum=_eval(exclusive_maximum),
        multipleOf=_eval(kwargs.get('multiple', None)),
        **kwargs)

def float(minimum=None, exclusive_minimum=None, maximum=None, exclusive_maximum=None, **kwargs):
    return create_schema(
        type='number',
        minimum=_eval(minimum),
        exclusiveMinimum=_eval(exclusive_minimum),
        maximum=_eval(maximum),
        exclusiveMaximum=_eval(exclusive_maximum),
        multipleOf=_eval(kwargs.get('multiple', None)),
        **kwargs)

def boolean(**kwargs):
    return create_schema(type='boolean', **kwargs)

def date_time(minimum=None, exclusive_minimum=None, maximum=None, exclusive_maximum=None, **kwargs):
    return create_schema(
        type='string',
        format='date-time',
        minimum=_eval(minimum),
        exclusiveMinimum=_eval(exclusive_minimum),
        maximum=_eval(maximum),
        exclusiveMaximum=_eval(exclusive_maximum),
        **kwargs)

def date(minimum=None, exclusive_minimum=None, maximum=None, exclusive_maximum=None, **kwargs):
    return create_schema(
        type='string',
        format='date',
        minimum=_eval(minimum),
        exclusiveMinimum=_eval(exclusive_minimum),
        maximum=_eval(maximum),
        exclusiveMaximum=_eval(exclusive_maximum),
        **kwargs)
