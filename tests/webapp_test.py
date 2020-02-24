import pytest
from flask_webapp.app import app


def test_main_get():
    response = app.test_client().get('/')
    # print(response.data)
    assert response.status_code == 200
    assert b'<title>Czech sentiment analyzer Datahappy \xc2\xa92019</title>' in response.data
