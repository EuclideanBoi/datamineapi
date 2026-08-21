import sqlalchemy as sa

engine = sa.create_engine("sqlite:///datamine.db")
check = sa.DDL("""SELECT * FROM lifecycle_event_types;""")
addition = sa.DDL("""SELECT * FROM web_users WHERE username = %s""")

try:
    with engine.begin() as conn:
        result = conn.execute(check)
        for x in result.fetchall():
            print(x)
        result = conn.exec_driver_sql("SELECT * FROM web_users WHERE username = ?;", ("admin",))
        x = result.fetchone()
        if x:
            print(x)
        '''result = conn.exec_driver_sql("SELECT password_hash FROM web_users WHERE username = %(username)s", dict(username="admin"))
        x = result.fetchone()
        if x:
            print(x)'''
except:
    raise Exception("error")