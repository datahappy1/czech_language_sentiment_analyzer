import sqlite3
from sqlite3 import Error

DB_FILE_LOC = "stats.db"


class Query:
    # create the stats table
    DB_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS stats (
    id integer PRIMARY KEY AUTOINCREMENT,
    request_datetime timestamp NOT NULL,
    sentiment_prediction string NOT NULL); """

    # insert into stats query
    DB_INSERT_STATS_QUERY = """
    INSERT INTO 'stats'('request_datetime', 'sentiment_prediction') VALUES (?, ?);"""

    # read the stats queries
    DB_SELECT_STATS_QUERY_PIE_CHART = """
    SELECT sum(i.cnt) as cnt, sentiment_prediction
    FROM 
      (SELECT 1 as cnt, sentiment_prediction 
       FROM stats 
       WHERE request_datetime >= ? 
       UNION ALL SELECT 0 as cnt, 'negative' as sentiment_prediction
       UNION ALL SELECT 0 as cnt, 'positive' as sentiment_prediction) i
    GROUP BY sentiment_prediction
    ORDER BY sentiment_prediction ;
    """

    DB_SELECT_STATS_QUERY_TIME_SERIES = """
    SELECT count(*) as cnt, sentiment_prediction, date(request_datetime) as 'DATE()' 
    FROM stats 
    WHERE request_datetime >= ?
    GROUP BY sentiment_prediction, date(request_datetime) 
    ORDER BY date(request_datetime) ;"""


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