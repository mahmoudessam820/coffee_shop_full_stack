#----------------------------------------------------------------#
# Imports
#----------------------------------------------------------------#
import os
from flask import (Flask, request, jsonify, abort)
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import (db_drop_and_create_all, setup_db, Drink)
from .auth.auth import (AuthError, requires_auth)


#-----------------------------------------------------------------#
# Create app configure
#-----------------------------------------------------------------#

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"*": {'origins': r"*"}})

#----------------------------------------------------------------#
# Setup CORS
#----------------------------------------------------------------#

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origions', '*')
    response.headers.add('Access-Control-Allow-headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-methods', 'GET,PUT,POST,DELETE,PATCH')
    return response


#----------------------------------------------------------------#
# API
#----------------------------------------------------------------#

@app.route('/drinks', methods=['GET'])
def get_drinks():
    
    try:
        get_all_drinks = Drink.query.all()
        drinks_details = [drinks.long() for drinks in get_all_drinks]
        return jsonify({
            'success': True,
            'drinls_detalis': drinks_details
        }), 200
    except:
        abort(500)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_all_drinks_details(payload):

    try:
        get_all_drinks = Drink.query.all()
        drinks_details = [drinks.long() for drinks in get_all_drinks]
        return jsonify({
            'success': True,
            'drinls_detalis': drinks_details
        }), 200

    except Exception:
        abort(500)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drinks_by_manager(token):
    try:

        body = request.get_json()
        n_title = body.get('title', None)
        n_recipe = body.get('recipe', None)
        print(n_title, n_recipe)

        if n_title is None or n_recipe is None:
            abort(422)

        new_drink = Drink(title=n_title, recipe=json.dumps(n_recipe))
        new_drink.insert()

    except:
        abort(500)

    return jsonify({
        'success': True,
        'New_drinks': [new_drink.long()]
    }), 200 


@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def edit_drinks_by_manager(payload, drink_id):

    get_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if get_drink is None:
        return json.dumps({
            'success': False,
            'error': 'Drink' + id + 'Is not found'
        }), 404
    
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if title is not None:
        get_drink.title = title

    if recipe is not None:
        get_drink.recipe = recipe
    
    try: 
        get_drink.update() 

    except Exception as e:
        abort(422)

    return jsonify({
        'success': True,
        'drink': [get_drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_by_manager(payload, drink_id):

    one_drink = Drink.query.get(drink_id)

    if one_drink is None:
        abort(404)

    try:
        one_drink.delete()
        return jsonify({
            'success': True,
            'delete': one_drink.id
        }), 200
        
    except Exception:
        abort(500)

#----------------------------------------------------------------#
# Error handlers
#----------------------------------------------------------------#

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(400)
def Bad_Request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

@app.errorhandler(401)
def Not_Authorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Not Authorized"
    }), 40

@app.errorhandler(AuthError)
def process_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code

    return response