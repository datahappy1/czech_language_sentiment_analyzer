import os
import urllib.parse as urlparse
from flask_webapp.database import local_sqlite, remote_postgres


class QueryCommon:
    # drop the stats table
    DB_DROP_TABLE = """
    DROP TABLE IF EXISTS stats; """

    # get max(id) query
    DB_SELECT_MAX_ID_QUERY = """
    SELECT max(id) as max_id FROM stats;"""


class QueryRemote:
    # create the stats table
    DB_CREATE_TABLE_POSTGRES = """
    CREATE TABLE IF NOT EXISTS stats(
    id SMALLSERIAL,
    request_datetime TIMESTAMP NOT NULL,
    sentiment_prediction VARCHAR NOT NULL); """

    # check if table exists
    DB_CHECK_TABLE_EXISTS_POSTGRES = """
    SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'czester'
    AND table_name = 'stats'); """

    # insert into stats query
    DB_INSERT_STATS_QUERY_POSTGRES = """
    INSERT INTO stats ("request_datetime", "sentiment_prediction") VALUES (%s, %s);"""

    DB_SELECT_STATS_QUERY_PIE_CHART_POSTGRES = """
    SELECT sum(i.cnt) as cnt, sentiment_prediction
    FROM 
      (SELECT 1 as cnt, sentiment_prediction 
       FROM stats 
       WHERE request_datetime::timestamp >= %s
       UNION ALL SELECT 0 as cnt, 'negative' as sentiment_prediction
       UNION ALL SELECT 0 as cnt, 'positive' as sentiment_prediction) i
    GROUP BY sentiment_prediction
    ORDER BY sentiment_prediction ;"""

    DB_SELECT_STATS_QUERY_TIME_SERIES_POSTGRES = """
    SELECT count(*) as cnt, sentiment_prediction, request_datetime::timestamp::date
    FROM stats 
    WHERE request_datetime::timestamp >= %s
    GROUP BY sentiment_prediction, request_datetime::timestamp::date
    ORDER BY request_datetime::timestamp::date ;"""


class QueryLocal:
    # create the stats table
    DB_CREATE_TABLE_SQLITE = """
    CREATE TABLE IF NOT EXISTS stats (
    id integer PRIMARY KEY AUTOINCREMENT,
    request_datetime timestamp NOT NULL,
    sentiment_prediction string NOT NULL); """

    # check if table exists
    DB_CHECK_TABLE_EXISTS_SQLITE = """
    SELECT 1 FROM sqlite_master 
    WHERE type='table' AND name='{stats}'; """

    # insert into stats query
    DB_INSERT_STATS_QUERY_SQLITE = """
    INSERT INTO 'stats'('request_datetime', 'sentiment_prediction') VALUES (?, ?);"""

    # get the stats queries
    DB_SELECT_STATS_QUERY_PIE_CHART_SQLITE = """
    SELECT sum(i.cnt) as cnt, sentiment_prediction
    FROM 
      (SELECT 1 as cnt, sentiment_prediction 
       FROM stats 
       WHERE request_datetime >= ? 
       UNION ALL SELECT 0 as cnt, 'negative' as sentiment_prediction
       UNION ALL SELECT 0 as cnt, 'positive' as sentiment_prediction) i
    GROUP BY sentiment_prediction
    ORDER BY sentiment_prediction ;"""

    DB_SELECT_STATS_QUERY_TIME_SERIES_SQLITE = """
    SELECT count(*) as cnt, sentiment_prediction, date(request_datetime) as 'DATE()' 
    FROM stats 
    WHERE request_datetime >= ?
    GROUP BY sentiment_prediction, date(request_datetime) 
    ORDER BY date(request_datetime) ;"""


class Database:
    def __init__(self, env):
        self.environment = env
        self.db_drop_table = QueryCommon.DB_DROP_TABLE
        self.db_select_max_id_query = QueryCommon.DB_SELECT_MAX_ID_QUERY
        self.conn = None

        if self.environment == "remote":
            self.db_create_table = QueryRemote.DB_CREATE_TABLE_POSTGRES
            self.db_insert_stats_query = QueryRemote.DB_INSERT_STATS_QUERY_POSTGRES
            self.db_check_table_exists = QueryRemote.DB_CHECK_TABLE_EXISTS_POSTGRES
            self.db_select_stats_query_pie_chart = QueryRemote.DB_SELECT_STATS_QUERY_PIE_CHART_POSTGRES
            self.db_select_stats_query_time_series = QueryRemote.DB_SELECT_STATS_QUERY_TIME_SERIES_POSTGRES
        elif self.environment == "local":
            self.db_create_table = QueryLocal.DB_CREATE_TABLE_SQLITE
            self.db_insert_stats_query = QueryLocal.DB_INSERT_STATS_QUERY_SQLITE
            self.db_check_table_exists = QueryLocal.DB_CHECK_TABLE_EXISTS_SQLITE
            self.db_select_stats_query_pie_chart = QueryLocal.DB_SELECT_STATS_QUERY_PIE_CHART_SQLITE
            self.db_select_stats_query_time_series = QueryLocal.DB_SELECT_STATS_QUERY_TIME_SERIES_SQLITE
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

    def close(self):
        self.conn.close()

    def run_statement_no_return(self, statement):
        if self.environment == "remote":
            run_statement_no_return = remote_postgres.run_statement_no_return(conn=self.conn,
                                                                              statement=statement)
        elif self.environment == "local":
            run_statement_no_return = local_sqlite.run_statement_no_return(conn=self.conn,
                                                                           statement=statement)
        else:
            raise NotImplementedError

        return run_statement_no_return

    def run_statement_fetchall(self, statement, arguments):
        if self.environment == "remote":
            run_statement_fetchall = remote_postgres.run_statement_fetchall(conn=self.conn,
                                                                            statement=statement,
                                                                            arguments=arguments)
        elif self.environment == "local":
            run_statement_fetchall = local_sqlite.run_statement_fetchall(conn=self.conn,
                                                                         statement=statement,
                                                                         arguments=arguments)
        else:
            raise NotImplementedError

        return run_statement_fetchall

    def db_builder(self):
        # make the db_builder one execute script, remove connect,close,run_statement_fetchall methods TODO

        # connect
        self.connect()

        # drop and re-create table
        _table_exists = False
        if self.conn:
            _table_exists = self.run_statement_fetchall(self.db_check_table_exists,arguments=None)

        if _table_exists is True:
            # check the max(id) in stats table
            _max_id = self.run_statement_fetchall(self.db_select_max_id_query,arguments=None)[0]

            if _max_id > 7000:
                # drop stats table
                self.run_statement_no_return(self.db_drop_table)
                print(f"Dropped the stats table, max(id): {_max_id}")

        # create stats table
        self.run_statement_no_return(self.db_create_table)

        # close the db connection
        self.close()

        return 0
