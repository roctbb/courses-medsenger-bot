import json
import threading
from datetime import datetime

import werkzeug
from flask import request, abort, jsonify, render_template, make_response
from config import *
import sys, os


def gts():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S - ")


def log(error, terminating=False):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    if terminating:
        print(gts(), exc_type, fname, exc_tb.tb_lineno, error, "CRITICAL")
    else:
        print(gts(), exc_type, fname, exc_tb.tb_lineno, error)


# decorators
def verify_args(func):
    def wrapper(*args, **kargs):
        if not request.args.get('contract_id'):
            abort(422)
        if request.args.get('api_key') != API_KEY:
            abort(401)
        try:
            return func(request.args, request.form, *args, **kargs)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def only_doctor_args(func):
    def wrapper(*args, **kargs):
        if not request.args.get('contract_id'):
            abort(422)
        if request.args.get('api_key') != API_KEY:
            abort(401)
        # if request.args.get('source') == 'patient':
        #    abort(401)
        try:
            return func(request.args, request.form, *args, **kargs)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def verify_json(func):
    def wrapper(*args, **kargs):
        if not request.json.get('contract_id') and "status" not in request.url:
            abort(422)
        if request.json.get('api_key') != API_KEY:
            abort(401)
        # return func(request.json, *args, **kargs)
        try:
            return func(request.json, *args, **kargs)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def safe(func):
    def wrapper(*args, **kargs):
        try:
            return func(*args, **kargs)
        except werkzeug.exceptions.HTTPException as e:
            raise e
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def validated(schema):
    def decorator(func):
        def wrapper(*args, **kargs):
            errors = schema.validate(request.json)

            if errors:
                return jsonify(errors), 400

            request.json['id'] = request.view_args.get('id')

            return func(schema.load(request.json), *args, **kargs)

        wrapper.__name__ = func.__name__
        return wrapper

    return decorator


def update(obj, updates):
    for key, value in updates.items():
        setattr(obj, key, value)
    return obj


def make(model, data):
    id = data.get('id')

    if not id:
        return model(**data)
    else:
        obj = model.query.get(id)

        if not obj:
            abort(make_response(jsonify(message="Object not found"), 404))

        return update(obj, data)


def to_dict(L):
    return [el.to_dict() for el in L]
