from flask import Flask, jsonify, Response, request, make_response
from flask_cors import CORS
from variables import *
from functions import *
from api import *
from operations import *
import socket
import bson
import jwt
from functools import wraps
import flask_jwt_extended
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token,
                                set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_jwt, decode_token,
                                verify_jwt_in_request)
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_mongoengine import MongoEngine
from mongoengine import Document, StringField, connect
from asgiref.sync import async_to_sync
import os
import logging

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(astimate)s:%(levelname)s:%(message)s')

app = Flask(__name__)
jwt_manager = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5173",
                             "allow_headers": ["Authorization", "Content-Type", "Access-Control-Allow-Origin"]}},
     supports_credentials=True, expose_headers='Authorization')
app.config[
    'SECRET_KEY'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918"  # generated from website - just for testing will change after tests passed
app.config['JWT_SECRET_KEY'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_SECRET_KEY'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918"
app.config['JWT_REFRESH_SECRET_KEY'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918"
mongo_uri = "mongodb://NikKimp:NikKimp@172.23.2.15:27017/?tls=false&authMechanism=DEFAULT"
connect(host=mongo_uri)


# db = MongoEngine()
# db.init_app(app)

class Users(Document):
    username = StringField(max_length=250, unique=True, required=True)
    password = StringField(max_length=250, required=True)
    role = StringField(max_length=250, required=True)
    meta = {'collection': 'user_creds',
            'db': 'Users'}


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.cookies.get('access_token_cookie')
        auth_cookie = request.cookies.get('access_token_cookie')

        token = None
        if auth_header:
            token = auth_header.split(' ')[1]  # "Bearer <token>"
        if auth_cookie:
            token = auth_cookie

        if not token:
            return jsonify({'error': 'token is missing'}), 403

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            username = payload.get('identity', {}).get('username')
            if not username:
                return jsonify({'error': 'Invalid token payload'}), 403

            # Pass the username to the decorated function
            return f(username, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'token is expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'token is invalid'}), 403

    return decorated


def jwt_required_from_cookie(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Extract the token from cookies
        cookies = request.cookies
        token = cookies.get('access_token_cookie')
        if token is None:
            return jsonify({"msg": "Missing access token", "token": token, "cookies": cookies}), 401

        # Manually verifying the token
        try:
            decoded_token = decode_token(token)
            current_user = decoded_token['identity']
            print(f"Decoded Token: {decoded_token}")
            print(f"Current User: {current_user}")
        except exceptions.JWTDecodeError as e:
            print(f"JWT Decode Error: {e}")
            return jsonify({"msg": "Invalid token", "token": token, "error": str(e)}), 401
        except Exception as e:
            print(f"General Exception: {e}")
            return jsonify({"msg": "Invalid token", "token": token, "exception": str(e)}), 401

        # Pass the current_user to the decorated function
        return fn(current_user, *args, **kwargs)

    return wrapper


def get_curr_user():
    auth_cookie = request.cookies.get('access_token_cookie')
    payload = jwt.decode(auth_cookie, app.config['SECRET_KEY'], algorithms=["HS256"])
    username = payload.get('identity', {}).get('username')
    return username


def role_required(role_keyword):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            if role_keyword.lower() in identity['role'].lower():
                return fn(*args, **kwargs)
            else:
                return jsonify({'error': 'Unauthorized access', 'code': 403}), 403

        return wrapper

    return decorator


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
# @jwt_required()
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
# @jwt_required()
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
# @jwt_required()
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
# @jwt_required(locations=['headers'])
async def get_builder_data_props():
    # Ensure the JWT is valid and present
    try:
        # identity = get_jwt_identity()
        # logging.debug(f"JWT Identity: {identity}")

        # Extract query parameters
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

        # Assuming get_total_builder_data_props is an async function
        data = await get_total_builder_data_props(props)
        print("data is :", data)
        response = make_response(jsonify({'data': data, 'is_data': True}), 200)
        response.headers.add("Access-Control-Request-Headers", "Authorization")
        return response, 200
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return make_response(jsonify({"error": "Internal Server Error"}), 500)


'''
@app.route("/login", methods=['GET', 'OPTIONS'])
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
'''
USERS = {
    'first_user': {
        'password': '123'
    }
}


@app.route("/login", methods=['GET', 'POST'])
def login():
    uri = "mongodb://NikKimp:NikKimp@172.23.2.15:27017/?tls=false&authMechanism=DEFAULT"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['Users']
    user_collection = db['user_creds']
    data = request.get_json()
    logging.debug("here is login started")
    print(data)
    if not data or not data.get('username') or not data.get('password'):
        response = jsonify({'error': 'Username and password are required', 'code': 400})
        return response, 400

    username = data['username']
    password = data['password']
    user = user_collection.find_one({'username': username})
    if not user or user['password'] != password:
        response = jsonify({'error': 'Invalid username or password', 'code': 401})
        return response, 401
    else:
        role = 'test_role'
        access_token = create_access_token(identity={'username': username, 'role': role})
        refresh_token = create_refresh_token(identity={'username': username})
        print("Tokens created")
        response = make_response(jsonify({'accessToken': access_token, 'login': True, 'username': username}))
        max_age_90_days = 90 * 24 * 60 * 60
        expires_30_days = datetime.utcnow() + timedelta(days=30)
        response.set_cookie('receive-cookie-deprecation', '1', httponly=True, path='/', max_age=max_age_90_days,
                            expires=expires_30_days.strftime("%a, %d-%b-%Y %H:%M:%S GMT"), samesite='None', secure=True)
        response.set_cookie('refresh_token_cookie', refresh_token, httponly=True, path='/', max_age=max_age_90_days,
                            expires=expires_30_days.strftime("%a, %d-%b-%Y %H:%M:%S GMT"), samesite='None', secure=True)
        response.set_cookie('access_token_cookie', access_token, httponly=True, path='/', max_age=max_age_90_days,
                            expires=expires_30_days.strftime("%a, %d-%b-%Y %H:%M:%S GMT"), samesite='None', secure=True)
        # response.headers.add("Access-Control-Allow-Credentials",True)

        # set_access_cookies(response, access_token)
        # set_refresh_cookies(response, refresh_token)
        print(f"Refresh Response: {response.get_data(as_text=True)}")
        print(f"Set-Cookie Header: {response.headers.get('Set-Cookie')}")
        return response, 200


@app.route('/refresh', methods=['POST'])
# @jwt_required(refresh=True)
def refresh():
    print(verify_jwt_in_request(locations=['headers', 'cookies']))
    print(f"Request Headers: {request.headers}")
    print(f"Request Cookies: {request.cookies}")
    # data = request.get_json()
    # print(data)
    refresh_token = request.cookies.get('refresh_token_cookie')
    print(f"Received refresh token: {refresh_token}")

    if refresh_token:
        try:
            # Decode the refresh token
            decoded_token = jwt.decode(refresh_token, key=os.getenv('REFRESH_TOKEN_SECRET'), algorithms=['HS256'])

            # You should verify the token and get user credentials if needed
            user_identity = decoded_token['identity']  # Or retrieve from your database

            # Generate a new access token
            access_token = create_access_token(identity=user_identity, expires_delta=False)

            return jsonify(accessToken=access_token), 200

        except Exception as e:
            # In case of any error (e.g., token invalid)
            return jsonify(message='Unauthorized'), 406

    return jsonify(message='Unauthorized'), 406


'''
def refresh():
    try:
        #cookies_data = request.cookies.get()
        refresh_token = request.cookies.get('refresh_token_cookie')
        print("here is refresh token:", refresh_token)
        logging.debug(f"here is refresh token: {refresh_token}")
        #if not refresh_token:
         #   return jsonify({'error': 'Refresh token is missing'}), 403

        decoded_token = decode_token(refresh_token)
        print(decoded_token)
        logging.debug(decoded_token)
        identity = decoded_token.get('sub')
        logging.debug(f"Decoded token identity: {identity}")

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
'''


@app.route("/protected", methods=['GET'])
# @token_required
def protected():
    print(verify_jwt_in_request(locations=['headers', 'cookies']))
    current_user = get_jwt_identity()
    response = jsonify(logged_in_as=current_user, code=200)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers",
                         "Content-Type, Authorization, Access-Control-Allow-Headers, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


def validate_token(token):
    try:
        # Verify and decode the token
        decoded_token = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        # You may perform additional checks here, such as checking against a database or cache
        return True
    except:
        return False


@app.route("/logout", methods=['POST'])
@token_required
def logout():
    response = jsonify({'logout': True})
    unset_jwt_cookies(response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers",
                         "Content-Type, Authorization, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response, 200


@app.route("/access", methods=['GET', 'OPTIONS'])
@jwt_required(locations=['cookies'])
def access():
    try:
        current_user = get_jwt_identity()
        access_token_cookie = request.cookies.get('access_token_cookie')
        print(f"Current User: {current_user}")
        response = jsonify({
            'message': f'Hello, {current_user}!',
            'accessToken': access_token_cookie
        })
        return response, 200
    except Exception as e:
        print(f"Error: {e}")
        response = jsonify({'error': 'Something went wrong, try to refresh the page or try again later'})
        return response, 401


# asyncio.run(app.run(host='0.0.0.0', port=5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)