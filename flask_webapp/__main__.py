"""
__main__.py
"""
import os
import pickle
from flask import Flask, render_template, send_from_directory, request
from waitress import serve

APP = Flask(__name__)

VECTOR = pickle.load(open('../ml_models/logistic_regression/vectorizer.pkl', 'rb'))
MODEL = pickle.load(open('../ml_models/logistic_regression/model.pkl', 'rb'))

THREADS_COUNT = 4


def _ml_model_evaluator(input_string):
    """

    :param input_string:
    :return:
    """
    prediction = MODEL.predict(VECTOR.transform(input_string))
    if prediction[0] == 'neg':
        prediction_output = 'negativní - negative'
    elif prediction[0] == 'pos':
        prediction_output = 'positivní - positive'
    else:
        prediction_output = 'neznámý - unknown'

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
        sentiment_result = _ml_model_evaluator([input_text])

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
