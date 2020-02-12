import sqlite3
from sqlite3 import Error
from flask_webapp.database.db_common import Query

DB_FILE_LOC = "flask_webapp/database/stats.db"


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


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def db_builder():
    # create a database connection
    conn = create_connection(DB_FILE_LOC)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, Query.DB_CREATE_TABLE)
        conn.close()
    else:
        print("Error! cannot create the database connection.")