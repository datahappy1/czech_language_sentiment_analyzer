"""
utilities module
"""
import os
import re
import functools
from itertools import groupby, product
from data_preparation import czech_stemmer


CZECH_STOPWORDS_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                                         'data_preparation', 'czech_stopwords.txt'))

MARKDOWN_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'README.md'))


class ProjectCommon:
    """
    project common helpers class
    """
    @staticmethod
    @functools.lru_cache()
    def read_czech_stopwords(czech_stopwords_file_path) -> list:
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

    @staticmethod
    def remove_czech_stopwords(text) -> str:
        """
        function removing czech stopwords from input text
        :param text:
        :return:
        """
        replacements = {x: '' for x in
                        ProjectCommon.read_czech_stopwords(CZECH_STOPWORDS_FILE_PATH)}
        output = [w for w in text.split(' ') if w not in replacements]

        return ' '.join(output)

    @staticmethod
    def remove_html(raw_text) -> str:
        """
        function to clean html tags contents from the input string
        :param raw_text:
        :return:
        """
        clean_r = re.compile('<.*?>')
        clean_text = re.sub(clean_r, '', raw_text)

        return clean_text

    @staticmethod
    def remove_non_alpha_chars(text) -> str:
        """
        function for replacing all occurrences of non alpha chars in the input string
        :param text:
        :return:
        """
        replacements = {'"': '', '.': '', '(': '', ')': '', ',': '',
                        '-': '', '?': '', '!': '', ':': '', '/': '', '„': '',
                        '  ': ' ', '   ': ' ', '%': '', '“': '', '*': '', '+': ''}

        for i, j in replacements.items():
            text = text.replace(i, j)

        return text

    @staticmethod
    def remove_diacritics(text) -> str:
        """
        function for replacing all occurrences of Czech diacritics in the input string
        :param text:
        :return:
        """
        replacements = {'ě': 'e', 'š': 's', 'č': 'c', 'ř': 'r', 'ž': 'z', 'ý':'y',
                        'á': 'a', 'í': 'i', 'é': 'e', 'ů': 'u', 'ú': 'u'}

        for i, j in replacements.items():
            text = text.replace(i, j)

        return text

    @staticmethod
    def trimmer(text) -> str:
        """
        function removing left and right trims
        :param text:
        :return:
        """
        text_output_trimmed = text.lstrip(' ').rstrip(' ')

        return text_output_trimmed

    @staticmethod
    def remove_non_alpha_chars_and_html(text) -> str:
        """
        function for removals of all non alpha chars and html in the input string
        :param text:
        :return:
        """
        text_output_trimmed = ProjectCommon.trimmer(text)

        text_output_no_html = ProjectCommon.remove_html(text_output_trimmed)

        text_output_no_html_no_non_alpha_chars = \
            ProjectCommon.remove_non_alpha_chars(text_output_no_html)

        return text_output_no_html_no_non_alpha_chars

    @staticmethod
    def remove_all(text) -> str:
        """
        function for running all-in-one replace functions
        :param text:
        :return:
        """
        text_output_no_html_no_non_alpha_chars = \
            ProjectCommon.remove_non_alpha_chars_and_html(text)

        text_output_no_html_no_non_alpha_chars_no_stopwords = \
            ProjectCommon.remove_czech_stopwords(text_output_no_html_no_non_alpha_chars)

        text_output_no_html_no_non_alpha_chars_no_stopwords_stemmed = \
            czech_stemmer.stemmer(text_output_no_html_no_non_alpha_chars_no_stopwords)

        text_output_no_html_no_non_alpha_chars_no_stopwords_stemmed_no_diacritics = \
            ProjectCommon.\
                remove_diacritics(text_output_no_html_no_non_alpha_chars_no_stopwords_stemmed)

        return text_output_no_html_no_non_alpha_chars_no_stopwords_stemmed_no_diacritics


class Webapp:
    """
    web application helpers class
    """
    @staticmethod
    def input_string_preparator(input_string) -> list:
        """
        function for input string preparation
        :param input_string:
        :return:
        """
        input_text_list_raw = re.split(';|,|[ ]|-|[?]|[!]|\n', input_string)
        input_text_list = [ProjectCommon.remove_all(x) for x in input_text_list_raw if x != '']

        return input_text_list

    @staticmethod
    def chart_data_preparator(input_data_set) -> dict:
        """
        function for transforming raw SQL fetched data
        to Charts.js compatible data structures
        :param input_data_set:
        :return:
        """
        all_charts_output = {'pie_by_sentiment': {'group_keys': [], 'output_data_set': []},
                             'time_series': {'group_keys': [], 'output_data_set': []}}

        cart_prod_sentiment = []
        pie_chart_by_sentiment_output = []
        time_series_output = []

        # let's prepare the cartesian product dataset
        dates = list(set([x[0] for x in input_data_set]))
        sentiment_values = ['negative', 'positive', 'uncertain']

        # let's add 0 to each row from the cartesian product dataset for sum
        for item in product(sentiment_values, dates):
            cart_prod_sentiment.append((item[1], item[0], 0))

        # let's add 1 to each row from the query fetched results for sum
        _input_data_set = [x.__add__((1,)) for x in input_data_set]

        # let's extend the _input_data_set with the cart_prod dataset
        _input_data_set.extend(cart_prod_sentiment)

        # pie chart by sentiment
        # let's sort the resulting dataset by date and sentiment values
        _data_set_for_grouping = sorted(_input_data_set, key=lambda x: (x[1]))

        # let's do the grouping of this dataset and sum the 1's and 0's
        for key, group in groupby(_data_set_for_grouping, lambda x: x[1]):
            _grouped_item = sum(r[2] for r in group), key
            pie_chart_by_sentiment_output.append(_grouped_item)

        all_charts_output['pie_by_sentiment']['group_keys'] = sorted(sentiment_values)
        all_charts_output['pie_by_sentiment']['output_data_set'] = pie_chart_by_sentiment_output

        # time series chart
        # let's sort the resulting dataset by date and sentiment values
        _data_set_for_grouping = sorted(_input_data_set, key=lambda x: (x[0], x[1]))

        # let's do the grouping of this dataset and sum the 1's and 0's
        for key, group in groupby(_data_set_for_grouping, lambda x: (x[0], x[1])):
            _grouped_item = sum(r[2] for r in group), key[0], key[1]
            time_series_output.append(_grouped_item)

        all_charts_output['time_series']['group_keys'] = sorted(dates)
        all_charts_output['time_series']['output_data_set'] = time_series_output

        return all_charts_output

    @staticmethod
    def markdown_reader():
        """
        function for reading markdown file
        :return:
        """
        with open(MARKDOWN_FILE_PATH, "r") as markdown_file_handler:
            return markdown_file_handler.read()
