from flask import Flask, jsonify, Response, request
from variables import *
from functions import *
from api import *
from operations import *
import socket
import bson

app = Flask(__name__)
#get_total_affiliates_data
@app.route('/total_data_no_params',methods=['GET', 'OPTIONS'])
async def total_data_no_params():
    if request.method == 'OPTIONS':
        # Handle preflight request
        data = await get_total_affiliates_data()
        response = Response(data, content_type='application/json')
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, ngrok-skip-browser-warning, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("ngrok-skip-browser-warning", "true")
    else:
        # Handle actual request
        data = await get_total_affiliates_data()
        response = Response(data, content_type='application/json')
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, ngrok-skip-browser-warning , Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
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
    print(props)
    print(request.args)
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
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, ngrok-skip-browser-warning, Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("ngrok-skip-browser-warning", "true")
    else:
        # Handle actual request
        data = await get_total_affiliates_data_prev_day()
        response = Response(data, content_type='application/json')
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, ngrok-skip-browser-warning , Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("ngrok-skip-browser-warning", "true")

    return response

@app.route('/total_data_compare',methods=['GET', 'OPTIONS'])
async def total_data_compare():
    props = {
        'startDate': request.args.get('startDate'),
        'endDate': request.args.get('endDate'),
        'affiliates': request.args.getlist('affiliates[]'),
        'divider': request.args.get('divider')
    }
    print(props)
    print(request.args)
    data = await getTotalAffilatesDataCompare(props)
    response = Response(data, content_type='application/json')
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, ngrok-skip-browser-warning , Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("ngrok-skip-browser-warning", "true")
    return response

# loop = asyncio.get_event_loop()
# loop.run_until_complete(app.run(host='127.0.0.1', port=5000))



@app.route('/get_builder_data_total', methods = ['GET','OPTIONS'])
async def get_builder_data_total():
    return data


@app.route('/get_builder_data_props', methods = ['GET','OPTIONS'])# params = created_from , created_to , ftd_from , ftd_to , registered_from , registered_to , group_by[]
async def get_builder_data_props():
    data = await get_total_builder_data()
    response = Response(data, content_type='application/json')
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("ngrok-skip-browser-warning", '69420')
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, ngrok-skip-browser-warning , Access-Control-Allow-Headers, Access-Control-Allow-Origin, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    response.headers.add("Access-Control-Allow-Credentials", "true")
   # response.headers.add("ngrok-skip-browser-warning", 'true')
    return response

asyncio.run(app.run(host='0.0.0.0', port=5000))
# strart = time.time()
# end = time.time()
# print("time exec", end - strart)
