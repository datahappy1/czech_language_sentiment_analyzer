"""
__main__.py
"""
import os
from datetime import date, datetime, timedelta
from flask import Flask, render_template, send_from_directory, request, jsonify, g
from flaskext.markdown import Markdown
from flask_caching import Cache
from waitress import serve
from langdetect import detect
from flask_webapp.exceptions import NotEnoughNonStopWordsException, NotEnoughWordsLengthException, \
    InvalidDetectedLanguageException, EXCEPTION_TYPE_RESPONSE_MESSAGE_MAP
from flask_webapp.database import __env__
from flask_webapp.database.database_interface import Database
from utils.utilities import Webapp
from ml_models import webapp_interface


def create_app():
    """
    create app factory
    :return:
    """
    _app = Flask(__name__)
    return _app


APP = create_app()

# bind flask-markdown extension to the app
Markdown(APP)
# load the markdown file content for /methodology route
APP.config['md_content'] = Webapp.markdown_reader()

# api base url setup
APP.config['api_prefix'] = '/api/v1/prediction/'

# setup Cache ext.
APP.config['CACHE_TYPE'] = 'simple'
# register the cache instance and bind it to the app
APP.cache = Cache(APP)

# language detection module allowed languages
# Slovak, Slovenian, Croatian allowed because langdetect module,
# when submitting Czech text without the diacritics detects one of these
APP.config['acceptable_detected_language_codes'] = ['cs', 'sk', 'sl', 'hr']

# run the build DB script on app startup, instantiate the Db object
# if __env__ is local ( env. variable DATABASE_URL not set ) -> Sqlite3
# if __env__ is remote ( env. variable DATABASE_URL configured for Heroku Postgres) -> Postgres
DB_OBJ = Database(__env__)
DB_OBJ.db_builder()


def get_db():
    """
    get db connection function
    :return:
    """
    database = getattr(g, '_database', None)
    if database is None:
        database = g._database = Database.connect(DB_OBJ)
    return database


def write_stats_to_table(sentiment_result):
    """
    function storing stats data in a table
    :param sentiment_result:
    :return: status
    """
    cur = get_db().cursor()
    data_tuple = (datetime.now(), sentiment_result)
    cur.execute(DB_OBJ.db_insert_stats_query, data_tuple)
    get_db().commit()


def process_input_text(input_text):
    """
    process input text function
    :param input_text:
    :return:
    """

    def _validate_input_text(_input_text):
        if not _input_text:
            raise NotEnoughNonStopWordsException

    def _validate_detected_language(detected_language):
        if detected_language not in APP.config['acceptable_detected_language_codes']:
            raise InvalidDetectedLanguageException

    def _create_input_text_lowered_list(_input_text):
        return Webapp.input_string_preparator(_input_text.lower())

    def _is_invalid_non_stop_word_count(_input_text_lowered_list):
        if len([i for i in _input_text_lowered_list if i != '']) < 3:
            raise NotEnoughNonStopWordsException

    def _is_invalid_word_length_count(_input_text_lowered_list):
        if all([len(i) < 3 for i in _input_text_lowered_list]):
            raise NotEnoughWordsLengthException

    def _get_sentiment_result(_input_text_lowered_list):
        return webapp_interface.ml_model_evaluator([' '.join(_input_text_lowered_list)])

    _validate_input_text(input_text)
    input_text_lowered_list = _create_input_text_lowered_list(input_text)
    _is_invalid_non_stop_word_count(input_text_lowered_list)
    _is_invalid_word_length_count(input_text_lowered_list)
    _validate_detected_language(detect(input_text))
    return _get_sentiment_result(input_text_lowered_list)


def post_request_exception_handler(handler_type, input_text, exception_type):
    """
    post request exception handler
    :param handler_type:
    :param input_text:
    :param exception_type:
    :return:
    """
    if handler_type == "main":
        return render_template('index.html',
                               template_input_string=input_text,
                               template_error_message=
                               EXCEPTION_TYPE_RESPONSE_MESSAGE_MAP[exception_type])
    if handler_type == "api":
        response = jsonify({
            'status': 400,
            'error': EXCEPTION_TYPE_RESPONSE_MESSAGE_MAP[exception_type],
            'mimetype': 'application/json'
        })
        response.status_code = 400
        return response


def post_request_success_handler(handler_type, input_text, sentiment_result):
    """
    post request success handler
    :param handler_type:
    :param input_text:
    :param sentiment_result:
    :return:
    """
    if handler_type == "main":
        return render_template('index.html',
                               template_input_string=input_text,
                               template_sentiment_result=sentiment_result)
    if handler_type == "api":
        response = jsonify({
            'status': 200,
            'sentiment_result': sentiment_result,
            'mimetype': 'application/json'
        })
        response.status_code = 200
        return response


