import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        return conn

    except Error as e:
        print(e)

    return conn


def run_statement_no_return(conn, statement):
    """ run a provided statement
    :param conn: Connection object
    :param statement:
    :return:0
    """
    try:
        c = conn.cursor()
        c.execute(statement)

    except Error as e:
        print(e)

    return 0


def run_statement_fetchall(conn, statement, arguments):
    """ run a provided statement
    :param conn:
    :param statement:
    :return: fetched rows list
    """
    output = []

    try:
        c = conn.cursor()
        c.execute(statement, [arguments])
        output = c.fetchall()

    except Error as e:
        print(e)

    return output
