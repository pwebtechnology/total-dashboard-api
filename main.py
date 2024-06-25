from flask import Flask, jsonify, Response, request, make_response
from variables import *
from functions import *
from api import *
from operations import *
import socket
import bson
import jwt


app = Flask(__name__)

app.config['secret_key'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918" #generated from website - just for testing will change after tests passed

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

# get_total_affiliates_data
@app.route('/total_data_no_params', methods=['GET', 'OPTIONS'])
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
    return data


@app.route('/get_builder_data_props', methods=['GET',
                                               'OPTIONS'])  # params = created_from , created_to , ftd_from , ftd_to , registered_from , registered_to , group_by[]
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

@app.route("/login")
def login():
    auth = request.authorization
    if auth and auth.password == "password": #test password need to be change on pass_check method
        token = jwt.encode({'user': auth.username, 'exp': datetime.utcnow() + timedelta(seconds=30)}, app.config['secret_key'])
        return f'<a href="http://localhost:5000/access?token={token}">Private link</a>'
    return make_response('Could not Verify', 401, {'WWW-Authenticate': 'Basic realm ="Login Required"'})

@app.route("/access")
@token_required
def access():
    return jsonify({'message': 'valid jwt token'})



asyncio.run(app.run(debug=True, host='0.0.0.0', port=5000))
