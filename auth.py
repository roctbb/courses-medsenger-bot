from config import *
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    if username == EDITOR_LOGIN and check_password_hash(EDITOR_HASH, password):
        return username
