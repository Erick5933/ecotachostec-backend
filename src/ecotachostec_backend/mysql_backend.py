"""
Backend de Django para MySQL que funciona con PyMySQL
"""
from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper

class DatabaseWrapper(MySQLDatabaseWrapper):
    pass
