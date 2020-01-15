"""
__main__.py
"""
import os
import pickle
from flask import Flask, render_template, send_from_directory, request
from waitress import serve
from utils.utils import _read_czech_stopwords


APP = Flask(__name__)
APP.config['czech_stopwords'] = _read_czech_stopwords()

VECTOR_NB = pickle.load(open('../ml_models/naive_bayes/vectorizer.pkl', 'rb'))
MODEL_NB = pickle.load(open('../ml_models/naive_bayes/model.pkl', 'rb'))
VECTOR_LR = pickle.load(open('../ml_models/logistic_regression/vectorizer.pkl', 'rb'))
MODEL_LR = pickle.load(open('../ml_models/logistic_regression/model.pkl', 'rb'))

THREADS_COUNT = 4


def _ml_model_evaluator(input_string):
    """

    :param input_string:
    :return: prediction_output dict
    """
    prediction_output = dict()
    prediction_naive_bayes = MODEL_NB.predict(VECTOR_NB.transform(input_string))
    prediction_logistic_regression = MODEL_LR.predict(VECTOR_LR.transform(input_string))

    if prediction_naive_bayes[0] == 0:
        prediction_output['naive_bayes'] = 'negativní - negative'
    elif prediction_naive_bayes[0] == 1:
        prediction_output['naive_bayes'] = 'positivní - positive'

    if prediction_logistic_regression[0] == 'neg':
        prediction_output['logistic_regression'] = 'negativní - negative'
    elif prediction_logistic_regression[0] == 'pos':
        prediction_output['logistic_regression'] = 'positivní - positive'

    return prediction_output


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
        return render_template('index.html')

    elif request.method == 'POST':
        input_text = request.form.get('InputText')
        input_text_list = input_text.split(' ')
        input_text_list = [x for x in input_text_list if x not in APP.config['czech_stopwords']
                           and x!='']

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


@APP.route('/API', methods=['GET'])
def api():
    """
    the route rendering API documentation
    :return:
    """
    return render_template('api.html')


@APP.route('/methodology', methods=['GET'])
def methodology():
    """
    the route rendering API documentation
    :return:
    """
    return render_template('methodology.html')


if __name__ == "__main__":
    serve(APP, host='0.0.0.0', port=80, threads=THREADS_COUNT)
