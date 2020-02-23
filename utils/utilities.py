"""
project common helper functions
"""
import os
import re
import functools
from itertools import groupby

CZECH_STOPWORDS_FILE_PATH = 'data_preparation/czech_stopwords.txt'
MARKDOWN_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'README.md'))


class ProjectCommon:
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
    def replace_html(raw_text) -> str:
        """
        function to clean html tags contents from the input string
        :param raw_text:
        :return:
        """
        clean_r = re.compile('<.*?>')
        clean_text = re.sub(clean_r, '', raw_text)

        return clean_text


    @staticmethod
    def replace_non_alpha_chars(text) -> str:
        """
        multi replace non alpha string function
        :param text:
        :return:
        """
        replacements = {'"': '', '.': '', '(': '', ')': '', ',': '',
                        '-': '', '?': '', '!': '', ':': '', '/': '', '„': '' ,
                        '  ': ' ', '   ': ' ', '%': '', '“': '', }

        for i, j in replacements.items():
            text = text.replace(i, j)

        return text


    @staticmethod
    def replace_diacritics(text) -> str:
        """
        multi replace diacritics string function
        :param text_output:
        :return:
        """
        replacements = {'ě': 'e', 'š': 's', 'č': 'c', 'ř': 'r', 'ž': 'z', 'ý':'y',
                        'á': 'a', 'í': 'i', 'é': 'e', 'ů': 'u', 'ú': 'u'}

        for i, j in replacements.items():
            text = text.replace(i, j)

        return text


    @staticmethod
    def replace_all(text) -> str:
        """
        multi replace all function
        :param text:
        :return:
        """
        text_output_no_html = ProjectCommon.replace_html(text)

        text_output_no_html_no_non_alpha_chars = \
            ProjectCommon.replace_non_alpha_chars(text_output_no_html)

        text_output_no_html_no_non_alpha_chars_no_diacritics = \
            ProjectCommon.replace_diacritics(text_output_no_html_no_non_alpha_chars)

        return text_output_no_html_no_non_alpha_chars_no_diacritics


class Webapp:
    @staticmethod
    def input_string_preparator(input_string) -> list:
        """
        function for input string preparation
        :param input_string:
        :return:
        """
        czech_stopwords_list = ProjectCommon.read_czech_stopwords(CZECH_STOPWORDS_FILE_PATH)

        input_text_list_raw = input_string.split(' ')
        input_text_list = [ProjectCommon.replace_all(x) for x in input_text_list_raw
                           if x not in czech_stopwords_list and x != '']

        return input_text_list

    @staticmethod
    def chart_data_preparator(input_data_set) -> dict:
        """
        function for transforming raw SQL fetched data
        to Charts.js compatible data structures
        :param input_data_set:
        :return:
        """
        all_charts_output = {'pie_by_source':{'group_keys': [], 'output_data_set': []},
                             'pie_by_sentiment': {'group_keys': [], 'output_data_set': []},
                             'time_series': {'group_keys': [], 'output_data_set': []}}

        # pie chart by source
        _sorted_data = sorted(input_data_set, key=lambda x: x[1])
        for k, g in groupby(_sorted_data, lambda x: x[1]):
            all_charts_output['pie_by_source']['group_keys'].append(k)
            all_charts_output['pie_by_source']['output_data_set'].append((len(list(g)), k))

        # pie chart by sentiment
        _sorted_data = sorted(input_data_set, key=lambda x: x[2])
        for k, g in groupby(_sorted_data, lambda x: x[2]):
            all_charts_output['pie_by_sentiment']['group_keys'].append(k)
            all_charts_output['pie_by_sentiment']['output_data_set'].append((len(list(g)), k))

        # time series chart
        _sorted_data = sorted(input_data_set, key=lambda x: (x[0], x[2]))
        for k, g in groupby(_sorted_data, lambda x: (x[0], x[2])):
            all_charts_output['time_series']['group_keys'].append(k[0])
            all_charts_output['time_series']['output_data_set'].append((len(list(g)), k[1], k[0]))

        return all_charts_output

    @staticmethod
    def markdown_reader():
        """
        markdown file reader function
        :param markdown_file_path:
        :return:
        """
        with open(MARKDOWN_FILE_PATH, "r") as f:
            return f.read()
