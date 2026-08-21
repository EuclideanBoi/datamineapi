import sqlalchemy as sa
from datetime import datetime
from argon2 import PasswordHasher
from flask_login import UserMixin
import base64
import secrets

ph = PasswordHasher()

class User(UserMixin):
    def __init__(self, uid, username, role_id):
        self.uid = uid
        self.username = username
        self.role_id = role_id

class Database():
    def __init__(self, app, uri):
        self.engine = sa.create_engine(uri)
        self.logger = app.logger

        check_exists = """SELECT string_value FROM config WHERE field_name = 'db_schema_version';"""

        try:
            with self.engine.begin() as conn:
                result = conn.exec_driver_sql(check_exists)
                self.logger.info("Existing database found, schema version " + result.fetchone()[0])
        except:
            self.logger.info("Database not initialized, creating tables")
            self.create_tables()
    
    def create_tables(self):
        from backend.schema import tables, indices, init_values
        try:
            with self.engine.begin() as conn:
                for table in tables:
                    conn.exec_driver_sql(table)
                for index in indices:
                    conn.exec_driver_sql(index)
                for init_val in init_values:
                    conn.exec_driver_sql(init_val)
                conn.commit()
        except:
            raise Exception("Database table creation error")

        self.logger.info("Database tables created")
        self.logger.info("Creating admin user: " + ("Success" if self.create_web_user("admin", "password", 1, True) else "Failed"))

    def create_api_user(self, expires = False, expiration_period = 30):
        unhashed_key = base64.urlsafe_b64encode(secrets.token_bytes(36)).decode("ascii")
        # hashed_key = ph.hash(unhashed_key)
        timestamp = int(datetime.datetime.now().timestamp())
        expiration_time = timestamp + (expiration_period * 24 * 60 * 60)

        new_user = """
            INSERT INTO api_users (
                api_key,
                issued_time,
                revoked,
                expires,
                expired,
                expiration_time
            ) VALUES
            (?, ?, ?, ?, ?, ?);
        """

        #try:
        with self.engine.begin() as conn:
            result = conn.exec(new_user, (unhashed_key, timestamp, False, expires, False, expiration_time))
            conn.commit()
        self.logger.info("API user registered")
        #except:
        #    raise Exception("Registration failure!")
        
        return unhashed_key
    
    def create_web_user(self, username: str, password: str, role_id: int, enabled: bool):
        password_hash = ph.hash(password)

        check_user = """
            SELECT username FROM web_users WHERE username = ?;
        """
        
        new_user = """
            INSERT INTO web_users (
                username,
                password_hash,
                role_id,
                enabled
            ) VALUES (?, ?, ?, ?);
        """

        with self.engine.begin() as conn:
            result = conn.exec_driver_sql(check_user, (username,))
            if result.fetchone():
                return False
            conn.exec_driver_sql(new_user, (username, password_hash, role_id, enabled))
            conn.commit()
        return True

    def authenticate(self, token):

        user_query = """
            SELECT * FROM users WHERE
        """

    def login(self, username: str, password: str, ip: str):
        user_query = """
            SELECT * FROM web_users WHERE username = ?;
        """
        log_insert = """
            INSERT INTO web_events (
                uid,
                type_id,
                time,
                ip_address
            ) VALUES (?, ?, ?, ?);
        """

        try:
            with self.engine.begin() as conn:
                result = conn.exec_driver_sql(user_query, (username,))
                data = result.fetchone()
                if data[4] and ph.verify(data[2], password):
                    conn.exec_driver_sql(log_insert, (data[0], 1, int(datetime.now().timestamp() * 1000), ip))
                    conn.commit()
                    return User(data[0], data[1], data[3])

                conn.exec_driver_sql(log_insert)
                return False
        except:
            return False