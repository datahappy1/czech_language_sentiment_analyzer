"""
database interface module
"""
from flask_webapp.database import conn_local_sqlite, conn_remote_postgres


def _connect_from_environment(environment):
    """
    _connect_from_environment mapping function
    :param environment:
    :return:
    """
    try:
        _mapping = {
            "local": {
                "conn": conn_local_sqlite.Connect,
            },
            "remote": {
                "conn": conn_remote_postgres.Connect,
            }
        }
        return _mapping[environment]
    except KeyError:
        raise Exception("Invalid environment value, valid values are remote | local")


def _get_query_from_environment(environment, query_name):
    """
    _get_query from environment mapping function
    :param environment:
    :param query_name:
    :return:
    """
    try:
        _mapping = {
            "local": {
                "drop_table": QueryCommon.DB_DROP_TABLE,
                "select_count_rows_query": QueryCommon.DB_SELECT_COUNT_ROWS_QUERY,
                "create_table": QueryLocal.DB_CREATE_TABLE,
                "insert_stats_query": QueryLocal.DB_INSERT_STATS_QUERY,
                "check_table_exists": QueryLocal.DB_CHECK_TABLE_EXISTS,
                "select_stats_query_all": QueryLocal.DB_SELECT_RAW_STATS_DATA,
            },
            "remote": {
                "drop_table": QueryCommon.DB_DROP_TABLE,
                "select_count_rows_query": QueryCommon.DB_SELECT_COUNT_ROWS_QUERY,
                "create_table": QueryRemote.DB_CREATE_TABLE,
                "insert_stats_query": QueryRemote.DB_INSERT_STATS_QUERY,
                "check_table_exists": QueryRemote.DB_CHECK_TABLE_EXISTS,
                "select_stats_query_all": QueryRemote.DB_SELECT_RAW_STATS_DATA
            }
        }
        return _mapping[environment][query_name]
    except KeyError:
        raise Exception("Invalid environment value, valid values are remote | local")


class QueryRemote:
    """
    query remote class for Postgres
    """
    # create the stats table
    DB_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS stats(
    id SMALLSERIAL,
    request_datetime TIMESTAMP NOT NULL,
    sentiment_prediction VARCHAR NOT NULL); """

    # check if table exists
    DB_CHECK_TABLE_EXISTS = """
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'stats'; """

    # insert into stats query
    DB_INSERT_STATS_QUERY = """
    INSERT INTO stats("request_datetime", "sentiment_prediction") VALUES (%s, %s); """

    # select raw stats data
    DB_SELECT_RAW_STATS_DATA = """
    SELECT to_char("request_datetime", 'YYYY-MM-DD'), sentiment_prediction 
    FROM stats
    WHERE request_datetime::timestamp >= %s; """


class QueryLocal:
    """
    query remote class for Sqlite3
    """
    # create the stats table
    DB_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS stats (
    id integer PRIMARY KEY AUTOINCREMENT,
    request_datetime timestamp NOT NULL,
    sentiment_prediction string NOT NULL); """

    # check if table exists
    DB_CHECK_TABLE_EXISTS = """
    SELECT 1 FROM sqlite_master 
    WHERE type='table' AND name='stats'; """

    # insert into stats query
    DB_INSERT_STATS_QUERY = """
    INSERT INTO 'stats'('request_datetime', 'sentiment_prediction') VALUES (?, ?); """

    # select raw stats data
    DB_SELECT_RAW_STATS_DATA = """
    SELECT date(request_datetime) as 'DATE()', sentiment_prediction 
    FROM stats
    WHERE request_datetime >= ?; """


class QueryCommon:
    """
    query common class
    """
    # drop the stats table
    DB_DROP_TABLE = """
    DROP TABLE IF EXISTS stats; """

    # select count(*) query
    DB_SELECT_COUNT_ROWS_QUERY = """
    SELECT count(*) FROM stats;"""


class Database:
    """
    main database interaction class
    """

    def __init__(self, env):
        self.environment = env

        self.db_drop_table = \
            _get_query_from_environment(self.environment, query_name="drop_table")

        self.db_select_count_rows_query = \
            _get_query_from_environment(self.environment, query_name="select_count_rows_query")

        self.db_create_table = \
            _get_query_from_environment(self.environment, query_name="create_table")

        self.db_insert_stats_query = \
            _get_query_from_environment(self.environment, query_name="insert_stats_query")

        self.db_check_table_exists = \
            _get_query_from_environment(self.environment, query_name="check_table_exists")

        self.db_select_stats_query_all = \
            _get_query_from_environment(self.environment, query_name="select_stats_query_all")

    def connect(self):
        """
        connect to database method
        :return:
        """
        _mapped_conn_obj = _connect_from_environment(self.environment)["conn"]
        conn = _mapped_conn_obj()
        return conn.connect()

    def db_builder(self):
        """
        db builder method
        :return:
        """
        conn = self.connect()

        # drop and re-create table
        with conn:
            cur = conn.cursor()
            cur.execute(self.db_check_table_exists)

            table_exists_query_result = cur.fetchone()

            if table_exists_query_result and table_exists_query_result[0] == 1:
                # check the count of all rows in the stats table
                cur.execute(self.db_select_count_rows_query)
                rowcount = cur.fetchone()[0]

                if rowcount > 7000:
                    # drop stats table if > 7000 rows due to
                    # Heroku Postgres free-tier limitation
                    cur.execute(self.db_drop_table)
                    print(f"Dropped the stats table, row count: {rowcount}")

            # create stats table if not exists
            cur.execute(self.db_create_table)

        return 0
