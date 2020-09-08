"""
local sqlite db connection module
"""
import os
import sqlite3


class Connect:
    """
    connect sqlite3 class
    """
    def __init__(self):
        """ create a database connection to the SQLite database
            specified by db_file
        :return: Connection object or sqlite3 error is raised
        """

        self.db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'stats.db'))

    def __repr__(self):
        return str(self.db_file)

    def connect(self):
        """
        connect method
        :return:
        """
        try:
            conn = sqlite3.connect(self.db_file)

        except sqlite3.Error as general_err:
            raise general_err

        return conn
