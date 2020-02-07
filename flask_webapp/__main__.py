"""
__main__.py
"""
import os
import pickle
import sqlite3
from datetime import date, datetime, timedelta
from flask import Flask, render_template, send_from_directory, request, jsonify, g
from flaskext.markdown import Markdown
from waitress import serve
from utils.utils import _read_czech_stopwords, _replace_all
from flask_webapp.database.db_build import DB_FILE_LOC, db_builder


APP = Flask(__name__)

# app setup
THREADS_COUNT = 4
API_PREFIX = '/api/v1/'
# load the czech stopwords file
APP.config['czech_stopwords'] = _read_czech_stopwords(czech_stopwords_file_path=
                                                      '../data_preparation/czech_stopwords.txt')

# setup Markdown ext.
Markdown(APP)

# load the markdown file content for /methodology
with open("../README.md", "r") as f:
    APP.config['md_content'] = f.read()

# pickle load ml models
VECTOR_NB = pickle.load(open('../ml_models/naive_bayes/vectorizer.pkl', 'rb'))
MODEL_NB = pickle.load(open('../ml_models/naive_bayes/model.pkl', 'rb'))
VECTOR_LR = pickle.load(open('../ml_models/logistic_regression/vectorizer.pkl', 'rb'))
MODEL_LR = pickle.load(open('../ml_models/logistic_regression/model.pkl', 'rb'))
MODEL_SVM = pickle.load(open('../ml_models/support_vector_machine/model.pkl', 'rb'))

# prepare the overall sentiment model weights
PRECISION_NB = 0.896
PRECISION_LR = 0.840
PRECISION_SVM = 0.822
PRECISION_SUM = PRECISION_NB + PRECISION_LR + PRECISION_SVM
PRECISION_NB_WEIGHT_AVG = PRECISION_NB / PRECISION_SUM
PRECISION_LR_WEIGHT_AVG = PRECISION_LR / PRECISION_SUM
PRECISION_SVM_WEIGHT_AVG = PRECISION_SVM / PRECISION_SUM

# build the DB
db_builder()

# setup the stats queries
DB_INSERT_STATS_QUERY = """
INSERT INTO 'stats'('request_datetime', 'sentiment_prediction') VALUES (?, ?);"""

DB_SELECT_STATS_QUERY_PIE_CHART = """
SELECT sum(i.cnt) as cnt, sentiment_prediction
FROM 
  (SELECT 1 as cnt, sentiment_prediction 
   FROM stats 
   WHERE request_datetime >= ? 
   UNION ALL SELECT 0 as cnt, 'negative' as sentiment_prediction
   UNION ALL SELECT 0 as cnt, 'positive' as sentiment_prediction) i
 GROUP BY sentiment_prediction ;
"""

DB_SELECT_STATS_QUERY_TIME_SERIES = """
SELECT count(*) as cnt, sentiment_prediction, date(request_datetime) as 'DATE()' 
FROM stats 
WHERE request_datetime >= ?
GROUP BY sentiment_prediction, date(request_datetime) 
ORDER BY date(request_datetime) ;"""

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_FILE_LOC)
    return db


