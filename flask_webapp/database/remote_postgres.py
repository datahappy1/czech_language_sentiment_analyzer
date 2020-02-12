import psycopg2
import urllib.parse as urlparse
import os
from flask_webapp.database.db_common import Query

DB_URL = urlparse.urlparse(os.environ.get('DATABASE_URL'))


def create_connection(db_url):
    dbname = db_url.path[1:]
    user = db_url.username
    password = db_url.password
    host = db_url.hostname
    port = db_url.port

    conn = None

    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except psycopg2.Error as e:
        print(e)

    return conn

def run_statement_fetchone(conn, statement):
    """

    :param conn:
    :param statement:
    :return:
    """
    output = []
    try:
        c = conn.cursor()
        c.execute(statement)
        output = c.fetchone()
    except psycopg2.Error as e:
        print(e)
    return output


def run_statement_fetchall(conn, statement):
    """

    :param conn:
    :param statement:
    :return:
    """
    output = []
    try:
        c = conn.cursor()
        c.execute(statement)
        output = c.fetchall()
    except psycopg2.Error as e:
        print(e)
    return output


def run_statement_no_return(conn, statement):
    """ run a provided statement
    :param conn: Connection object
    :param statement:
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(statement)
    except psycopg2.Error as e:
        print(e)


def db_builder():
    # create a database connection
    conn = create_connection(DB_URL)

    # drop and re-create table
    if conn is not None:
        # # check the max(id) in stats table
        # _max_id = run_statement_fetchone(conn, Query.DB_SELECT_MAX_ID_QUERY)[0]

        # if _max_id > 7000:
        #     # drop stats table
        #     run_statement_no_return(conn, Query.DB_DROP_TABLE)
        #     print(f"Dropped the stats table, max(id): {_max_id}")

        # create stats table
        run_statement_no_return(conn, Query.DB_CREATE_TABLE)

        conn.close()
    else:
        print("Error! cannot create the database connection.")