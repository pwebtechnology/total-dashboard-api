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
    result = await execute_data_from_crm(database, conv_collections, query)

    return result

async def execute_data_from_conversion_crm_builder(props):
    database = conv_parameters_builder['database']
    query = conv_parameters_builder['query']
    queryAll = conv_parameters_builder['queryAll']
    #current_query = query(props) if props else queryAll
    current_query = queryAll
    result, total_count = await execute_data_from_crm_builder(database, conv_collections, current_query)
    renamed_result = [{conv_key_renames.get(k, k): v for k, v in item.items()} for item in result]
    return {'data': renamed_result,'total_count': total_count}


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
    #current_query = query(props) if props else queryAll
    current_query = queryAll
    result, total_count = await execute_data_from_crm_builder(database, ret_collections, current_query)
    renamed_result = [{ret_key_renames.get(k, k): v for k, v in item.items()} for item in result]
    return {'data': renamed_result,'total_count': total_count}


async def execute_ret_collection_names():
    mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    db = mongo_client['admin']
    collection = db['ret_etl_controll']
    brands = collection.find({},{"_id":0, "brand":1})
    ret_collections = []
    for brand in brands:
        col_name = str("tickets_data_crm_"+ brand)
        ret_collections.append(col_name)
    return ret_collections

async def execute_conv_collection_names():
    mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    db = mongo_client['admin']
    collection = db['conv_etl_controll']
    brands = collection.find({},{"_id":0, "brand":1})
    conv_collections = []
    for brand in brands:
        col_name = str("traders_data_crm_"+ brand)
        conv_collections.append(col_name)
    return conv_collections