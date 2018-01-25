"""Common utilities across all backends.

Classes
-------
InvalidObjectClassError
InvalidObjectError
"""


class InvalidObjectClassError(Exception):
    def __init__(self, objclass, valid):
        msg = "{} is not a valid class of object in the database. " \
            .format(objclass)
        msg += "Valid classes are: {}".format(list(valid))
        super(InvalidObjectClassError, self).__init__(msg)


class InvalidObjectError(Exception):
    def __init__(self, obj):
        msg = "{} is not an instance of a valid database object. ".format(obj)
        msg += "This object may be of an unknown class or may be malformed."
        super(InvalidObjectError, self).__init__(msg)
