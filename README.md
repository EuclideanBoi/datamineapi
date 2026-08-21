# Datamine API
FlaskREST API for log aggregation and web portal  
## Setup
    python3 -m venv venv  
    venv/bin/python -m pip install -r requirements.txt
    
    # Replace 365 with however many days you want the certificate to be valid for  
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

    # Launch with local SQLite DB  
    venv/bin/gunicorn --certfile cert.pem --keyfile key.pem -b 0.0.0.0:8000 app.app

    # Launch with remote Postgres DB  
    export DATABASE_URL=postgresql://username:password@host/datamine  
    venv/bin/gunicorn --certfile cert.pem --keyfile key.pem -b 0.0.0.0:8000 app.app