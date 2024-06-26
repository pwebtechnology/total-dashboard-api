from flask import Flask, jsonify, Response, request, make_response
from variables import *
from functions import *
from api import *
from operations import *
import socket
import bson
import jwt
from functools import wraps
import flask_jwt_extended
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt_identity)
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_mongoengine import MongoEngine
from mongoengine import Document, StringField, connect

app = Flask(__name__)

app.config['SECRET_KEY'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918" #generated from website - just for testing will change after tests passed
app.config["JWT_SECRET_KEY"] = app.config['SECRET_KEY']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)
mongo_uri = "mongodb://NikKimp:NikKimp@172.23.2.15:27017/?tls=false&authMechanism=DEFAULT"
connect(host=mongo_uri)

jwt = JWTManager(app)
#db = MongoEngine()
#db.init_app(app)

class Users(Document):
    username = StringField(max_length=250, unique=True, required=True)
    password = StringField(max_length=250, required=True)
    meta = {'collection': 'user_creds',
            'db': 'Users'}

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'error': 'token is missing'}), 403
        try:
            jwt.decode(token, app.config['secret_key'], algorithms="HS256")
        except Exception as error:
            return jsonify({'error': 'token is invalid or expired'})
        return f(*args, **kwargs)
    return decorated

def get_user_pass(username):
    print(username)
    logging.debug(username)
    user = Users.objects(username=username).first()
    if user:
        return user.password
    return None

def pass_check(username, password):
    stored_password = get_user_pass(username)
    print(stored_password)
    logging.debug(stored_password)
    if stored_password and check_password_hash(stored_password, password):
        return True
    return False

# get_total_affiliates_data
@app.route('/total_data_no_params', methods=['GET', 'OPTIONS'])
#@jwt_required()
async def total_data_no_params():
    if request.method == 'OPTIONS':
        # Handle preflight request
        data = await get_total_affiliates_data()
        response = Response(data, content_type='application/json')
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("ngrok-skip-browser-warning", "true")
    else:
        # Handle actual request
        data = await get_total_affiliates_data()
        response = Response(data, content_type='application/json')
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("ngrok-skip-browser-warning", "true")

    return response


'''
@app.route('/total_data_prev_day',methods=['GET','OPTIONS'])
async def total_data_prev_day():
    data = await get_total_affiliates_data_prev_day()
    response = Response(data, content_type='application/json')
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("ngrok-skip-browser-warning", "true")
    return response

        props = {
        'startDate': request.args.get('startDate'),
        'endDate': request.args.get('endDate'),
        'affiliates': request.args.getlist('affiliates[]'),
        'divider': request.args.get('divider')
    }

    data = await getTotalAffilatesDataCompare(props)
    response = Response(data, content_type='application/json')
'''


@app.route('/total_data_prev_day', methods=['GET', 'OPTIONS'])
#@jwt_required()
async def total_data_prev_day():
    if request.method == 'OPTIONS':
        # Handle preflight request
        data = await get_total_affiliates_data_prev_day()
        response = Response(data, content_type='application/json')
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("ngrok-skip-browser-warning", "true")
    else:
        # Handle actual request
        data = await get_total_affiliates_data_prev_day()
        response = Response(data, content_type='application/json')
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("ngrok-skip-browser-warning", "true")

    return response


@app.route('/total_data_compare', methods=['GET', 'OPTIONS'])
#@jwt_required()
async def total_data_compare():
    props = {
        'startDate': request.args.get('startDate'),
        'endDate': request.args.get('endDate'),
        'affiliates': request.args.getlist('affiliates[]'),
        'divider': request.args.get('divider')
    }

    data = await getTotalAffilatesDataCompare(props)
    response = Response(data, content_type='application/json')
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers",
                         "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("ngrok-skip-browser-warning", "true")
    return response

@app.route('/get_builder_data_total', methods=['GET', 'OPTIONS'])
async def get_builder_data_total():
    return None


@app.route('/get_builder_data_props', methods=['GET',
                                               'OPTIONS'])  # params = created_from , created_to , ftd_from , ftd_to , registered_from , registered_to , group_by[]
#@jwt_required()
async def get_builder_data_props():
    pageIndex = int(request.args.get('pageIndex', 0))
    pageSize = int(request.args.get('pageSize', 10))
    dimentions = request.args.getlist('dimentions[]')
    metrics = request.args.getlist('metrics[]')
    logging.debug(metrics)
    props = {
        'pageIndex': pageIndex,
        'pageSize': pageSize,
        'dimentions': dimentions,
        'metrics': metrics
    }
    #metrix = str()
    data = await get_total_builder_data_props(props)

    response = jsonify(data)
    #response = data
    response.headers.add("Access-Control-Allow-Origin", "*")

    response.headers.add("ngrok-skip-browser-warning", '69420')

    response.headers.add("Access-Control-Allow-Headers",
                         "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    response.headers.add("Access-Control-Allow-Credentials", "true")

    return response

@app.route("/login", methods=['POST'])
def login():
    print("here is logging method called")
    logging.debug("here is logging method called")
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    if pass_check(data['username'], data['password']):
        token = create_access_token(identity=data['username'])
        return jsonify({'token': token}), 200
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route("/logout", methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/access", methods=["GET"])
@jwt_required()
def access():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Hello, {current_user}!'})



asyncio.run(app.run(debug=True, host='0.0.0.0', port=5000))
