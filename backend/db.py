import sqlalchemy as sa
import backend.schema as schema
from datetime import datetime
from argon2 import PasswordHasher
import base64
import secrets

ph = PasswordHasher()

def check_password(hash, token):
    try:
        if ph.verify(hash, token):
            return True
        return False
    except:
        return False

class Session():
    def __init__(self, uid, username, session_token, role_id):
        self.uid = uid
        self.username = username
        self.session_token = session_token
        self.role_id = role_id

class Database():
    def __init__(self, app, uri, is_postgres):
        self.engine = sa.create_engine(uri)
        self.logger = app.logger
        self.sessions = {}
        if is_postgres:
            self.autoincrement = " GENERATED ALWAYS AS IDENTITY"
            self.wildcard = "%s"
        else:
            self.autoincrement = ""
            self.wildcard = "?"

        try:
            with self.engine.begin() as conn:
                result = conn.exec_driver_sql(schema.check_exists)
                self.logger.info("Existing database found, schema version " + result.fetchone()[0])
        except:
            self.logger.info("Database not initialized, creating tables")
            self.create_tables()
    
    def create_tables(self):
        try:
            with self.engine.begin() as conn:
                for table in schema.tables:
                    conn.exec_driver_sql(table.format(autoinc=self.autoincrement))
                for index in schema.indices:
                    conn.exec_driver_sql(index)
                for init_val in schema.init_values:
                    conn.exec_driver_sql(init_val)
                conn.commit()
        except:
            raise Exception("Database table creation error")

        self.logger.info("Database tables created")
        self.logger.info("Creating admin user: " + ("Success" if self.create_web_user('admin', 'password', 1, True) else "Failed"))

    def create_api_user(self, expires = False, expiration_period = 30):
        unhashed_key = base64.urlsafe_b64encode(secrets.token_bytes(36)).decode("ascii")
        hashed_key = ph.hash(unhashed_key)
        timestamp = int(datetime.now().timestamp())
        expiration_time = timestamp + (expiration_period * 24 * 60 * 60)

        with self.engine.begin() as conn:
            result = conn.exec_driver_sql(schema.api_new_user.format(wc=self.wildcard), (hashed_key, timestamp, False, 3, expires, False, expiration_time))
            new_uid = conn.exec_driver_sql(schema.api_last_user).fetchone()[0]
            conn.commit()
        self.logger.info("API user registered")
        
        return (str(new_uid)+ "~" + unhashed_key)
    
    def create_web_user(self, username: str, password: str, role_id: int, enabled: bool):
        password_hash = ph.hash(password)

        with self.engine.begin() as conn:
            result = conn.exec_driver_sql(schema.web_user_query.format(wc=self.wildcard), (username,))
            if result.fetchone():
                return False
            conn.exec_driver_sql(schema.web_new_user.format(wc=self.wildcard), (username, password_hash, role_id, enabled))
            conn.commit()
        return True

    def authenticate(self, token):

        '''user_query = """
            SELECT * FROM users WHERE
        """'''

    def login(self, username: str, password: str, ip: str):
        try:
            with self.engine.begin() as conn:
                result = conn.exec_driver_sql(schema.web_user_query.format(wc=self.wildcard), (username,))
                data = result.fetchone()
                if data is None:
                    conn.exec_driver_sql(schema.web_log.format(wc=self.wildcard), (-1, 2, "Nonexistent Account", int(datetime.now().timestamp()), ip))
                    conn.commit()
                    return False
                
                if data[4] == 0:
                    conn.exec_driver_sql(schema.web_log.format(wc=self.wildcard), (data[0], 2, "Account Disabled", int(datetime.now().timestamp()), ip))
                    conn.commit()
                    return False
                
                if check_password(data[2], password):
                    conn.exec_driver_sql(schema.web_log.format(wc=self.wildcard), (data[0], 1, None, int(datetime.now().timestamp()), ip))
                    conn.commit()
                    token = base64.urlsafe_b64encode(secrets.token_bytes(36)).decode("ascii")
                    session = Session(data[0], data[1], token, data[3])
                    self.sessions[token] = session
                    return session
                
                conn.exec_driver_sql(schema.web_log.format(wc=self.wildcard), (data[0], 2, "Wrong Password", int(datetime.now().timestamp()), ip))
                conn.commit()
                return False
        except:
            with self.engine.begin() as conn:
                conn.exec_driver_sql(schema.web_log.format(wc=self.wildcard), (-1, 2, "Server Error", int(datetime.now().timestamp()), ip))
                conn.commit()
            return False
    
    def check_token(self, token: str):
        if self.sessions.get(token) is not None:
            return True
        return False

    def logout(self, token: str, ip):
        session = self.sessions.get(token)
        if session is not None:
            del self.sessions[token]
            with self.engine.begin() as conn:
                conn.exec_driver_sql(schema.web_log.format(wc=self.wildcard), (session.uid, 3, None, int(datetime.now().timestamp()), ip))
                conn.commit()
            return True
        return False