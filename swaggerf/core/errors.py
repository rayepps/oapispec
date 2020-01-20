# -*- coding: utf-8 -*-


class RestError(Exception):
    '''Base class for all Flask-RESTX Errors'''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ValidationError(Exception):
    '''A helper class for validation errors.'''
    def __init__(self, errors):
        self.errors = errors


class SpecsError(Exception):
    '''A helper class for incoherent specifications.'''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
