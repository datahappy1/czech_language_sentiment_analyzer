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
from flask_webapp.database import __env__
from flask_webapp.database.database_interface import Database
from utils.utilities import Webapp
from ml_models import webapp_interface


# setup the application factory
def create_app():
    app = Flask(__name__)
    return app


app = create_app()


# bind flask-markdown extension to the app
Markdown(app)
# load the markdown file content for /methodology route
app.config['md_content'] = Webapp.markdown_reader()

# api base url setup
app.config['api_prefix'] = '/api/v1/prediction/'

# setup Cache ext.
app.config['CACHE_TYPE'] = 'simple'
# register the cache instance and bind it to the app
app.cache = Cache(app)

# language detection module allowed languages
# Slovak, Slovenian, Croatian allowed because langdetect module,
# when submitting Czech text without the diacritics detects one of these
app.config['acceptable_detected_language_codes'] = ['cs', 'sk', 'sl', 'hr']

# run the build DB script on app startup, instantiate the Db object
# if __env__ is local ( env. variable DATABASE_URL not set ) -> Sqlite3
# if __env__ is remote ( env. variable DATABASE_URL configured for Heroku Postgres) -> Postgres
Db_obj = Database(__env__)
Database.db_builder(Db_obj)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = Database.connect(Db_obj)
    return db


def _stats_to_table_writer(sentiment_result):
    """
    function storing stats data in a table
    :param sentiment_result:
    :return: status
    """
    try:
        cur = get_db().cursor()
        data_tuple = (datetime.now(), sentiment_result)
        cur.execute(Db_obj.db_insert_stats_query, data_tuple)
        get_db().commit()
        status = 'Stats data stored OK'
    except Exception as exc:
        status = 'Could not store the stats, {}'.format(exc)

    return status


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/favicon.ico')
def favicon():
    """
    function to properly handle favicon
    :return:
    """
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(400)
def bad_request(error):
    """
    bad request error handler function
    :param error:
    :return:error html page or api response
    """
    if request.path.startswith(app.config["api_prefix"]):
        response = jsonify({
            'status': 400,
            'error': str(error),
            'mimetype': 'application/json'
        })
        response.status_code = 400
        return response
    return render_template('error_page.html', template_error_message=error)


@app.errorhandler(405)
def not_allowed(error):
    """
    not allowed method error handler function
    :param error:
    :return:error html page or api response
    """
    if request.path.startswith(app.config["api_prefix"]):
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
    if request.path.startswith(app.config["api_prefix"]):
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
        input_text = request.form.get('Input_Text').lower()
        input_text_list = Webapp.input_string_preparator(input_text)

        if len(input_text_list) < 3:
            return render_template('index.html',
                                   template_input_string=input_text,
                                   template_error_message="Sorry, need to submit at least 3 non stop-words")

        if all([len(i) < 3 for i in input_text_list]):
            return render_template('index.html',
                                   template_input_string=input_text,
                                   template_error_message="Sorry, need to submit at least 1 word with 3 and more "
                                                          "characters")

        detected_lang = detect(input_text)
        if detected_lang not in app.config['acceptable_detected_language_codes']:
            return render_template('index.html',
                                   template_input_string=input_text,
                                   template_error_message="Sorry, need to submit text written in Czech")
        else:
            input_text_for_eval = ' '.join(input_text_list)
            sentiment_result = webapp_interface.ml_model_evaluator([input_text_for_eval])

            _stats_to_table_writer(sentiment_result=sentiment_result.get('overall_sentiment').get('sentiment'))

            return render_template('index.html',
                                   template_input_string=input_text_for_eval,
                                   template_sentiment_result=sentiment_result)


@app.route(app.config["api_prefix"], methods=['POST'])
def api():
    """
    CURL POST example:
    curl -X POST -F Input_Text="your text for analysis" http://127.0.0.1:5000/api/v1/prediction/
    :return:
    """
    if request.method == 'POST':
        input_text = request.form.get('Input_Text').lower()
        input_text_list = Webapp.input_string_preparator(input_text)

        if len(input_text_list) < 3:
            response = jsonify({
                'status': 400,
                'error': 'Sorry, need to submit at least 3 non stop-words',
                'mimetype': 'application/json'
            })
            response.status_code = 400
            return response

        if all([len(i) < 3 for i in input_text_list]):
            response = jsonify({
                'status': 400,
                'error': 'Sorry, need to submit at least 1 word with 3 and more characters',
                'mimetype': 'application/json'
            })
            response.status_code = 400
            return response

        detected_lang = detect(input_text)
        if detected_lang not in app.config['acceptable_detected_language_codes']:
            response = jsonify({
                'status': 400,
                'error': 'Sorry, need to submit text written in Czech',
                'mimetype': 'application/json'
            })
            response.status_code = 400
            return response

        else:
            input_text_list_for_eval = ' '.join(input_text_list)
            sentiment_result = webapp_interface.ml_model_evaluator([input_text_list_for_eval])

            _stats_to_table_writer(sentiment_result=sentiment_result.get('overall_sentiment').get('sentiment'))

            response = jsonify({
                'status': 200,
                'sentiment_result': sentiment_result,
                'mimetype': 'application/json'
            })
            response.status_code = 200
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
    # falls back to last 24 hours of stats
    else:
        period_from = date.today() - timedelta(days=1)

    # fetch the stats data from the DB
    cur = get_db().cursor()
    cur.execute(Db_obj.db_select_stats_query_all, [period_from])
    raw_data = cur.fetchall()

    chart_data = Webapp.chart_data_preparator(raw_data)

    return render_template('stats.html',
                           template_period=period,
                           template_pie_chart_data_sentiment=
                           [x[0] for x in chart_data.get('pie_by_sentiment').get('output_data_set')],
                           template_pie_chart_labels_sentiment=
                           chart_data.get('pie_by_sentiment').get('group_keys'),
                           template_time_series_data_positive=
                           [x[0] for x in chart_data.get('time_series').get('output_data_set') if x[2] == "positive"],
                           template_time_series_data_negative=
                           [x[0] for x in chart_data.get('time_series').get('output_data_set') if x[2] == "negative"],
                           template_time_series_data_uncertain=
                           [x[0] for x in chart_data.get('time_series').get('output_data_set') if x[2] == "uncertain"],
                           template_time_series_labels=chart_data.get('time_series').get('group_keys')
                           )


if __name__ == "__main__":
    serve(app, host='127.0.0.1', port=5000)
