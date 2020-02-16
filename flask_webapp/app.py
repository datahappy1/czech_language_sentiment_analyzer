"""
__main__.py
"""
import os
import pickle
from datetime import date, datetime, timedelta
from itertools import groupby
from flask import Flask, render_template, send_from_directory, request, jsonify, g
from flaskext.markdown import Markdown
from flask_caching import Cache
from waitress import serve
from utils.utils import _read_czech_stopwords, _replace_all
from flask_webapp.database import __env__
from flask_webapp.database.db_abstraction import Database


app = Flask(__name__)

# app setup
API_PREFIX = '/api/v1/'
# load the czech stopwords file
app.config['czech_stopwords'] = _read_czech_stopwords(czech_stopwords_file_path=
                                                      'data_preparation/czech_stopwords.txt')

# bind flask-markdown extension to your app
Markdown(app)

# setup Cache ext.
app.config['CACHE_TYPE'] = 'simple'

# register the cache instance and bind it to your app
app.cache = Cache(app)

# load the markdown file content for /methodology
with open("README.md", "r") as f:
    app.config['md_content'] = f.read()

# pickle load ml models
VECTOR_NB = pickle.load(open('ml_models/naive_bayes/vectorizer.pkl', 'rb'))
MODEL_NB = pickle.load(open('ml_models/naive_bayes/model.pkl', 'rb'))
VECTOR_LR = pickle.load(open('ml_models/logistic_regression/vectorizer.pkl', 'rb'))
MODEL_LR = pickle.load(open('ml_models/logistic_regression/model.pkl', 'rb'))
MODEL_SVM = pickle.load(open('ml_models/support_vector_machine/model.pkl', 'rb'))

# prepare the overall sentiment model weights
PRECISION_NB = 0.896
PRECISION_LR = 0.840
PRECISION_SVM = 0.822
PRECISION_SUM = PRECISION_NB + PRECISION_LR + PRECISION_SVM
PRECISION_NB_WEIGHT_AVG = PRECISION_NB / PRECISION_SUM
PRECISION_LR_WEIGHT_AVG = PRECISION_LR / PRECISION_SUM
PRECISION_SVM_WEIGHT_AVG = PRECISION_SVM / PRECISION_SUM

# build the DB
Db_obj = Database(__env__)
Database.db_builder(Db_obj)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = Database.connect(Db_obj)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def _write_stats_to_table(source, sentiment_result):
    """
    function storing stats data in a table
    :param source: api or website
    :param sentiment_result:
    :return:
    """
    try:
        cur = get_db().cursor()
        data_tuple = (datetime.now(), source, sentiment_result)
        cur.execute(Db_obj.db_insert_stats_query, data_tuple)
        get_db().commit()
    except Exception:
        # storing the stats cannot block the user from retrieving sentiment
        pass


def _input_string_preparator(input_string):
    """
    function for input string preparation
    :param input_string:
    :return:
    """
    input_text_list_raw = input_string.split(' ')
    input_text_list = [_replace_all(x) for x in input_text_list_raw
                       if x not in app.config['czech_stopwords'] and x != '']
    return input_text_list


def _ml_model_evaluator(input_string):
    """
    function for machine learning model evaluation
    :param input_string:
    :return: prediction_output dict
    """
    prediction_output = dict()
    # prediction_naive_bayes = MODEL_NB.predict(VECTOR_NB.transform(input_string))
    # prediction_logistic_regression = MODEL_LR.predict(VECTOR_LR.transform(input_string))
    # prediction_support_vector_machine = MODEL_SVM.predict(input_string)

    prediction_naive_bayes_prob = MODEL_NB.predict_proba(VECTOR_NB.transform(input_string))[0][0]
    prediction_logistic_regression_prob = MODEL_LR.predict_proba(VECTOR_LR.transform(input_string))[0][0]
    prediction_support_vector_machine_prob = MODEL_SVM.predict_proba(input_string)[0][0]

    prediction_output_overall_proba = round((prediction_naive_bayes_prob * PRECISION_NB_WEIGHT_AVG) + \
                                      (prediction_logistic_regression_prob * PRECISION_LR_WEIGHT_AVG) + \
                                      (prediction_support_vector_machine_prob * PRECISION_SVM_WEIGHT_AVG), 2)

    if prediction_output_overall_proba < 0.48:
        prediction_output['overall_sentiment'] = {'sentiment': 'positive',
                                                  'probability': prediction_output_overall_proba}
    elif prediction_output_overall_proba > 0.52:
        prediction_output['overall_sentiment'] = {'sentiment': 'negative',
                                                  'probability': prediction_output_overall_proba}
    else:
        prediction_output['overall_sentiment'] = {'sentiment': 'uncertain',
                                                  'probability': prediction_output_overall_proba}

    return prediction_output


