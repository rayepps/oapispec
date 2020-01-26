'''
This module provide some helpers for advanced types parsing.
'''


class ipv4:
    __schema__ = {
        'type': 'string',
        'format': 'ipv4'
    }

class ipv6:
    __schema__ = {
        'type': 'string',
        'format': 'ipv6'
    }

class ip:
    __schema__ = {
        'type': 'string',
        'format': 'ip'
    }

class url:
    __schema__ = {
        'type': 'string',
        'format': 'url',
    }

class email:
    __schema__ = {
        'type': 'string',
        'format': 'email',
    }

class regex:

    def __init__(self, pattern):
        self.pattern = pattern

    @property
    def __schema__(self):
        return {
            'type': 'string',
            'pattern': self.pattern,
        }


class iso8601interval:
    '''
    Parses ISO 8601-formatted datetime intervals into tuples of datetimes.

    Accepts both a single date(time) or a full interval using either start/end
    or start/duration notation, with the following behavior:

    - Intervals are defined as inclusive start, exclusive end
    - Single datetimes are translated into the interval spanning the
      largest resolution not specified in the input value, up to the day.
    - The smallest accepted resolution is 1 second.
    - All timezones are accepted as values; returned datetimes are
      localized to UTC. Naive inputs and date inputs will are assumed UTC.
    '''
    __schema__ = {
        'type': 'string',
        'format': 'iso8601-interval'
    }

class date:
    __schema__ = {
        'type': 'string',
        'format': 'date'
    }

class natural:
    __schema__ = {
        'type': 'integer',
        'minimum': 0
    }

class positive:
    __schema__ = {
        'type': 'integer',
        'minimum': 0,
        'exclusiveMinimum': True
    }

class int_range:
    '''Restrict input to an integer in a range (inclusive)'''
    def __init__(self, low, high):
        self.low = low
        self.high = high

    @property
    def __schema__(self):
        return {
            'type': 'integer',
            'minimum': self.low,
            'maximum': self.high,
        }

class boolean:
    __schema__ = {
        'type': 'boolean'
    }

class datetime_from_iso8601:
    '''
    Turns an ISO8601 formatted date into a datetime object.
    '''
    __schema__ = {
        'type': 'string',
        'format': 'date-time'
    }

class date_from_iso8601:
    '''
    Turns an ISO8601 formatted date into a date object.
    '''
    __schema__ = {
        'type': 'string',
        'format': 'date'
    }
