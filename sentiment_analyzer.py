"""
sentiment analyzer CLI tool
"""
import argparse
import logging
from fuzzywuzzy import fuzz

CZECH_STOPWORDS = []

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
LOGGER = logging.getLogger(__name__)


def _read_czech_stopwords():
    """
    read czech stopwords from czech_stopwords.txt file to a list
    :return:
    """
    with open("./data_preparation/czech_stopwords.txt", 'r', encoding='utf8') as stop_word_file:
        for line in stop_word_file:
            CZECH_STOPWORDS.append(line[:-1])


def _read_valence_file_generator(valence_file):
    """
    read valence file generator
    :return: yield rows
    """
    for row in open(valence_file, encoding="utf8"):
        yield row[:-1]


def read_valence_file(level):
    """
    function opening the expected valence file based on the level input
    and populating a dictionary with the words and their corresponding valence
    values
    :param level:
    :return:
    """
    if level == "low":
        valence_file = open("./data_preparation/data_output/"
                            "small_czech_words_list_w_word_valence.txt", encoding='utf8')

    elif level == "high":
        valence_file = _read_valence_file_generator("./data_preparation/data_output/"
                                                    "big_czech_words_list_w_word_valence.txt")

    else:
        raise FileNotFoundError

    scores = {}
    for line in valence_file:
        term, score = line.split()
        scores[term] = float(score)

    LOGGER.info('file with word and corresponding valence pairs loaded successfully')

    return scores.items()


def get_sentiment(prepared_args):
    """
    function calculating the sentiment score
    :param prepared_args:
    :return: sentiment value
    """
    _read_czech_stopwords()

    valence_file = read_valence_file(prepared_args['level'])
    words = prepared_args['string'].split()
    fuzzy = prepared_args['fuzzy']
    fuzzy_threshold = 0
    if prepared_args['level'] == "high":
        fuzzy_threshold = 70
    elif prepared_args['level'] == "low":
        fuzzy_threshold = 52
    sentiment_value = 0.0
    sentiment_details = []
    _match_counter = 0

    for word in words:
        if word not in CZECH_STOPWORDS:
            for item in valence_file:
                if word in item:
                    _match_counter += 1
                    sentiment_value += item[1]
                    sentiment_details.append({'word': word,
                                              'sentiment_value': item[1]})
                elif fuzzy is True:
                    ratio = fuzz.ratio(word, item)
                    if ratio > fuzzy_threshold:
                        _match_counter += 1
                        sentiment_value += item[1]
                        sentiment_details.append({'word': word,
                                                  'sentiment_value': item[1],
                                                  'fuzzy_ratio': ratio})
                else:
                    pass

    if _match_counter > 0:
        LOGGER.info('Sentiment calculated successfully')
        return sentiment_value, sentiment_details
    else:
        LOGGER.warning('No values for sentiment analysis found')
        return None, None


def prepare_args():
    """
    function for preparation of the CLI arguments
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-string', '--inputstring', type=str, required=True)
    parser.add_argument('-level', '--depthlevel', type=str, required=False, default='low',
                        choices=['low', 'high'])
    parser.add_argument('-fuzzy', '--fuzzymatch', type=str, required=False, default=False)
    parsed = parser.parse_args()

    string = parsed.inputstring
    level = parsed.depthlevel
    fuzzy = parsed.fuzzymatch
    # arg parse bool data type known bug workaround
    if fuzzy.lower() in ('no', 'false', 'f', 'n', '0'):
        fuzzy = False
    else:
        fuzzy = True

    LOGGER.info('arguments parsed successfully')

    return {'string': string,
            'level': level,
            'fuzzy': fuzzy}


if __name__ == '__main__':
    PREPARED_ARGS = prepare_args()
    SENTIMENT_RESULT, SENTIMENT_DETAILS = get_sentiment(PREPARED_ARGS)
    LOGGER.info('Sentiment value is: %s', SENTIMENT_RESULT)
    LOGGER.info('Sentiment value details: %s', SENTIMENT_DETAILS)
