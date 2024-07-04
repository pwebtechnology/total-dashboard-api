from quart import Quart, jsonify, request, make_response, Response
from quart_cors import cors
from variables import *
from functions import *
from api import *
from operations import *
import bson
import jwt
from functools import wraps
from quart_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity,
    create_refresh_token, set_access_cookies, unset_jwt_cookies, decode_token, verify_jwt_in_request
)
from werkzeug.security import generate_password_hash, check_password_hash
from mongoengine import Document, StringField, connect
import os
import logging
from datetime import datetime, timedelta

app = Quart(__name__)
app = cors(app, allow_origin="http://127.0.0.1",
           allow_headers=["Authorization", "Content-Type", "Access-Control-Allow-Origin", "X-Requested-With", "Cross-Origin-Resource-Policy"],
           allow_methods=['GET', 'POST', 'OPTIONS',],
           allow_credentials=True,
           expose_headers=['Authorization'])
jwt_manager = JWTManager(app)

# Quart configuration
app.config['SECRET_KEY'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918"
app.config['JWT_SECRET_KEY'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_CSRF_IN_COOKIES'] = False
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_REFRESH_SECRET_KEY'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918"

# MongoDB Configuration
mongo_uri = "mongodb://NikKimp:NikKimp@172.23.2.15:27017/?tls=false&authMechanism=DEFAULT"
connect(host=mongo_uri)


# MongoDB Models
class Users(Document):
    username = StringField(max_length=250, unique=True, required=True)
    password = StringField(max_length=250, required=True)
    meta = {'collection': 'user_creds', 'db': 'Users'}


# Helper Functions
async def get_user_pass(username):
    logging.debug(f"Fetching password for username: {username}")
    user = await Users.objects(username=username).first_async()
    return user.password if user else None


async def pass_check(username, password):
    stored_password = await get_user_pass(username)
    if stored_password and check_password_hash(stored_password, password):
        return True
    return False


# Token Required Decorator
def token_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        print("here is requst token checking started")
        auth_header = request.headers.get('Authorization')
        print("HEARED FROM REQUEST +++++++++++++++++++++++++++++++++++++++++++++++++++++++", request.headers)
        print("Auth header", auth_header)
        if auth_header:
            token = auth_header.split(' ')[1]  # "Bearer <token>"
        else:
            print("can`t parse auth header")
            token = None
        if not token:
            return jsonify({'error': 'Token is missing'}), 403
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except Exception as error:
            return jsonify({'error': 'Token is invalid or expired'}), 403
        return await f(*args, **kwargs)

    return decorated


# Routes
@app.route('/total_data_no_params', methods=['GET', 'OPTIONS'])
async def total_data_no_params():
    if request.method == 'OPTIONS':
        data = await get_total_affiliates_data()
    else:
        data = await get_total_affiliates_data()

    response = await make_response(Response(data, content_type='application/json'))
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers",
                         "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("ngrok-skip-browser-warning", "true")
    return response


@app.route('/total_data_prev_day', methods=['GET', 'OPTIONS'])
async def total_data_prev_day():
    if request.method == 'OPTIONS':
        data = await get_total_affiliates_data_prev_day()
    else:
        data = await get_total_affiliates_data_prev_day()

    response = await make_response(Response(data, content_type='application/json'))
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers",
                         "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("ngrok-skip-browser-warning", "true")
    return response


@app.route('/total_data_compare', methods=['GET', 'OPTIONS'])
async def total_data_compare():
    props = {
        'startDate': request.args.get('startDate'),
        'endDate': request.args.get('endDate'),
        'affiliates': request.args.getlist('affiliates[]'),
        'divider': request.args.get('divider')
    }
    data = await getTotalAffilatesDataCompare(props)
    if request.method == 'OPTIONS':
        response = await make_response(Response(data, content_type='application/json'))
    else :
        response = await make_response(Response(data, content_type='application/json'))
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers",
                         "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        response.headers.add("Access-Control-Allow-Credentials", "true")
    return response, 200


@app.route('/get_builder_data_total', methods=['GET', 'OPTIONS'])
async def get_builder_data_total():
    return jsonify({"message": "This endpoint is not yet implemented"})


USERS = {
    'first_user': {
        'password': '123'
    }
}


@app.route('/get_builder_data_props', methods=['GET', 'OPTIONS'])
@token_required
async def get_builder_data_props():
    print("cookies :", request.cookies)
    print("headers: ", request.headers)
    try:
        pageIndex = int(request.args.get('pageIndex', 0))
        pageSize = int(request.args.get('pageSize', 10))
        dimentions = request.args.getlist('dimentions[]')
        metrics = request.args.getlist('metrics[]')
        props = {
            'pageIndex': pageIndex,
            'pageSize': pageSize,
            'dimentions': dimentions,
            'metrics': metrics
        }
        data = await get_total_builder_data_props(props)
        print("response data :",data)
        response = jsonify(data)
        response.headers.add("Access-Control-Expose-Headers", "Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Request-Headers", "Authorization")
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return make_response(jsonify({"error": "Internal Server Error"}), 500)


@app.route("/login", methods=['GET', 'POST'])
async def login():
    data = await request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        response = jsonify({'error': 'Username and password are required', 'code': 400})
        return response, 400

    username = data['username']
    password = data['password']
    if username in USERS and USERS[username]['password'] == password:
        access_token = create_access_token(identity={'username': username, 'password': password})
        refresh_token = create_refresh_token(identity={'username': username, 'password': password})

        response = await make_response(jsonify({'accessToken': access_token, 'login': True, 'username': username}))

        max_age_90_days = 90 * 24 * 60 * 60
        expires_30_days = datetime.utcnow() + timedelta(days=30)

        response.set_cookie('refresh_token_cookie', refresh_token, httponly=True, path='/', max_age=max_age_90_days,
                            expires=expires_30_days.strftime("%a, %d-%b-%Y %H:%M:%S GMT"), samesite='None',
                            domain='172.23.2.15')
        response.set_cookie('access_token_cookie', access_token, httponly=True, path='/', max_age=max_age_90_days,
                            expires=expires_30_days.strftime("%a, %d-%b-%Y %H:%M:%S GMT"), samesite='None',
                            domain='172.23.2.15')
        response.headers.add("Access-Control-Expose-Headers", "Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Request-Headers", "Authorization")
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    else:
        return make_response(jsonify({'error': 'Invalid username or password'}), 401)

@app.route('/refresh', methods=['POST'])
@app.before_request
async def refresh():
    print("cookies:",request.cookies)
    try:
        refresh_token = request.cookies.get('refresh_token_cookie')
        if refresh_token:
            decoded_token = decode_token(refresh_token)
            identity = decoded_token.get('sub')
            if not identity:
                return jsonify({'error': 'Failed to identify your connection, log in again please'}), 403

            access_token = create_access_token(identity=identity)
            response = jsonify({'refresh': True, 'accessToken': access_token})
            set_access_cookies(response, access_token)
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers",
                                 "Content-Type, Authorization, Access-Control-Allow-Headers, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response, 200
    except Exception as error:
        logging.error(f"Error during token refresh: {error}")
        return jsonify({'error': 'Failed to identify your connection, log in again please'}), 403
    return jsonify({'message': 'Unauthorized'}), 406

@app.route("/protected", methods=['GET'])
async def protected():
    try:
        await verify_jwt_in_request()
        current_user = get_jwt_identity()
        response = jsonify(logged_in_as=current_user, code=200)
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, Access-Control-Allow-Headers, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    except Exception as e:
        logging.error(f"Error in protected route: {e}")
        return jsonify({'error': 'Unauthorized', 'code': 403}), 403

@app.route("/logout", methods=['POST'])
@token_required
async def logout():
    response = jsonify({'logout': True})
    unset_jwt_cookies(response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers",
                         "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response, 200

@app.route("/access", methods=['GET'])
@token_required
async def access():
    print("access request header:", request.headers)
    print("here is start giving an access")
    try:
        print("access request header:",request.headers)
        #await verify_jwt_in_request()

        current_user = get_jwt_identity()
        response = jsonify({'message': f'Hello, {current_user}!'})
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    except Exception as e:
        logging.error(f"Error in access route: {e}")
        return jsonify({'error': 'Something went wrong, try to refresh the page or try again later', 'code': 403}), 403

# Run Quart Application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
