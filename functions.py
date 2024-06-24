import numpy as np
import datetime
from datetime import datetime
from variables import *


def is_date(date, start, end):
    def parse_date(date_str):
        if date_str == 'Empty':
            return datetime(1, 1, 1)
        elif isinstance(date_str, str):
            formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    pass
            raise ValueError("Could not parse date: {}".format(date_str))
        else:
            return date_str
    start_dt = parse_date(start)
    end_dt = parse_date(end)
    date_dt = parse_date(date)
    return start_dt <= date_dt <= end_dt

def to_date(date_str, format):
    return datetime.strptime(date_str, format)

async def connect_to_mongo():
    uri = "mongodb://NikKimp:NikKimp@172.23.2.15:27017/?tls=false&authMechanism=DEFAULT"
    client = MongoClient(uri, server_api=ServerApi('1'))
    return client

def check_unassigned(property):
    return not property or property in unassignedStages or 'pool' in property.lower() or 'crm' in property.lower()

def get_cohort_dates(date):
    return [to_date(date_str, rev_format) for date_str in date.split(' - ')]

def compare_functions(start, end, divider):
    start_date = np.datetime64(start)
    end_date = np.datetime64(end)

    if divider == 'day':
        delta = np.timedelta64(1, 'D')
    elif divider == 'week':
        delta = np.timedelta64(7, 'D')
    elif divider == 'month':
        delta = np.timedelta64(30, 'D')
    elif divider == 'quarter':
        delta = np.timedelta64(90, 'D')
    elif divider == 'year':
        delta = np.timedelta64(365, 'D')
    else:
        raise ValueError('Invalid divider')

    current_start_date = start_date
    current_end_date = current_start_date + delta

    cohorts_result = []

    while current_end_date <= end_date:
        cohorts_result.append({
            'start': current_start_date.astype(object).strftime(rev_format),
            'end': current_end_date.astype(object).strftime(rev_format)
        })

        current_start_date += delta

        if current_end_date == end_date:
            break
        elif current_end_date + delta > end_date:
            current_end_date = end_date
        else:
            current_end_date += delta

    return [f"{row['start']} - {row['end']}" for row in cohorts_result]

def get_percent(number):
    return round(number * 10000) / 100;


def merge_data(conv_data, ret_data):
    # Convert conv_data to a dictionary keyed by Customer_ID for fast lookup
    print("conv data:",conv_data)
    print("ret data:", ret_data)
    conv_data_dict = {item['Trader_Email']: item for item in conv_data}

    merged_data = []

    for ret_item in ret_data:
        customer_id = ret_item['Trader_Email']

        # Look for the corresponding item in conv_data
        conv_item = conv_data_dict.get(customer_id, {})

        # Merge the two dictionaries, with ret_item taking precedence
        merged_item = {**ret_item, **conv_item}

        merged_data.append(merged_item)

    return merged_data
