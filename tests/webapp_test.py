"""
Flask app Pytest testing suite
"""
from flask_webapp.app import APP

API_PREFIX = APP.config['api_prefix']


def test_main_get():
    APP.testing = True
    response = APP.test_client().get('/')
    assert response.status_code == 200
    assert b'<title>Czech sentiment analyzer Datahappy \xc2\xa92019</title>' in response.data


def test_main_post_no_input_text():
    APP.testing = True
    response = APP.test_client().post('/')
    assert response.status_code == 200
    assert b'<div id="error_message" class="alert alert-danger" style="display:block;">' \
           b'Sorry, need to submit at least 3 non stop-words</div>' in response.data


def test_main_post_invalid_input_text_too_few_words():
    response = APP.test_client().post('/', data=dict(Input_Text='a jsi'),
                                      follow_redirects=True)

    assert response.status_code == 200
    assert b'<div id="error_message" class="alert alert-danger" style="display:block;">' \
           b'Sorry, need to submit at least 3 non stop-words</div>' in response.data


def test_main_post_invalid_input_text_too_short_words():
    response = APP.test_client().post('/', data=dict(Input_Text='a b c d'),
                                      follow_redirects=True)

    assert response.status_code == 200
    assert b'<div id="error_message" class="alert alert-danger" style="display:block;">' \
           b'Sorry, need to submit at least 1 word with 3 and more characters</div>' in response.data


def test_main_post_invalid_input_text_not_czech_language():
    response = APP.test_client().post('/', data=dict(Input_Text='ein zwei polizei'),
                                      follow_redirects=True)

    assert response.status_code == 200
    assert b'<div id="error_message" class="alert alert-danger" style="display:block;">' \
           b'Sorry, need to submit text written in Czech</div>' in response.data


def test_main_post_valid_input_text_positive():
    response = APP.test_client().post('/', data=dict(Input_Text='Skvělé funkcionální testy'),
                                      follow_redirects=True)

    assert response.status_code == 200
    assert b'overall_sentiment : <b>positive</b>' in response.data


def test_main_post_valid_input_text_negative():
    response = APP.test_client().post('/', data=dict(Input_Text='Hrozné funkcionální testy'),
                                      follow_redirects=True)

    assert response.status_code == 200
    assert b'overall_sentiment : <b>negative</b>' in response.data


def test_api_get():
    APP.testing = True
    response = APP.test_client().get(API_PREFIX)

    assert response.status_code == 405
    assert b'{"error":"405 Method Not Allowed: The method is not allowed for the requested URL.",' \
           b'"mimetype":"application/json","status":405}' in response.data


def test_api_post_no_input_text():
    APP.testing = True
    response = APP.test_client().post(API_PREFIX)
    assert response.status_code == 400
    assert b'{"error":"Sorry, need to submit at least 3 non stop-words",' \
           b'"mimetype":"application/json","status":400}' in response.data


def test_api_post_invalid_input_text_too_few_words():
    response = APP.test_client().post(API_PREFIX, data=dict(Input_Text='a jsi'),
                                      follow_redirects=True)

    assert response.status_code == 400
    assert b'{"error":"Sorry, need to submit at least 3 non stop-words",' \
           b'"mimetype":"application/json","status":400}' in response.data


def test_api_post_invalid_input_text_too_short_words():
    response = APP.test_client().post(API_PREFIX, data=dict(Input_Text='a b c d'),
                                      follow_redirects=True)

    assert response.status_code == 400
    assert b'{"error":"Sorry, need to submit at least 1 word with 3 and more characters",' \
           b'"mimetype":"application/json","status":400' in response.data


def test_api_post_invalid_input_text_not_czech_language():
    response = APP.test_client().post(API_PREFIX, data=dict(Input_Text='ein zwei polizei'),
                                      follow_redirects=True)

    assert response.status_code == 400
    assert b'{"error":"Sorry, need to submit text written in Czech",' \
           b'"mimetype":"application/json","status":400}' in response.data


def test_api_post_valid_input_text_positive():
    response = APP.test_client().post(API_PREFIX, data=dict(Input_Text='Skvělé funkcionální testy'),
                                      follow_redirects=True)

    assert response.status_code == 200
    assert b'"sentiment":"positive"' in response.data


def test_api_post_valid_input_text_negative():
    response = APP.test_client().post(API_PREFIX, data=dict(Input_Text='Hrozné funkcionální testy'),
                                      follow_redirects=True)

    assert response.status_code == 200
    assert b'"sentiment":"negative"' in response.data
