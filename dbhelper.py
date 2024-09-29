import sqlite3


class DBHelper:
    def __init__(self, dbname="users.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS users (user_id integer PRIMARY KEY, address text, private_key text)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_user(self, user_id, address, private_key):
        stmt = "INSERT INTO users (user_id, address, private_key) VALUES (?, ?, ?)"
        args = (user_id, address, private_key)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_users(self):
        stmt = "SELECT user_id, address, private_key FROM users"
        return self.conn.execute(stmt).fetchall()

    def contains_user(self, user_id):
        stmt = "SELECT 1 FROM users WHERE user_id = ? LIMIT 1"
        args = (user_id,)
        result = self.conn.execute(stmt, args).fetchone()
        return result is not None

    def get_address_by_user_id(self, user_id):
        stmt = "SELECT address FROM users WHERE user_id = ?"
        args = (user_id,)
        result = self.conn.execute(stmt, args).fetchone()
        return result[0] if result else None

    def get_private_key_by_user_id(self, user_id):
        stmt = "SELECT private_key FROM users WHERE user_id = ?"
        args = (user_id,)
        result = self.conn.execute(stmt, args).fetchone()
        return result[0] if result else None