@app.route('/favicon.ico')
def favicon():
    """
    function to properly handle favicon
    :return:
    """
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(405)
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


@app.errorhandler(404)
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


@app.route('/', methods=['GET', 'POST'])
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

            _write_stats_to_table(source='website',
                                  sentiment_result=sentiment_result.get('overall_sentiment').get('sentiment'))

            return render_template('index.html',
                                   template_input_string=input_text,
                                   template_sentiment_result=sentiment_result)
        else:
            return render_template('index.html',
                                   template_input_string=input_text,
                                   template_error_message="More words for analysis needed")


@app.route(f'{API_PREFIX}prediction/', methods=['POST'])
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

            _write_stats_to_table(source='api',
                                  sentiment_result=sentiment_result.get('overall_sentiment').get('sentiment'))

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


@app.route('/api_docs', methods=['GET'])
def api_docs():
    """
    the route rendering API documentation
    :return:
    """
    return render_template('api_docs.html')


@app.route('/methodology', methods=['GET'])
def methodology():
    """
    the route rendering methodology documentation
    from the repo README.md markdown
    :return:
    """
    return render_template('methodology.html', text=app.config['md_content'])


@app.route('/stats/<string:period>/', methods=['GET'])
@app.cache.cached(timeout=60)  # cache this view for 1 minute
def stats(period="day"):
    """
    the route rendering stats
    :return:
    """

    # prepare the select stats query argument
    if period == "day":
        period_from = date.today() - timedelta(days=1)
    elif period == "week":
        period_from = date.today() - timedelta(weeks=1)
    elif period == "month":
        period_from = date.today() - timedelta(weeks=4)
    elif period == "all":
        period_from = datetime.strptime("2020-01-01", '%Y-%m-%d')
    # falls back to 1 day of stats
    else:
        period_from = datetime.today() - timedelta(days=1)

    # fetch the stats data from the DB
    cur = get_db().cursor()
    cur.execute(Db_obj.db_select_stats_query_all, [period_from])
    raw_data = cur.fetchall()

    def _chart_data_preparator(input_data_set):
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

    chart_data = _chart_data_preparator(raw_data)

    return render_template('stats.html',
                           template_period=period,
                           template_pie_chart_data_source=
                           [x[0] for x in chart_data.get('pie_by_source').get('output_data_set')],
                           template_pie_chart_labels_source=
                           chart_data.get('pie_by_source').get('group_keys'),
                           template_pie_chart_data_sentiment=
                           [x[0] for x in chart_data.get('pie_by_sentiment').get('output_data_set')],
                           template_pie_chart_labels_sentiment=
                           chart_data.get('pie_by_sentiment').get('group_keys'),
                           template_time_series_data_positive=
                           [x[0] for x in chart_data.get('time_series').get('output_data_set') if x[1] == "positive"],
                           template_time_series_data_negative=
                           [x[0] for x in chart_data.get('time_series').get('output_data_set') if x[1] == "negative"],
                           template_time_series_data_uncertain=
                           [x[0] for x in chart_data.get('time_series').get('output_data_set') if x[1] == "uncertain"],
                           template_time_series_labels=
                           sorted(list(set(chart_data.get('time_series').get('group_keys'))))
                           )


if __name__ == "__main__":
    # # Local app run:
    # serve(app, host='0.0.0.0', port=80, threads=4)

    # Heroku deployed app run:
    serve(app, host='127.0.0.1', port=5000)
