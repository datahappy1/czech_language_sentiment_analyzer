"""
project common helper functions
"""


def _replace_all(text):
    """
    multi replace string function
    :param text:
    :return:
    """
    replacements = {'"': '', '.': '', '(': '', ')': '', ',': '',
                    '-': '', '?': '', '!': '', ':': '', '/': '',
                    }

    for i, j in replacements.items():
        text = text.replace(i, j)
    return text
