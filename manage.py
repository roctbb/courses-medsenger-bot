from flask import Flask
from models import db
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
from flask_marshmallow import Marshmallow

from config import *

app = Flask(__name__)
ma = Marshmallow(app)
auth = HTTPBasicAuth()

db_string = "postgresql://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string

db.init_app(app)

migrate = Migrate(app, db)
