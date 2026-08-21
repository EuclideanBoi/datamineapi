tables = [
    """
        CREATE TABLE IF NOT EXISTS config (
            field_name VARCHAR(16) PRIMARY KEY,
            int_value integer,
            string_value text
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS lifecycle_event_types (
            type_id integer PRIMARY KEY,
            label VARCHAR(16) NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS web_event_types (
            type_id integer PRIMARY KEY,
            label VARCHAR(16) NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS player_event_types (
            type_id integer PRIMARY KEY,
            label VARCHAR(16) NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS roles (
            role_id integer PRIMARY KEY,
            label VARCHAR(16) NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS api_users (
            uid integer PRIMARY KEY,
            api_key CHAR(48) UNIQUE NOT NULL,
            role_id integer REFERENCES roles(role_id) NOT NULL,
            issued_time bigint NOT NULL,
            revoked boolean NOT NULL,
            expires boolean NOT NULL,
            expired boolean NOT NULL,
            expiration_time bigint
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS web_users (
            uid integer PRIMARY KEY,
            username VARCHAR(32) UNIQUE NOT NULL,
            password_hash CHAR(97) NOT NULL,
            role_id integer REFERENCES roles(role_id) NOT NULL,
            enabled boolean DEFAULT false
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS resources (
            action_id integer PRIMARY KEY,
            label VARCHAR(32) NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS acl (
            action_id integer REFERENCES resources(action_id) NOT NULL,
            role_id integer REFERENCES roles(role_id) NOT NULL,
            r_read boolean DEFAULT false,
            r_edit boolean DEFAULT false,
            r_create boolean DEFAULT false,
            r_delete boolean DEFAULT false
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS lifecycle_events (
            event_id integer PRIMARY KEY,
            uid integer REFERENCES api_users(uid) NOT NULL,
            type_id integer REFERENCES lifecycle_event_types(type_id) NOT NULL,
            time bigint NOT NULL,
            ip_address inet NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS web_events (
            event_id integer PRIMARY KEY,
            uid integer REFERENCES web_users(uid),
            type_id integer REFERENCES web_event_types(type_id) NOT NULL,
            message text,
            time bigint NOT NULL,
            ip_address inet NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS players (
            mc_uuid uuid PRIMARY KEY
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS player_events (
            event_id integer PRIMARY KEY,
            mc_uuid uuid REFERENCES players(mc_uuid) NOT NULL,
            type_id REFERENCES player_event_types(type_id) NOT NULL,
            username VARCHAR(16),
            time bigint NOT NULL,
            ip_address inet NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id integer PRIMARY KEY,
            mc_uuid uuid REFERENCES players(mc_uuid) NOT NULL,
            message text NOT NULL,
            time bigint NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS commands (
            command_id integer PRIMARY KEY,
            mc_uuid uuid REFERENCES players(mc_uuid) NOT NULL,
            command text NOT NULL,
            successful bool NOT NULL,
            time bigint NOT NULL
        );
    """
]

indices = [
    """CREATE UNIQUE INDEX idx_api_key ON api_users(api_key);""",
    """CREATE UNIQUE INDEX idx_web_username ON web_users(username);""",
    """CREATE INDEX idx_event_uuid ON player_events(mc_uuid);""",
    """CREATE INDEX idx_chat_uuid ON chat_messages(mc_uuid);""",
    """CREATE INDEX idx_command_uuid ON commands(mc_uuid);"""
]

init_values = [
    """
        INSERT INTO config (field_name, string_value) VALUES
        ('db_schema_version', '1.0');
    """,
    """
        INSERT INTO lifecycle_event_types (label) VALUES
        ('startup'),
        ('shutdown'),
        ('crash');
    """,
    """
        INSERT INTO web_event_types (label) VALUES
        ('login'),
        ('failed_login'),
        ('logout');
    """,
    """
        INSERT INTO roles (label) VALUES
        ('Administrator'),
        ('Moderator'),
        ('API User'),
        ('User'),
        ('Guest');
    """,
    """
        INSERT INTO resources (label) VALUES
        ('Players'),
        ('Chat'),
        ('Commands'),
        ('Lifecycle Events'),
        ('Users');
    """
]

check_exists = """SELECT string_value FROM config WHERE field_name = 'db_schema_version';"""

api_new_user = """
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

web_user_query = """
            SELECT * FROM web_users WHERE username = ?;
        """

web_new_user = """
            INSERT INTO web_users (
                username,
                password_hash,
                role_id,
                enabled
            ) VALUES (?, ?, ?, ?);
        """

web_log = """
            INSERT INTO web_events (
                uid,
                type_id,
                message,
                time,
                ip_address
            ) VALUES (?, ?, ?, ?, ?);
        """