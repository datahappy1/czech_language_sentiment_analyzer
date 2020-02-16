import os
import urllib.parse as urlparse
from flask_webapp.database import local_sqlite, remote_postgres


class QueryCommon:
    # drop the stats table
    DB_DROP_TABLE = """
    DROP TABLE IF EXISTS stats; """

    # select count(*) query
    DB_SELECT_COUNT_ROWS_QUERY = """
    SELECT count(*) FROM stats;"""


class QueryRemote:
    # create the stats table
    DB_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS stats(
    id SMALLSERIAL,
    request_datetime TIMESTAMP NOT NULL,
    source VARCHAR NOT NULL,
    sentiment_prediction VARCHAR NOT NULL); """

    # check if table exists
    DB_CHECK_TABLE_EXISTS = """
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'czester'
    AND table_name = 'stats'; """

    # insert into stats query
    DB_INSERT_STATS_QUERY = """
    INSERT INTO stats ("request_datetime", "source", "sentiment_prediction") VALUES (%s, %s, %s); """

    # select raw stats data
    DB_SELECT_RAW_STATS_DATA = """
    SELECT to_char("request_datetime", 'YYYY-MM-DD'), source, sentiment_prediction 
    FROM stats
    WHERE request_datetime::timestamp >= %s; """


class QueryLocal:
    # create the stats table
    DB_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS stats (
    id integer PRIMARY KEY AUTOINCREMENT,
    request_datetime timestamp NOT NULL,
    source string NOT NULL,
    sentiment_prediction string NOT NULL); """

    # check if table exists
    DB_CHECK_TABLE_EXISTS = """
    SELECT 1 FROM sqlite_master 
    WHERE type='table' AND name='stats'; """

    # insert into stats query
    DB_INSERT_STATS_QUERY = """
    INSERT INTO 'stats'('request_datetime', 'source', 'sentiment_prediction') VALUES (?, ?, ?); """

    # select raw stats data
    DB_SELECT_RAW_STATS_DATA = """
    SELECT date(request_datetime) as 'DATE()', source, sentiment_prediction 
    FROM stats
    WHERE request_datetime >= ?; """


class Database:
    def __init__(self, env):
        self.environment = env
        self.db_drop_table = QueryCommon.DB_DROP_TABLE
        self.db_select_count_rows_query = QueryCommon.DB_SELECT_COUNT_ROWS_QUERY
        self.conn = None

        if self.environment == "remote":
            self.db_create_table = QueryRemote.DB_CREATE_TABLE
            self.db_insert_stats_query = QueryRemote.DB_INSERT_STATS_QUERY
            self.db_check_table_exists = QueryRemote.DB_CHECK_TABLE_EXISTS
            self.db_select_stats_query_all = QueryRemote.DB_SELECT_RAW_STATS_DATA

        elif self.environment == "local":
            self.db_create_table = QueryLocal.DB_CREATE_TABLE
            self.db_insert_stats_query = QueryLocal.DB_INSERT_STATS_QUERY
            self.db_check_table_exists = QueryLocal.DB_CHECK_TABLE_EXISTS
            self.db_select_stats_query_all = QueryLocal.DB_SELECT_RAW_STATS_DATA

        else:
            raise NotImplementedError

    def connect(self):
        if self.environment == "remote":
            db_url = os.environ.get('DATABASE_URL')
            db_url_parsed = urlparse.urlparse(db_url)
            self.conn = remote_postgres.create_connection(db_url_parsed)

        elif self.environment == "local":
            db_file_loc = "flask_webapp/database/stats.db"
            self.conn = local_sqlite.create_connection(db_file_loc)

        else:
            raise NotImplementedError

        return self.conn

    def db_builder(self):
        # connect
        self.connect()

        # drop and re-create table
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(self.db_check_table_exists)
            _table_exists = cur.fetchone()

            if _table_exists:
                # check the count of all wors in the stats table
                cur.execute(self.db_select_count_rows_query)
                _rowcount = cur.fetchone()[0]

                if _rowcount > 1:
                    # drop stats table if > 7000 rows due to
                    # Heroku Postgres free-tier limitation
                    cur.execute(self.db_drop_table)
                    print(f"Dropped the stats table, row count: {_rowcount}")

            # create stats table if not exists
            cur.execute(self.db_create_table)

        return 0