def post_request_sentiment_analyzer_handler(handler_type, input_text):
    """
    sentiment analyzer handler
    :param handler_type:
    :param input_text:
    :return:
    """
    try:
        sentiment_result = process_input_text(input_text)

    except NotEnoughNonStopWordsException:
        return post_request_exception_handler(
            handler_type, input_text, "NotEnoughNonStopWordsException"
        )

    except NotEnoughWordsLengthException:
        return post_request_exception_handler(
            handler_type, input_text, "NotEnoughWordsLengthException"
        )

    except InvalidDetectedLanguageException:
        return post_request_exception_handler(
            handler_type, input_text, "InvalidDetectedLanguageException"
        )

    except Exception:
        return post_request_exception_handler(handler_type, input_text, "GenericException")

    write_stats_to_table(
        sentiment_result=sentiment_result.get('overall_sentiment').get('sentiment')
    )

    return post_request_success_handler(handler_type, input_text, sentiment_result)


@APP.teardown_appcontext
def close_connection(exception):
    """
    close database connection function
    :return:
    """
    database = getattr(g, '_database', None)
    if database is not None:
        database.close()


@APP.route('/favicon.ico')
def favicon():
    """
    function to properly handle favicon
    :return:
    """
    return send_from_directory(os.path.join(APP.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@APP.errorhandler(400)
def bad_request(error):
    """
    bad request error handler function
    :param error:
    :return:error html page or api response
    """
    if request.path.startswith(APP.config["api_prefix"]):
        response = jsonify({
            'status': 400,
            'error': str(error),
            'mimetype': 'application/json'
        })
        response.status_code = 400
        return response
    return render_template('error_page.html', template_error_message=error)


@APP.errorhandler(405)
def not_allowed(error):
    """
    not allowed method error handler function
    :param error:
    :return:error html page or api response
    """
    if request.path.startswith(APP.config["api_prefix"]):
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
    if request.path.startswith(APP.config["api_prefix"]):
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

    if request.method == 'POST':
        return post_request_sentiment_analyzer_handler(
            handler_type='main', input_text=request.form.get('Input_Text')
        )


@APP.route(APP.config["api_prefix"], methods=['POST'])
def api():
    """
    CURL POST example:
    curl -X POST -F Input_Text="your text for analysis" http://127.0.0.1:5000/api/v1/prediction/
    :return:
    """
    if request.method == 'POST':
        return post_request_sentiment_analyzer_handler(
            handler_type='api', input_text=request.form.get('Input_Text')
        )


@APP.route('/api_docs', methods=['GET'])
def api_docs():
    """
    the route rendering API documentation
    :return:
    """
    return render_template('api_docs.html')


@APP.route('/methodology', methods=['GET'])
def methodology():
    """
    the route rendering methodology documentation
    from the repo README.md markdown
    :return:
    """
    return render_template('methodology.html', text=APP.config['md_content'])


@APP.route('/stats/<string:period>/', methods=['GET'])
@APP.cache.cached(timeout=60)  # cache this view for 1 minute
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
    # falls back to last 24 hours of stats
    else:
        period_from = date.today() - timedelta(days=1)

    # fetch the stats data from the DB
    cur = get_db().cursor()
    cur.execute(DB_OBJ.db_select_stats_query_all, [period_from])
    raw_data = cur.fetchall()

    chart_data = Webapp.chart_data_preparator(raw_data)

    return render_template('stats.html',
                           template_period=period,

                           template_pie_chart_data_sentiment=
                           [x[0] for x in
                            chart_data.get('pie_by_sentiment').get('output_data_set')],

                           template_pie_chart_labels_sentiment=
                           chart_data.get('pie_by_sentiment').get('group_keys'),

                           template_time_series_data_positive=
                           [x[0] for x in
                            chart_data.get('time_series').get('output_data_set')
                            if x[2] == "positive"],

                           template_time_series_data_negative=
                           [x[0] for x in
                            chart_data.get('time_series').get('output_data_set')
                            if x[2] == "negative"],

                           template_time_series_data_uncertain=
                           [x[0] for x in
                            chart_data.get('time_series').get('output_data_set')
                            if x[2] == "uncertain"],

                           template_time_series_labels
                           =chart_data.get('time_series').get('group_keys')
                           )


if __name__ == "__main__":
    serve(APP, host='127.0.0.1', port=5000)
