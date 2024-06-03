from flask import Flask, jsonify, Response, request
from functions import *
from api import *

app = Flask(__name__)

# Route to get total data without any parameters
@app.route('/total_data_no_params', methods=['GET'])
def total_data_no_params():
    data = get_total_affiliates_data()
    response = jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", "https://deep-traff-analysis.vercel.app")
    response.headers.add("Access-Control-Allow-Methods", "GET")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

# Route to get total data from the previous day
@app.route('/total_data_prev_day', methods=['GET'])
def total_data_prev_day():
    data = get_total_affiliates_data_prev_day()
    response = jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", "https://deep-traff-analysis.vercel.app")
    response.headers.add("Access-Control-Allow-Methods", "GET")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

# Route to compare total data
@app.route('/total_data_compare', methods=['GET'])
def total_data_compare():
    props = {
        'startDate': request.args.get('startDate'),
        'endDate': request.args.get('endDate'),
        'affiliates': request.args.getlist('affiliates[]'),
        'divider': request.args.get('divider')
    }
    data = getTotalAffilatesDataCompare(props)
    response = jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", "https://deep-traff-analysis.vercel.app")
    response.headers.add("Access-Control-Allow-Methods", "GET")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

# Route to get total builder data
@app.route('/get_builder_data_total', methods=['GET'])
def get_builder_data_total():
    data = get_total_builder_data()
    response = jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", "https://deep-traff-analysis.vercel.app")
    response.headers.add("Access-Control-Allow-Methods", "GET")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

# Route to get total builder data with specific parameters
@app.route('/get_builder_data_props', methods=['GET'])
def get_builder_data_props():
    data = get_total_builder_data()
    response = jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", "https://deep-traff-analysis.vercel.app")
    response.headers.add("Access-Control-Allow-Methods", "GET")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
