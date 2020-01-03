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
        sentiment_result = []

        input_text = request.form.get('InputText')
        fuzzy = bool(request.form.get('FuzzyMatch'))
        fuzzy_ratio = int(request.form.get('iFuzzyratio'))
        algorithm_type = request.form.get('AlgorithmTypeSelect')

        if algorithm_type == 'all':
            for algorithm in ['small', 'big', 'affin111']: #TODO add 'naivebayes'
                prepared_args = {'string': input_text,
                                 'level': algorithm,
                                 'fuzzy': fuzzy,
                                 'ratio': fuzzy_ratio}
                sentiment_result.append(get_sentiment(prepared_args))

        else:
            prepared_args = {'string': input_text,
                             'level': algorithm_type,
                             'fuzzy': fuzzy,
                             'ratio': fuzzy_ratio}

            sentiment_result.append(get_sentiment(prepared_args))

        return render_template('index.html',
                               template_input_string=input_text,
                               template_algorithm_type=algorithm_type,
                               template_fuzzy=fuzzy,
                               template_fuzzy_ratio=fuzzy_ratio,
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
