import sqlite3
from sqlite3 import Error

DB_FILE_LOC = "stats.db"


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
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS stats (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        request_datetime timestamp NOT NULL,
                                        sentiment_prediction string NOT NULL
                                    ); """

    # create a database connection
    conn = create_connection(DB_FILE_LOC)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_projects_table)
        conn.close()
    else:
        print("Error! cannot create the database connection.")