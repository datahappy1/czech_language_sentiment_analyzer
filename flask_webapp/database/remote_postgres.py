import psycopg2


def create_connection(db_url):
    """ create a database connection to the Postgres database
        specified by db_url
    :param db_url: database url
    :return: Connection object or None
    """
    db_name = db_url.path[1:]
    user = db_url.username
    password = db_url.password
    host = db_url.hostname
    port = db_url.port
    conn = None

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port,
            sslmode='require'
        )

    except psycopg2.Error as e:
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
        conn.commit()

    except psycopg2.Error as e:
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

    except psycopg2.Error as e:
        print(e)

    return output
