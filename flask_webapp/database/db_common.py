class Query:
    # drop the stats table
    DB_DROP_TABLE = """
    DROP TABLE IF EXISTS stats; """

    # create the stats table
    DB_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS stats (
    id integer PRIMARY KEY AUTOINCREMENT,
    request_datetime timestamp NOT NULL,
    sentiment_prediction string NOT NULL); """

    # get max(id) query
    DB_SELECT_MAX_ID_QUERY = """
    SELECT max(id) as max_id FROM stats;"""

    # insert into stats query
    DB_INSERT_STATS_QUERY = """
    INSERT INTO 'stats'('request_datetime', 'sentiment_prediction') VALUES (?, ?);"""

    # get the stats queries
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