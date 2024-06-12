import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from variables import *

async def fetch_promises(database, collections, query):
    promises = []
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        for collection_name in collections:
            collection = database.get_collection(collection_name)
            cursor = collection.aggregate(query)
            promise = loop.run_in_executor(None, list, cursor)
            promises.append(promise)
    return await asyncio.gather(*promises)

async def execute_data_from_crm(database, collections, query):
    mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    try:
        db = mongo_client.get_database(database)
        results = await fetch_promises(db, collections, query)
        return [item for sublist in results for item in sublist]

    finally:
        mongo_client.close()
async def execute_data_from_crm_builder(database, collections, query):
    mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    try:
        db = mongo_client.get_database(database)
        results = await fetch_promises(db, collections, query)
        total_records = sum(db[collection].count_documents({}) for collection in collections)
        flattened_results = [item for sublist in results for item in sublist]
        return flattened_results, total_records
    finally:
        mongo_client.close()


async def execute_data_from_payment(props=None):
    database = payment_parametrs['database']
    query = payment_parametrs['query']
    queryAll = payment_parametrs['queryAll']
    current_query = query(props) if props else queryAll
    result = await execute_data_from_crm(database, payment_collection, current_query)

    return result


async def execute_data_from_payment_builder(props=None):
    database = payment_parametrs_builder['database']
    query = payment_parametrs_builder['query']
    queryAll = payment_parametrs_builder['queryAll']
    current_query = query(props) if props else queryAll
    result, total_count = await execute_data_from_crm_builder(database, payment_collection, current_query)

    return result, total_count

async def execute_data_from_payment_prev_day(props=None):
    database = payment_parametrs['database']
    query = payment_parametrs['queryPrevDay']
    result = await execute_data_from_crm(database, payment_collection, query)

    return result

async def execute_data_from_conversion_crm(props=None):
    database = conv_parameters['database']
    query = conv_parameters['query']
    queryAll = conv_parameters['queryAll']
    current_query = query(props) if props else queryAll
    result = await execute_data_from_crm(database, conv_collections, current_query)

    return result

async def execute_data_from_conversion_crm_prev_day():
    database = conv_parameters['database']
    query = conv_parameters['queryPrevDay']
    result = await execte_data_from_crm(database, conv_collections, query)

    return result

async def execute_data_from_conversion_crm_builder(props):
    database = conv_parameters_builder['database']
    query = conv_parameters_builder['query']
    queryAll = conv_parameters_builder['queryAll']
    current_query = query(props) if props else queryAll
    result, total_count = await execute_data_from_crm_builder(database, conv_collections, current_query)
    key_renames = {
        'Trader_Source': 'Source',
        'Trader_Registered_At': 'Registered_At',
        'Trader_Sale_Status': 'Sale_status',
        'Trader_ID': 'Customer_ID',
        'Campaign_Campaign_Name': 'Campaign',
        'Desk_Desk_Name': 'Desk_Conversion',
        'Trader_Country': 'Country',
        'Brocker': 'Main_stage',
        'Trader_First_assigned_broker': 'Broker_Conv',
        'Brand': 'Brand_Conv',
        'Trader_Ftd_Date': 'FTD_Date',
        'Trader_Last_Login': 'Last_login'
    }

    return result, total_count


async def execute_data_from_retention_crm(props=None):
    database = ret_parameters['database']
    query = ret_parameters['query']
    queryAll = ret_parameters['queryAll']
    current_query = query(props) if props else queryAll
    result = await execute_data_from_crm(database, ret_collections, current_query)

    return result

async def execute_data_from_retention_crm_prev_day(props=None):
    database = ret_parameters['database']
    query = ret_parameters['queryPrevDay']
    result = await execute_data_from_crm(database, ret_collections, query)

    return result

async def execute_data_from_retention_crm_builder(props):
    database = ret_parameters_builder['database']
    query = ret_parameters_builder['query']
    queryAll = ret_parameters_builder['queryAll']
    current_query = query(props) if props else queryAll
    result, total_count = await execute_data_from_crm_builder(database, ret_collections, current_query)
    key_renames = {
        'Ticket_Trader_First_Assigned_Broker': 'Broker_Ret',
        'Campaign_Name': 'Campaign',
        'Ticket_Method': 'Method',
        'Trader_Country': 'Country',
        'Trader_ID': 'Customer_ID',
        'Broker': 'Main_stage',
        'is_no_ftd': 'Is_no_ftd',
        'Trader_Source': 'Source',
        'Brand': 'Brand_Ret',
        'Trader_Ftd_Date': 'FTD_Date',
        'Desk_Desk_Name': 'Desk_Retention',
        'is_removed': 'Is_removed'     
        
    }
    renamed_result = []
    for item in result:
        renamed_item = {key_renames.get(k,k): v for k, v in item.items()}
        renamed_result.append(renamed_item)
    return renamed_result, total_count