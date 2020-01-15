"""
project common helper functions
"""


def _read_czech_stopwords(czech_stopwords_file_path) -> list:
    """
    function reading czech stopwords file and storing it to a list
    :param czech_stopwords_file_path
    :return:czech_stopwords
    """
    czech_stopwords = []

    with open(czech_stopwords_file_path, 'r', encoding='utf8') as stop_word_file:
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
                    '„': '' , '<strong>': '', '<em>': '', 'ě': 'e',
                    'š': 's', 'č': 'c', 'ř': 'r', 'ž': 'z', 'ý':'y',
                    'á': 'a', 'í': 'i', 'é': 'e', 'ů': 'u', 'ú': 'u'}

    for i, j in replacements.items():
        text = text.replace(i, j)
    return text
