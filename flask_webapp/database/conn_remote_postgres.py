"""
remote postgres db connection module
"""
import psycopg2


def create_connection(db_url):
    """ create a database connection to the Postgres database
        specified by db_url
    :param db_url: database url
    :return: Connection object or psycopg2 error is raised
    """
    db_name = db_url.path[1:]
    user = db_url.username
    password = db_url.password
    host = db_url.hostname
    port = db_url.port

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
