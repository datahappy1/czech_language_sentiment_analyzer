"""
remote postgres db connection module
"""
import os

import urllib.parse as urlparse
import psycopg2


class Connect:
    """
    connect Postgres class
    """
    def __init__(self):
        """ create a database connection to the Postgres database
            specified by db_url
        :return: Connection object or psycopg2 error is raised
        """

        self.db_url = os.environ.get('DATABASE_URL')

    def __repr__(self):
        return str(self.db_url)

    def connect(self):
        """
        connect method
        :return:
        """
        db_url_parsed = urlparse.urlparse(self.db_url)

        db_name = db_url_parsed.path[1:]
        user = db_url_parsed.username
        password = db_url_parsed.password
        host = db_url_parsed.hostname
        port = db_url_parsed.port

        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port,
                sslmode='require'
            )

        except psycopg2.Error as psycopg2_err:
            raise psycopg2_err

        return conn
