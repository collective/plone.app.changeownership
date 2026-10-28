from zope.schema import ValidationError


class InvalidListLength(ValidationError):
    "Invalid list length address"


def validateListLength(value):

    if not isinstance(value, (list, set)):
        raise InvalidListLength(value)

    if len(value) < 1:
        raise InvalidListLength(value)

    return True
