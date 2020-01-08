"""
project common helper functions
"""


CZECH_STOPWORDS_FILE_PATH = '../data_preparation/czech_stopwords.txt'


def _read_czech_stopwords() -> list:
    """
    function reading czech stopwords file and storing it to a list
    :return:czech_stopwords
    """
    czech_stopwords = []

    with open(CZECH_STOPWORDS_FILE_PATH, 'r', encoding='utf8') as stop_word_file:
        for line in stop_word_file:
            czech_stopwords.append(line[:-1])

    return czech_stopwords


def _replace_all(text) -> str:
    """
    multi replace string function
    :param text:
    :return:
    """
    replacements = {'"': '', '.': '', '(': '', ')': '', ',': '',
                    '-': '', '?': '', '!': '', ':': '', '/': '',
                    '„': '' , '<strong>': '', '<em>': ''}
    #TODO replace ě : e, š : s... and retrain models and scrub the input text against this function
    for i, j in replacements.items():
        text = text.replace(i, j)
    return text
