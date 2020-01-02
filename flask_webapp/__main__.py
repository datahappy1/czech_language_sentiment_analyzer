"""
__main__.py
"""
import os
from flask import Flask, render_template, send_from_directory, request
from waitress import serve
from CLI.sentiment_analyzer import get_sentiment

APP = Flask(__name__)

THREADS_COUNT = 4


@APP.route('/favicon.ico')
def favicon():
    """
    function to properly handle favicon
    :return:
    """
    return send_from_directory(os.path.join(APP.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@APP.route('/', methods=['GET', 'POST'])
def main():
    """
    the main route rendering index.html
    :return:
    """
    if request.method == 'GET':
        return render_template('index.html', template_sentiment_result=None)

    elif request.method == 'POST':
        input_text = request.form.get('InputText')
        level = 'low'
        fuzzy = request.form.get('FuzzyMatch')

        prepared_args = {'string': input_text,
                         'level': level,
                         'fuzzy': (True if fuzzy else False)}

        sentiment_result = get_sentiment(prepared_args)

        return render_template('index.html',
                               template_input_string=input_text,
                               template_fuzzy=(True if fuzzy else False),
                               template_sentiment_result=sentiment_result)


@APP.route('/API', methods=['GET'])
def api():
    """
    the route rendering API documentation
    :return:
    """
    return render_template('api.html')


if __name__ == "__main__":
    serve(APP, host='0.0.0.0', port=80, threads=THREADS_COUNT)