@APP.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def _input_string_preparator(input_string):
    """
    function for input string preparation
    :param input_string:
    :return:
    """
    input_text_list_raw = input_string.split(' ')
    input_text_list = [_replace_all(x) for x in input_text_list_raw
                       if x not in APP.config['czech_stopwords'] and x != '']
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
    prediction_support_vector_machine = MODEL_SVM.predict(input_string)

    prediction_naive_bayes_prob = MODEL_NB.predict_proba(VECTOR_NB.transform(input_string))[0][0]
    prediction_logistic_regression_prob = MODEL_LR.predict_proba(VECTOR_LR.transform(input_string))[0][0]
    prediction_support_vector_machine_prob = MODEL_SVM.predict_proba(input_string)[0][0]

    # if prediction_naive_bayes[0] == 0:
    #     prediction_output['naive_bayes'] = 'negative'
    # elif prediction_naive_bayes[0] == 1:
    #     prediction_output['naive_bayes'] = 'positive'
    #
    # if prediction_logistic_regression[0] == 'neg':
    #     prediction_output['logistic_regression'] = 'negative'
    # elif prediction_logistic_regression[0] == 'pos':
    #     prediction_output['logistic_regression'] = 'positive'
    #
    # if prediction_support_vector_machine[0] == 'neg':
    #     prediction_output['support_vector_machine'] = 'negative'
    # elif prediction_support_vector_machine[0] == 'pos':
    #     prediction_output['support_vector_machine'] = 'positive'

    print(prediction_naive_bayes_prob)
    print(PRECISION_NB_WEIGHT_AVG)
    print(prediction_logistic_regression_prob)
    print(PRECISION_LR_WEIGHT_AVG)
    print(prediction_support_vector_machine_prob)
    print(PRECISION_SVM_WEIGHT_AVG)

    prediction_output_overall_proba = (prediction_naive_bayes_prob * PRECISION_NB_WEIGHT_AVG) + \
                                      (prediction_logistic_regression_prob * PRECISION_LR_WEIGHT_AVG) + \
                                      (prediction_support_vector_machine_prob * PRECISION_SVM_WEIGHT_AVG)

    if prediction_output_overall_proba < 0.48:
        prediction_output['overall_sentiment'] = 'positive'
    elif prediction_output_overall_proba > 0.52:
        prediction_output['overall_sentiment'] = 'negative'
    else:
        prediction_output['overall_sentiment'] = 'uncertain'

    print('weighted avg')
    print(prediction_output_overall_proba)
    print(prediction_output['overall_sentiment'])

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

        # to verify the input string a little bit, check if
        # at least 3 words in the input, and at least one word length > 3
        if len(input_text_list) > 2 and [i for i in input_text_list if len(i) > 3]:
            input_text_list = ' '.join(input_text_list)
            sentiment_result = _ml_model_evaluator([input_text_list])

            # store the stats data in sqlite3
            cur = get_db().cursor()
            data_tuple = (datetime.now(), sentiment_result.get('overall_sentiment'))
            cur.execute(DB_INSERT_STATS_QUERY, data_tuple)
            get_db().commit()

            return render_template('index.html',
                                   template_input_string=input_text,
                                   template_sentiment_result=sentiment_result)
        else:
            return render_template('index.html',
                                   template_input_string=input_text,
                                   template_error_message="More words for analysis needed")

@APP.route(f'{API_PREFIX}prediction/', methods=['POST'])
def api():
    """
    CURL POST example:
    curl -X POST -F Input_Text="your text for analysis" http://127.0.0.1/api/v1/prediction/
    :return:
    """
    if request.method == 'POST':
        input_text = request.form['Input_Text']
        input_text_list = _input_string_preparator(input_text)

        if len(input_text_list) > 2 and [i for i in input_text_list if len(i) > 3]:
            input_text_list = ' '.join(input_text_list)
            sentiment_result = _ml_model_evaluator([input_text_list])
            response = jsonify({
                'status': 200,
                'sentiment_result': sentiment_result,
                'mimetype': 'application/json'
            })
            response.status_code = 200
            return response
        else:
            response = jsonify({
                'status': 400,
                'error': 'More words for analysis needed',
                'mimetype': 'application/json'
            })
            response.status_code = 400
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
    return render_template('methodology.html', text=APP.config['md_content'])


@APP.route('/stats/<string:period>/', methods=['GET'])
def stats(period="week"):
    """
    the route rendering stats
    :return:
    """

    # prepare the select stats query argument
    if period == "week":
        period_from = date.today() - timedelta(weeks=1)
    elif period == "day":
        period_from = date.today() - timedelta(days=1)
    elif period == "month":
        period_from = date.today() - timedelta(weeks=4)
    elif period == "all":
        period_from = datetime.strptime("2020-01-01", '%Y-%m-%d')
    # falls back to 1 day of stats
    else:
        period_from = datetime.today() - timedelta(days=1)

    # fetch the stats data from sqlite3
    cur = get_db().cursor()
    cur.execute(DB_SELECT_STATS_QUERY_PIE_CHART, [period_from])
    pie_chart_raw_data = sorted(cur.fetchall(), key=lambda x:x[1])
    print(pie_chart_raw_data)

    cur.execute(DB_SELECT_STATS_QUERY_TIME_SERIES, [period_from])
    time_series_raw_data = sorted(cur.fetchall(), key=lambda x: (x[2], x[1]))
    print(time_series_raw_data)

    return render_template('stats.html',
                           template_pie_chart_data=[x[0] for x in pie_chart_raw_data],
                           template_pie_chart_labels=[x[1] for x in pie_chart_raw_data],
                           template_time_series_data_positive=[x[0] for x in time_series_raw_data if x[1] == "positive"],
                           template_time_series_data_negative=[x[0] for x in time_series_raw_data if x[1] == "negative"],
                           template_time_series_labels=list(set([x[2] for x in time_series_raw_data]))
                           )


if __name__ == "__main__":
    serve(APP, host='0.0.0.0', port=80, threads=THREADS_COUNT)
