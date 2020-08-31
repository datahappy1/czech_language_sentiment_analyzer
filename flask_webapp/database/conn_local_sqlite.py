"""
local sqlite db connection module
"""
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or sqlite3 error is raised
    """

    try:
        conn = sqlite3.connect(db_file)

    except Error as general_err:
        raise general_err

    return conn
