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
    INSERT INTO stats ("request_datetime", "source", "sentiment_prediction") VALUES (%s, %s, %s);"""

    DB_SELECT_STATS_QUERY_PIE_CHART_SOURCE = """
    SELECT sum(i.cnt) as cnt, source
    FROM 
      (SELECT 1 as cnt, source 
       FROM stats 
       WHERE request_datetime::timestamp >= %s
       UNION ALL SELECT 0 as cnt, 'api' as source
       UNION ALL SELECT 0 as cnt, 'website' as source) i
    GROUP BY source
    ORDER BY source ;"""


    DB_SELECT_STATS_QUERY_PIE_CHART_SENTIMENT = """
    SELECT sum(i.cnt) as cnt, sentiment_prediction
    FROM 
      (SELECT 1 as cnt, sentiment_prediction 
       FROM stats 
       WHERE request_datetime::timestamp >= %s
       UNION ALL SELECT 0 as cnt, 'negative' as sentiment_prediction
       UNION ALL SELECT 0 as cnt, 'positive' as sentiment_prediction) i
    GROUP BY sentiment_prediction
    ORDER BY sentiment_prediction ;"""

    DB_SELECT_STATS_QUERY_TIME_SERIES = """
    SELECT count(*) as cnt, sentiment_prediction, to_char("request_datetime", 'YYYY-MM-DD')
    FROM stats 
    WHERE request_datetime::timestamp >= %s
    GROUP BY sentiment_prediction, to_char("request_datetime", 'YYYY-MM-DD')
    ORDER BY to_char("request_datetime", 'YYYY-MM-DD') ;"""


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
    INSERT INTO 'stats'('request_datetime', 'source', 'sentiment_prediction') VALUES (?, ?, ?);"""

    # get the stats queries
    DB_SELECT_STATS_QUERY_PIE_CHART_SOURCE = """
    SELECT sum(i.cnt) as cnt, source
    FROM 
      (SELECT 1 as cnt, source 
       FROM stats 
       WHERE request_datetime >= ? 
       UNION ALL SELECT 0 as cnt, 'api' as source
       UNION ALL SELECT 0 as cnt, 'website' as source) i
    GROUP BY source
    ORDER BY source ;"""

    DB_SELECT_STATS_QUERY_PIE_CHART_SENTIMENT = """
    SELECT sum(i.cnt) as cnt, sentiment_prediction
    FROM 
      (SELECT 1 as cnt, sentiment_prediction 
       FROM stats 
       WHERE request_datetime >= ? 
       UNION ALL SELECT 0 as cnt, 'negative' as sentiment_prediction
       UNION ALL SELECT 0 as cnt, 'positive' as sentiment_prediction) i
    GROUP BY sentiment_prediction
    ORDER BY sentiment_prediction ;"""

    DB_SELECT_STATS_QUERY_TIME_SERIES = """
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
            self.db_create_table = QueryRemote.DB_CREATE_TABLE
            self.db_insert_stats_query = QueryRemote.DB_INSERT_STATS_QUERY
            self.db_check_table_exists = QueryRemote.DB_CHECK_TABLE_EXISTS
            self.db_select_stats_query_pie_chart_source = QueryRemote.DB_SELECT_STATS_QUERY_PIE_CHART_SOURCE
            self.db_select_stats_query_pie_chart_sentiment = QueryRemote.DB_SELECT_STATS_QUERY_PIE_CHART_SENTIMENT
            self.db_select_stats_query_time_series = QueryRemote.DB_SELECT_STATS_QUERY_TIME_SERIES

        elif self.environment == "local":
            self.db_create_table = QueryLocal.DB_CREATE_TABLE
            self.db_insert_stats_query = QueryLocal.DB_INSERT_STATS_QUERY
            self.db_check_table_exists = QueryLocal.DB_CHECK_TABLE_EXISTS
            self.db_select_stats_query_pie_chart_source = QueryLocal.DB_SELECT_STATS_QUERY_PIE_CHART_SOURCE
            self.db_select_stats_query_pie_chart_sentiment = QueryLocal.DB_SELECT_STATS_QUERY_PIE_CHART_SENTIMENT
            self.db_select_stats_query_time_series = QueryLocal.DB_SELECT_STATS_QUERY_TIME_SERIES

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
                # check the max(id) in stats table
                cur.execute(self.db_select_max_id_query)
                _max_id = cur.fetchone()[0]

                if _max_id > 7000:
                    # drop stats table if > 7000 ids due to
                    # Heroku Postgres free-tier limitation
                    cur.execute(self.db_drop_table)
                    print(f"Dropped the stats table, max(id): {_max_id}")

            # create stats table if not exists
            cur.execute(self.db_create_table)

        return 0
