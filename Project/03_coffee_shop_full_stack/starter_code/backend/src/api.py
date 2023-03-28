import os
from flask import Flask, request, jsonify, abort, render_template
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, get_token_auth_header, requires_auth, verify_decode_jwt

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
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
@app.route('/')
def home():
    return jsonify({'success': True}), 200

@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            abort (404)
        
        formatted_drinks = list(map(Drink.short, Drink.query.all()))

        return jsonify({
            "success" : True,
            "drinks" : formatted_drinks
        }, 200)
    except:
        abort (500)

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
def get_drinks_detail(jwt):
    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            abort (404)

        formatted_drinks = list(map(Drink.long, Drink.query.all()))
        print (formatted_drinks)
        return jsonify ({
            "success" : True,
            "drinks" : formatted_drinks
        }, 200)
    except:
        abort (500)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    try:
        response = request.get_json()
        title = response.get("title", None)
        recipe = response.get("recipe", None)

        print(title)
        print(recipe)

        if title is None or recipe is None:
            abort(400)

        format_recipe = json.dumps(recipe)

        drink = Drink(title = title, recipe = format_recipe)
        drink.insert()

        return jsonify({
            "success" : True,
            "drink" : drink.long()
        }, 200)
    except:
        abort (500)

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
@app.route('/drinks/<int:drink_id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def change_drinks(jwt, drink_id):
    try:
        response = request.get_json()
        title = response.get("title", None)

        if title is None:
            abort (400)
    
        drink = Drink.query.filter_by(id = drink_id).one_or_none()

        if drink is None:
            abort (404)

        drink.title = title 
        drink.update()

        return jsonify({
            "success" : True,
            "drink" : drink.long()
        })

    except Exception as e:
        print(e)
        abort (500)

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
@app.route('/drinks/<int:drink_id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, drink_id):
    try:
        response = request.get_json()

        drink = Drink.query.filter_by(id = drink_id).one_or_none()

        if drink is None:
            abort (404)
        try:
            drink.delete()

            return jsonify({
                "success" : True,
                "delete" : drink_id
            })
        except:
            abort (422)
    except:
        abort (500)


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
    each error handler should return (with approprate messages):
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
        "success" : False,
        "error" : 404,
        "message" : "resource not found"
    }), 404
 
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success" : False,
        "error" : 400,
        "message" : "bad request"
    }), 400

@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success" : False,
        "error" : 500,
        "message" : 'an unexpected error occured, request could not be processed'
    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success" : False,
        "error" : error.status_code,
        "message" : error.error
    }), error.status_code
