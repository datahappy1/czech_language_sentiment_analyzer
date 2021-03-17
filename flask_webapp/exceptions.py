"""
exceptions.py
"""


class NotEnoughNonStopWordsException(Exception):
    """
    Not Enough Non Stop Words Exception Class
    """


class NotEnoughWordsLengthException(Exception):
    """
    Not Enough Words Length Exception Class
    """


class InvalidDetectedLanguageException(Exception):
    """
    Invalid Detected Language Exception Class
    """


class GenericException(Exception):
    """
    Generic Exception Class
    """


EXCEPTION_TYPE_RESPONSE_MESSAGE_MAP = {
    "NotEnoughNonStopWordsException":
        "Sorry, need to submit at least 3 non stop-words",
    "NotEnoughWordsLengthException":
        "Sorry, need to submit at least 1 word with 3 and more characters",
    "InvalidDetectedLanguageException":
        "Sorry, need to submit text written in Czech",
    "GenericException":
        "Sorry, something went wrong"
}
