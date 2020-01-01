"""
__main__.py
"""
import os
from flask import Flask, render_template, send_from_directory
from waitress import serve

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


@APP.route('/', methods=['GET'])
def main():
    """
    the main route rendering index.html
    :return:
    """
    return render_template('index.html')


@APP.route('/API', methods=['GET'])
def api():
    """
    the route rendering API documentation
    :return:
    """
    return render_template('api.html')


if __name__ == "__main__":
    serve(APP, host='0.0.0.0', port=80, threads=THREADS_COUNT)
