"""
__main__.py
"""
import os
import pickle
from flask import Flask, render_template, send_from_directory, request, jsonify
from waitress import serve
from utils.utils import _read_czech_stopwords


APP = Flask(__name__)
APP.config['czech_stopwords'] = _read_czech_stopwords(czech_stopwords_file_path=
                                                      '../data_preparation/czech_stopwords.txt')

VECTOR_NB = pickle.load(open('../ml_models/naive_bayes/vectorizer.pkl', 'rb'))
MODEL_NB = pickle.load(open('../ml_models/naive_bayes/model.pkl', 'rb'))
VECTOR_LR = pickle.load(open('../ml_models/logistic_regression/vectorizer.pkl', 'rb'))
MODEL_LR = pickle.load(open('../ml_models/logistic_regression/model.pkl', 'rb'))

THREADS_COUNT = 4
API_PREFIX = '/api/v1/'


def _input_string_preparator(input_string):
    """
    function for input string preparation
    :param input_string:
    :return:
    """
    input_text_list = input_string.split(' ')
    input_text_list = [x for x in input_text_list if x not in APP.config['czech_stopwords']
                       and x != '']
    return input_text_list


def _ml_model_evaluator(input_string):
    """
    function for machine learning model evaluation
    :param input_string:
    :return: prediction_output dict
    """
    prediction_output = dict()
    prediction_naive_bayes = MODEL_NB.predict(VECTOR_NB.transform(input_string))
    prediction_logistic_regression = MODEL_LR.predict(VECTOR_LR.transform(input_string))

    if prediction_naive_bayes[0] == 0:
        prediction_output['naive_bayes'] = 'negative'
    elif prediction_naive_bayes[0] == 1:
        prediction_output['naive_bayes'] = 'positive'

    if prediction_logistic_regression[0] == 'neg':
        prediction_output['logistic_regression'] = 'negative'
    elif prediction_logistic_regression[0] == 'pos':
        prediction_output['logistic_regression'] = 'positive'

    return prediction_output


@APP.route('/favicon.ico')
def favicon():
    """
    function to properly handle favicon
    :return:
    """
    return send_from_directory(os.path.join(APP.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@APP.errorhandler(405)
def not_allowed(error):
    """
    not allowed method error handler function
    :param error:
    :return:error html page or api response
    """
    if request.path.startswith(API_PREFIX):
        response = jsonify({
            'status': 405,
            'error': str(error),
            'mimetype': 'application/json'
        })
        response.status_code = 405
        return response
    return render_template('error_page.html', template_error_message=error)


@APP.errorhandler(404)
def not_found(error):
    """
    not found app error handler function
    :param error:
    :return:error html page or api response
    """
    if request.path.startswith(API_PREFIX):
        response = jsonify({
            'status': 404,
            'error': str(error),
            'mimetype': 'application/json'
        })
        response.status_code = 404
        return response
    return render_template('error_page.html', template_error_message=error)


@APP.route('/', methods=['GET', 'POST'])
def main():
    """
    the main route rendering index.html
    :return:
    """
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        input_text = request.form.get('InputText')
        input_text_list = _input_string_preparator(input_text)

        if len(input_text_list) < 2:
            return render_template('index.html',
                                   template_input_string=input_text,
                                   template_error_message="More words for analysis needed")

        else:
            input_text_list = ' '.join(input_text_list)
            sentiment_result = _ml_model_evaluator([input_text_list])
            return render_template('index.html',
                                   template_input_string=input_text,
                                   template_sentiment_result=sentiment_result)


@APP.route(API_PREFIX, methods=['POST'])
def api():
    """
    CURL POST example:
    curl -X POST -F Input_Text="your text for analysis" http://127.0.0.1/api/v1/
    :return:
    """
    if request.method == 'POST':
        input_text = request.form['Input_Text']
        input_text_list = _input_string_preparator(input_text)

        if len(input_text_list) < 2:
            response = jsonify({
                'status': 400,
                'error': 'More words for analysis needed',
                'mimetype': 'application/json'
            })
            response.status_code = 400
            return response
        else:
            input_text_list = ' '.join(input_text_list)
            sentiment_result = _ml_model_evaluator([input_text_list])
            response = jsonify({
                'status': 200,
                'sentiment_result': sentiment_result,
                'mimetype': 'application/json'
            })
            response.status_code = 200
            return response


@APP.route('/API_DOCS', methods=['GET'])
def api_docs():
    """
    the route rendering API documentation
    :return:
    """
    return render_template('api_docs.html')


@APP.route('/methodology', methods=['GET'])
def methodology():
    """
    the route rendering API documentation
    :return:
    """
    return render_template('methodology.html')


@APP.route('/stats', methods=['GET'])
def stats():
    """
    the route rendering stats
    :return:
    """
    return render_template('stats.html')


if __name__ == "__main__":
    serve(APP, host='0.0.0.0', port=80, threads=THREADS_COUNT)
