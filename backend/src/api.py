import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def retrieve_drinks():
    query_drinks = Drink.query.all()

    # If drinks has no items return error 404
    if len(query_drinks) == 0:
        abort(404)

    drinks = [drink.short() for drink in query_drinks]

    return jsonify({
        'success' : True,
        'drinks': drinks
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
    query_drinks = Drink.query.all()

    # If drinks has no items return error 404
    if len(query_drinks) == 0:
        abort(404)

    drinks = [drink.long() for drink in query_drinks]

    return jsonify({
        'success' : True,
        'drinks': drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if title is None or recipe is None:
        abort(404)

    try:
        drink = Drink(
            title=title,
            recipe=json.dumps(recipe), #recipe is a dict, dumps converts to json string
        )

        drink.insert()
        drink = drink.long()
        return jsonify({
            "success": True,
            "drinks": drink
        }), 200

    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    body = request.get_json()

    # If no matching drink, abort
    if drink is None:
        abort(404)

    try:
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        #assign new values to drink if values are provided
        if title is not None:
            drink.title = title
        if recipe is not None:
            drink.recipe = json.dumps(recipe)
        
        drink.update()
        
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    
    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        # If no matching drink, abort
        if drink is None:
            abort(404)
        
        drink.delete()

        return jsonify({
            'success': True,
            'delete': id
        }), 200
    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

@app.errorhandler(400)
def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

@app.errorhandler(405)
def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

@app.errorhandler(500)
def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error, please try again later"
        }), 500
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description'],
        }), error.status_code