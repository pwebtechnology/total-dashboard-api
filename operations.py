import json
import math
import logging
import bson
from bson.int64 import Int64
from datetime import datetime, timedelta, date
import numpy as np
from collections import defaultdict
from variables import *
from functions import *
from api import *
from flask import jsonify

async def get_retention_data_compare(props):
    data = await execute_data_from_retention_crm(props)
    date_data = compare_functions(props['startDate'], props['endDate'], props['divider'])
    groupped_data = {}

    for date in date_data:
        item_start, item_end = get_cohort_dates(date)
        current_data = {}
        for row in data:
            affiliate = row['Affiliate']
            STD = row['STD']
            Ticket_Amount_USD = row['Ticket_Amount_USD']
            Ticket_Created_At = row['Ticket_Created_At']
            Ticket_Trader_First_Assigned_Broker = row['Ticket_Trader_First_Assigned_Broker']
            Ticket_Is_ftd = row['Ticket_Is_ftd']
            Ticket_Type = row['Ticket_Type']
            Trader_Ftd_Date = row['Trader_Ftd_Date']
            if isinstance(Trader_Ftd_Date, str):
                Trader_Ftd_Date = datetime.strptime(Trader_Ftd_Date, '%Y-%m-%dT%H:%M:%S.%f')
                if isinstance(Trader_Ftd_Date, Int64):
                    timestamp_seconds = Trader_Ftd_Date / 1000000000
                    Trader_Ftd_Date = datetime.utcfromtimestamp(timestamp_seconds)

            for correctAffilate in affilateException:
                if affiliate in affilateException[correctAffilate]:
                    affiliate = correctAffilate

            if affiliate not in current_data:
                current_data[affiliate] = {
                    'FTDs': 0,
                    'STDs': 0,
                    'Total_WD': 0,
                    'Total_NET': 0,
                    'count_of_withdrawal': 0,
                    'count_of_records': 0,
                    'unassigned': 0
                }

            if is_date(Ticket_Created_At, item_start, item_end):
                current_data[affiliate]['count_of_records'] += 1
                current_data[affiliate]['unassigned'] += 1 if check_unassigned(
                    Ticket_Trader_First_Assigned_Broker) else 0
                current_data[affiliate]['STDs'] += STD if STD != "-" else 0

                if Ticket_Type == "Deposit" and Ticket_Is_ftd != 1:
                    current_data[affiliate]['Total_NET'] += Ticket_Amount_USD

                if Ticket_Type == "Withdrawal":
                    current_data[affiliate]['Total_WD'] += Ticket_Amount_USD
                    current_data[affiliate]['Total_NET'] -= Ticket_Amount_USD
                    current_data[affiliate]['count_of_withdrawal'] += 1

            if is_date(Trader_Ftd_Date, item_start, item_end):
                current_data[affiliate]['FTDs'] += Ticket_Is_ftd

        result = {}
        for affiliate, values in current_data.items():
            result[affiliate] = {}
            is_ftds = bool(values['FTDs'])
            is_records = bool(values['count_of_records'])

            result[affiliate]['WD'] = values['Total_WD']
            result[affiliate]['Net'] = values['Total_NET']
            result[affiliate]['PV'] = values['Total_NET'] / values['FTDs'] if is_ftds else 0
            result[affiliate]['STD Rate'] = values['STDs'] / values['FTDs'] if is_ftds else 0
            result[affiliate]['WD Rate'] = values['count_of_withdrawal'] / values[
                'count_of_records'] if is_records else 0
            result[affiliate]['UnAssigned Tickets'] = values['unassigned'] / values[
                'count_of_records'] if is_records else 0

        groupped_data[date] = result
    return groupped_data

async def get_retention_data_compare_buider(props):
    data = await execute_data_from_retention_crm(props)
    date_data = compare_functions(props['startDate'], props['endDate'], props['divider'])
    groupped_data = {}

    for date in date_data:
        current_data = {}
        for row in data:
            trader_id = row['Trader_ID']
            campaign = row['Campaign_Name']
            STD = row['STD']
            Ticket_Amount_USD = row['Ticket_Amount_USD']
            Ticket_Created_At = row['Ticket_Created_At']
            Ticket_Trader_First_Assigned_Broker = row['Ticket_Trader_First_Assigned_Broker']
            Ticket_Is_ftd = row['Ticket_Is_ftd']
            Ticket_Type = row['Ticket_Type']
            Trader_Ftd_Date = row['Trader_Ftd_Date']
            if isinstance(Trader_Ftd_Date, str):
                Trader_Ftd_Date = datetime.strptime(Trader_Ftd_Date, '%Y-%m-%dT%H:%M:%S.%f')
                if isinstance(Trader_Ftd_Date, Int64):
                    timestamp_seconds = Trader_Ftd_Date / 1000000000
                    Trader_Ftd_Date = datetime.utcfromtimestamp(timestamp_seconds)


            if affiliate not in current_data:
                current_data[trader_id] = {
                    'FTDs': 0,
                    'STDs': 0,
                    'Total_WD': 0,
                    'Total_NET': 0,
                    'count_of_withdrawal': 0,
                    'count_of_records': 0,
                    'unassigned': 0
                }

            if is_date(Ticket_Created_At, item_start, item_end):
                current_data[trader_id]['count_of_records'] += 1
                current_data[trader_id]['unassigned'] += 1 if check_unassigned(
                    Ticket_Trader_First_Assigned_Broker) else 0
                current_data[trader_id]['STDs'] += STD if STD != "-" else 0

                if Ticket_Type == "Deposit" and Ticket_Is_ftd != 1:
                    current_data[trader_id]['Total_NET'] += Ticket_Amount_USD

                if Ticket_Type == "Withdrawal":
                    current_data[trader_id]['Total_WD'] += Ticket_Amount_USD
                    current_data[trader_id]['Total_NET'] -= Ticket_Amount_USD
                    current_data[trader_id]['count_of_withdrawal'] += 1

            if is_date(Trader_Ftd_Date, item_start, item_end):
                current_data[trader_id]['FTDs'] += Ticket_Is_ftd

        result = {}
        for trader_id, values in current_data.items():
            result[trader_id] = {}
            is_ftds = bool(values['FTDs'])
            is_records = bool(values['count_of_records'])

            result[trader_id]['WD'] = values['Total_WD']
            result[trader_id]['Net'] = values['Total_NET']
            result[trader_id]['PV'] = values['Total_NET'] / values['FTDs'] if is_ftds else 0
            result[trader_id]['STD Rate'] = values['STDs'] / values['FTDs'] if is_ftds else 0
            result[trader_id]['WD Rate'] = values['count_of_withdrawal'] / values[
                'count_of_records'] if is_records else 0
            result[trader_id]['UnAssigned Tickets'] = values['unassigned'] / values[
                'count_of_records'] if is_records else 0

        groupped_data[date] = result
    return groupped_data


async def get_conversion_data_compare(props):
    data = await execute_data_from_conversion_crm(props)
    date_data = compare_functions(props['startDate'], props['endDate'], props['divider'])
    groupped_data = {}
    for date in date_data:
        item_start, item_end = get_cohort_dates(date)
        current_data = {}

        for row in data:
            affilate = row['Affiliate']
            Trader_First_assigned_broker = row['Trader_First_assigned_broker']
            Brocker = row['Brocker']
            Trader_Sale_Status = row['Trader_Sale_Status']
            Trader_Is_Ftd = row['Trader_Is_Ftd']
            Trader_Ftd_Date = row['Trader_Ftd_Date']
            Trader_Registered_At = row['Trader_Registered_At']
            Trader_Last_Login = row['Trader_Last_Login'].strftime("%Y-%m-%d %H:%M:%S")

            if affilate not in current_data:
                current_data[affilate] = {
                    'FTDs': 0,
                    'Leads': 0,
                    'na_counters': 0,
                    'unassigned': 0,
                    'pool': 0,
                    'total_calls': 0,
                    'login': 0
                }

            if is_date(Trader_Registered_At, item_start, item_end):
                current_data[affilate]['Leads'] += 1
                current_data[affilate]['total_calls'] += 1 if 'Trader_Phone' in row else 0
                current_data[affilate]['unassigned'] += 1 if check_unassigned(Trader_First_assigned_broker) else 0
                current_data[affilate]['pool'] += 1 if check_unassigned(Brocker) else 0
                current_data[affilate]['na_counters'] += 1 if Trader_Sale_Status in ['No answer 5 UP', 'No answer 1-5'] else 0;
                current_data[affilate]['login'] += 1 if Trader_Last_Login != empty_date else 0

            if is_date(Trader_Ftd_Date, item_start, item_end):
                current_data[affilate]['FTDs'] += Trader_Is_Ftd

        result = {}
        for affilate, values in current_data.items():
            is_leads = bool(values['Leads'])
            result[affilate] = {}
            result[affilate]['Leads'] = values['Leads']
            result[affilate]['FTDs'] = values['FTDs']
            result[affilate]['Calls per FTD'] = round(values['total_calls'] / values['FTDs']) if values['FTDs'] else 0
            result[affilate]['CR'] = get_percent(values['FTDs'] / values['Leads']) if is_leads else 0
            result[affilate]['NA'] = get_percent(values['na_counters'] / values['Leads']) if is_leads else 0
            result[affilate]['AnRate'] = 1 - result[affilate]['NA']
            result[affilate]['UnAssigned Leads'] = get_percent(values['unassigned'] / values['Leads']) if is_leads else 0
            result[affilate]['Pool VS Assigned'] = get_percent(values['pool'] / (
                        values['Leads'] - values['pool'])) if is_leads and (values['Leads'] - values['pool']) != 0 else 0
            result[affilate]['Autologin'] = get_percent(values['login'] / values['Leads']) if is_leads else 0

        groupped_data[date] = result

    return groupped_data

async def get_conversion_data_compare_builder(props):
    data = await execute_data_from_conversion_crm(props)
    date_data = compare_functions(props['startDate'], props['endDate'], props['divider'])
    groupped_data = {}
    for date in date_data:
        item_start, item_end = get_cohort_dates(date)
        current_data = {}

        for row in data:
            trader_id = row['Trader_ID']
            campaign = row['Campaign_campaign_name']
            Trader_First_assigned_broker = row['Trader_First_assigned_broker']
            Brocker = row['Brocker']
            Trader_Sale_Status = row['Trader_Sale_Status']
            Trader_Is_Ftd = row['Trader_Is_Ftd']
            Trader_Ftd_Date = row['Trader_Ftd_Date']
            Trader_Registered_At = row['Trader_Registered_At']
            Trader_Last_Login = row['Trader_Last_Login'].strftime("%Y-%m-%d %H:%M:%S")

            if affilate not in current_data:
                current_data[trader_id] = {
                    'FTDs': 0,
                    'Leads': 0,
                    'na_counters': 0,
                    'unassigned': 0,
                    'pool': 0,
                    'total_calls': 0,
                    'login': 0
                }

            if is_date(Trader_Registered_At, item_start, item_end):
                current_data[trader_id]['Leads'] += 1
                current_data[trader_id]['total_calls'] += 1 if 'Trader_Phone' in row else 0
                current_data[trader_id]['unassigned'] += 1 if check_unassigned(Trader_First_assigned_broker) else 0
                current_data[trader_id]['pool'] += 1 if check_unassigned(Brocker) else 0
                current_data[trader_id]['na_counters'] += 1 if Trader_Sale_Status in ['No answer 5 UP', 'No answer 1-5'] else 0;
                current_data[trader_id]['login'] += 1 if Trader_Last_Login != empty_date else 0

            if is_date(Trader_Ftd_Date, item_start, item_end):
                current_data[trader_id]['FTDs'] += Trader_Is_Ftd

        result = {}
        for trader_id, values in current_data.items():
            is_leads = bool(values['Leads'])
            result[trader_id] = {}
            result[trader_id]['Leads'] = values['Leads']
            result[trader_id]['FTDs'] = values['FTDs']
            result[trader_id]['Calls per FTD'] = round(values['total_calls'] / values['FTDs']) if values['FTDs'] else 0
            result[trader_id]['CR'] = get_percent(values['FTDs'] / values['Leads']) if is_leads else 0
            result[trader_id]['NA'] = get_percent(values['na_counters'] / values['Leads']) if is_leads else 0
            result[trader_id]['AnRate'] = 1 - result[affilate]['NA']
            result[trader_id]['UnAssigned Leads'] = get_percent(values['unassigned'] / values['Leads']) if is_leads else 0
            result[trader_id]['Pool VS Assigned'] = get_percent(values['pool'] / (
                        values['Leads'] - values['pool'])) if is_leads and (values['Leads'] - values['pool']) != 0 else 0
            result[trader_id]['Autologin'] = get_percent(values['login'] / values['Leads']) if is_leads else 0

        groupped_data[date] = result

    return groupped_data



async def get_conversion_data():
    st = time.time()
    data = await execute_data_from_conversion_crm()

    preparedData = defaultdict(lambda: {'FTDs': 0, 'Leads': 0, 'na_counters': 0, 'unassigned': 0, 'pool': 0, 'assigned': 0, 'total_calls': 0, 'login': 0, 'not_login': 0})

    for row in data:
        affilate = row['Affiliate']
        Trader_Is_Ftd = row['Trader_Is_Ftd']
        Trader_First_assigned_broker = row['Trader_First_assigned_broker']
        Brocker = row['Brocker']
        Trader_Sale_Status = row['Trader_Sale_Status']
        Trader_Last_Login = row['Trader_Last_Login'].strftime("%Y-%m-%d %H:%M:%S")

        preparedData[affilate]['Leads'] += 1
        preparedData[affilate]['total_calls'] += 1 if 'Trader_Phone' in row else 0
        preparedData[affilate]['FTDs'] += Trader_Is_Ftd
        preparedData[affilate]['unassigned'] += 1 if check_unassigned(Trader_First_assigned_broker) else 0
        preparedData[affilate]['pool'] += 1 if check_unassigned(Brocker) else 0
        preparedData[affilate]['na_counters'] += Trader_Sale_Status in ['No answer 5 UP', 'No answer 1-5']
        preparedData[affilate]['login'] += 1 if Trader_Last_Login != empty_date else 0

    result = {
        affilate: {
            'FTDs': affilateData['FTDs'],
            'Leads': affilateData['Leads'],
            'Calls per FTD': round(affilateData['total_calls'] / affilateData['FTDs']) if affilateData['FTDs'] else 0,
            'CR': get_percent(affilateData['FTDs'] / affilateData['Leads']) if affilateData['Leads'] else 0,
            'NA': get_percent(affilateData['na_counters'] / affilateData['Leads']) if affilateData['Leads'] else 0,
            'AnRate': get_percent(1 - (affilateData['na_counters'] / affilateData['Leads'])) if affilateData['Leads'] else 0,
            'UnAssigned Leads': get_percent(affilateData['unassigned'] / affilateData['Leads']) if affilateData['Leads'] else 0,
            'Pool Customers VS Assigned': get_percent(affilateData['pool'] / (affilateData['Leads'] - affilateData['pool'])) if (affilateData['Leads'] - affilateData['pool']) else 0,
            'Autologin': get_percent(affilateData['login'] / affilateData['Leads']) if affilateData['Leads'] else 0,
            'Login': affilateData['login'],
            'NA Counters': affilateData['na_counters']
        }
        for affilate, affilateData in preparedData.items()
    }

    return result

async def get_conversion_data_builder(props):
    st = time.time()
    data, total_count = await execute_data_from_conversion_crm_builder(props)
    dimentions = props.get('dimentions',['Trader_ID'])
    metrics = props.get('metrics',[])
    preparedData = defaultdict(lambda: {metrics: 0 for metric in metrics})


    for row in data:
        key = tuple(row[dim] for dim in dimentions)
        for metric in metrics:
            if metric == '#Leads':
                preparedData[key][metric] += 1
            elif metric == '#FTDs' :
                preparedData[key][metric] += row.get('Trader_Is_Ftd', 0)
            elif metric == '$FTDs' :
                preparedData[key][metric] += row.get('Ticket_Amount_USD',0) if row.get('Trader_Is_Ftd') else 0
            elif metric == '#std':
                preparedData[key][metric] += row.get('STD',0)
            elif metric == '$std':
                preparedData[key][metric] += row.get('Ticket_Amount_USD',0) if row.get('STD') else 0
            elif metric == '#rdp':
                if row.get('Ticket_Type') == "Deposit" and  row.get('Trader_Is_Ftd') == 0:
                    preparedData[key][metric] += 1
            elif metric == '$rdp':
                if row.get('Ticket_Type') == "Deposit" and row.get('Trader_Is_Ftd') == 0:
                    preparedData[key][metric] += row.get('Ticket_Amount_USD',0)
            elif metric == '$Total_deposit':
                if row.get('Ticket_Type') == "Deposit":
                    preparedData[key][metric] += row.get('Ticket_Amount_USD',0)
            elif metric == '$WD':
                if row.get('Ticket_Type') == "Withdrawal":
                    preparedData[key][metric] += row.get('Ticket_Amount_USD',0)
            elif metric == '$Net':
                if row.get('Ticket_Type') == "Deposit":
                    preparedData[key]['$Total_deposit'] += row.get('Ticket_Amount_USD',0)
                if row.get('Ticket_Type') == "Withdrawal":
                    preparedData[key]['$WD'] += row.get('Ticket_Amount_USD',0)
                preparedData[key][metric] = preparedData[key]['$Total_deposit'] - preparedData[key]['$WD']
            elif metric == 'PV':
                if row.get('Ticket_Type') == "Deposit":
                    preparedData[key]['$Total_deposit'] += row.get('Ticket_Amount_USD', 0)
                if row.get('Ticket_Type') == "Withdrawal":
                    preparedData[key]['$WD'] += row.get('Ticket_Amount_USD', 0)
                preparedData[key]['$Net'] = preparedData[key]['$Total_deposit'] - preparedData[key]['$WD']
                preparedData[key]['#FTDs'] = max(preparedData[key]['#FTDs'], 1)
                preparedData[key][metric] = preparedData[key]['$Net'] / preparedData[key]['#FTDs']
            elif metric == 'STD_rate%':
                preparedData[key]['#std'] = max(preparedData[key]['#std'], 1)
                preparedData[key][metric] = get_percent(preparedData[key]['#std'] / preparedData[key]['#FTDs'])
            elif metric == 'CR%':
                preparedData[key][metric] = get_percent(preparedData[key]['#FTDs'] / preparedData[key]['#Leads'])
            elif metric == 'InCR%':
                reg_month = row.get('Trader_Registered_At').month if row.get('Trader_Registered_At') else None
                ftd_month = row.get('Trader_Ftd_Date').month if row.get('Trader_Ftd_Date') else None
                if reg_month == ftd_month:
                    preparedData[key][metric] = get_percent(preparedData[key]['#FTDs'] / preparedData[key]['#Leads'])
            elif metric == 'InTRV$':
                created_month = row.get('Ticket_Created_At').month if row.get('Ticket_Created_At') else None
                ftd_month = row.get('Trader_Ftd_Date').month if row.get('Trader_Ftd_Date') else None
                if created_month == ftd_month:
                    preparedData[key][metric] = preparedData[key]['$Net'] / preparedData[key]['#FTD']
            elif metric == 'NA%':
                if row.get('Trader_Sale_Status') in ['No answer 5 UP', 'No answer 1-5'] :
                    preparedData[key]['NA_Count'] += 1
                preparedData[key][metric] = get_percent(preparedData[key]['NA_Count'] / preparedData[key]['#Leads'])
            elif metric == 'Autologin%':
                if row.get('Trader_Last_Login')  :
                    preparedData[key]['Autologin_Count'] += 1
                preparedData[key][metric] = get_percent(preparedData[key]['Autologin_Count'] / preparedData[key]['#Leads'])
            elif metric == 'CallAgain%':
                if row.get('Trader_Sale_Status') == 'Call Again' :
                    preparedData[key]['CallAgain_Count'] += 1
                preparedData[key][metric] = get_percent(preparedData[key]['CallAgain_Count'] / preparedData[key]['#Leads'])
            elif metric == 'CallBack%':
                if row.get('Trader_Sale_Status') == 'Call Back' :
                    preparedData[key]['CallBack_Count'] += 1
                preparedData[key][metric] = get_percent(preparedData[key]['CallBack_Count'] / preparedData[key]['#Leads'])
    result = {
        '_'.join(map(str, key)): {**traderData , **{dim: key[i] for i, dim in enumerate(dimentions)}}
        for key, traderData in preparedData.items()
    }
    return {'result': result, 'total_count': total_count}



async def get_retention_data():
    st = time.time()
    result = {}
    data = await execute_data_from_retention_crm()
    preparedData = {}

    for row in data:
        affilate = row['Affiliate']
        for correctAffilate in affilateException:
            if affilate in affilateException[correctAffilate]:
                affilate = correctAffilate

        if affilate not in preparedData:
            preparedData[affilate] = {
                'FTDs': 0,
                'STDs': 0,
                'Total_WD': 0,
                'Total_NET': 0,
                'count_of_withdrawal': 0,
                'count_of_records': 0,
                'unassigned': 0,
            }
        preparedData[affilate]['count_of_records'] += 1
        preparedData[affilate]['FTDs'] += row['Ticket_Is_ftd']
        preparedData[affilate]['STDs'] += row['STD'] if row['STD'] != "-" else 0
        preparedData[affilate]['unassigned'] += 1 if check_unassigned(row['Ticket_Trader_First_Assigned_Broker']) else 0

        if row['Ticket_Type'] == "Deposit" and row['Ticket_Is_ftd'] != 1:
            preparedData[affilate]['Total_NET'] += row['Ticket_Amount_USD']

        if row['Ticket_Type'] == "Withdrawal":
            preparedData[affilate]['Total_WD'] += row['Ticket_Amount_USD']
            preparedData[affilate]['Total_NET'] -= row['Ticket_Amount_USD']
            preparedData[affilate]['count_of_withdrawal'] += 1

    for affilate, affilateData in preparedData.items():
        result[affilate] = {}
        isFtds = bool(affilateData['FTDs'])
        isRecords = bool(affilateData['count_of_records'])
        result[affilate]['unassigned'] = affilateData['unassigned']
        result[affilate]['Total_WD'] = affilateData['Total_WD']
        result[affilate]['Total_NET'] = affilateData['Total_NET']
        result[affilate]['STDs'] = affilateData['STDs']
        result[affilate]['PV'] = affilateData['Total_NET'] / affilateData['FTDs'] if isFtds else 0
        result[affilate]['STD_Rate'] = affilateData['STDs'] / affilateData['FTDs'] if isFtds else 0
        result[affilate]['WD_Rate'] = affilateData['count_of_withdrawal'] / affilateData[
            'count_of_records'] if isRecords else 0
        result[affilate]['UnAssigned_Tickets'] = affilateData['unassigned'] / affilateData[
            'count_of_records'] if isRecords else 0

    return result

async def get_retention_data_builder(props):
    st = time.time()
    data, total_count = await execute_data_from_conversion_crm_builder(props)
    dimentions = props.get('dimentions', ['Trader_ID'])
    metrics = props.get('metrics', [])
    preparedData = defaultdict(lambda: {metrics: 0 for metric in metrics})

    for row in data:
        key = tuple(row[dim] for dim in dimentions)
        for metric in metrics:
            if metric == '#Leads':
                preparedData[key][metric] += 1
            elif metric == '#FTDs':
                preparedData[key][metric] += row.get('Trader_Is_Ftd', 0)
            elif metric == '$FTDs':
                preparedData[key][metric] += row.get('Ticket_Amount_USD', 0) if row.get('Trader_Is_Ftd') else 0
            elif metric == '#std':
                preparedData[key][metric] += row.get('STD', 0)
            elif metric == '$std':
                preparedData[key][metric] += row.get('Ticket_Amount_USD', 0) if row.get('STD') else 0
            elif metric == '#rdp':
                if row.get('Ticket_Type') == "Deposit" and row.get('Trader_Is_Ftd') == 0:
                    preparedData[key][metric] += 1
            elif metric == '$rdp':
                if row.get('Ticket_Type') == "Deposit" and row.get('Trader_Is_Ftd') == 0:
                    preparedData[key][metric] += row.get('Ticket_Amount_USD', 0)
            elif metric == '$Total_deposit':
                if row.get('Ticket_Type') == "Deposit":
                    preparedData[key][metric] += row.get('Ticket_Amount_USD', 0)
            elif metric == '$WD':
                if row.get('Ticket_Type') == "Withdrawal":
                    preparedData[key][metric] += row.get('Ticket_Amount_USD', 0)
            elif metric == '$Net':
                if row.get('Ticket_Type') == "Deposit":
                    preparedData[key]['$Total_deposit'] += row.get('Ticket_Amount_USD', 0)
                if row.get('Ticket_Type') == "Withdrawal":
                    preparedData[key]['$WD'] += row.get('Ticket_Amount_USD', 0)
                preparedData[key][metric] = preparedData[key]['$Total_deposit'] - preparedData[key]['$WD']
            elif metric == 'PV':
                if row.get('Ticket_Type') == "Deposit":
                    preparedData[key]['$Total_deposit'] += row.get('Ticket_Amount_USD', 0)
                if row.get('Ticket_Type') == "Withdrawal":
                    preparedData[key]['$WD'] += row.get('Ticket_Amount_USD', 0)
                preparedData[key]['$Net'] = preparedData[key]['$Total_deposit'] - preparedData[key]['$WD']
                preparedData[key]['#FTDs'] = max(preparedData[key]['#FTDs'], 1)
                preparedData[key][metric] = preparedData[key]['$Net'] / preparedData[key]['#FTDs']
            elif metric == 'STD_rate%':
                preparedData[key]['#std'] = max(preparedData[key]['#std'], 1)
                preparedData[key][metric] = get_percent(preparedData[key]['#std'] / preparedData[key]['#FTDs'])
            elif metric == 'CR%':
                preparedData[key][metric] = get_percent(preparedData[key]['#FTDs'] / preparedData[key]['#Leads'])
            elif metric == 'InCR%':
                reg_month = row.get('Trader_Registered_At').month if row.get('Trader_Registered_At') else None
                ftd_month = row.get('Trader_Ftd_Date').month if row.get('Trader_Ftd_Date') else None
                if reg_month == ftd_month:
                    preparedData[key][metric] = get_percent(preparedData[key]['#FTDs'] / preparedData[key]['#Leads'])
            elif metric == 'InTRV$':
                created_month = row.get('Ticket_Created_At').month if row.get('Ticket_Created_At') else None
                ftd_month = row.get('Trader_Ftd_Date').month if row.get('Trader_Ftd_Date') else None
                if created_month == ftd_month:
                    preparedData[key][metric] = preparedData[key]['$Net'] / preparedData[key]['#FTD']
            elif metric == 'NA%':
                if row.get('Trader_Sale_Status') in ['No answer 5 UP', 'No answer 1-5']:
                    preparedData[key]['NA_Count'] += 1
                preparedData[key][metric] = get_percent(preparedData[key]['NA_Count'] / preparedData[key]['#Leads'])
            elif metric == 'Autologin%':
                if row.get('Trader_Last_Login'):
                    preparedData[key]['Autologin_Count'] += 1
                preparedData[key][metric] = get_percent(
                    preparedData[key]['Autologin_Count'] / preparedData[key]['#Leads'])
            elif metric == 'CallAgain%':
                if row.get('Trader_Sale_Status') == 'Call Again':
                    preparedData[key]['CallAgain_Count'] += 1
                preparedData[key][metric] = get_percent(
                    preparedData[key]['CallAgain_Count'] / preparedData[key]['#Leads'])
            elif metric == 'CallBack%':
                if row.get('Trader_Sale_Status') == 'Call Back':
                    preparedData[key]['CallBack_Count'] += 1
                preparedData[key][metric] = get_percent(
                    preparedData[key]['CallBack_Count'] / preparedData[key]['#Leads'])
    result = {
        '_'.join(map(str, key)): {**traderData, **{dim: key[i] for i, dim in enumerate(dimentions)}}
        for key, traderData in preparedData.items()
    }
    return {'result': result, 'total_count': total_count}


async def get_conversion_data_prev_day():
    data = await execute_data_from_conversion_crm_prev_day()
    preparedData = {}

    for row in data:
        affilate = row['Affiliate']
        Trader_Is_Ftd = row['Trader_Is_Ftd']
        Trader_First_assigned_broker = row['Trader_First_assigned_broker']
        Brocker = row['Brocker']
        Trader_Sale_Status = row['Trader_Sale_Status']
        Trader_Last_Login = row['Trader_Last_Login'].strftime("%Y-%m-%d %H:%M:%S")
        Trader_Ftd_Date = row['Trader_Ftd_Date']
        if isinstance(Trader_Ftd_Date, Int64):
            timestamp_seconds = Trader_Ftd_Date / 1000000000
            Trader_Ftd_Date = datetime.utcfromtimestamp(timestamp_seconds)
        elif isinstance(Trader_Ftd_Date, str):
            Trader_Ftd_Date = datetime.strptime(Trader_Ftd_Date, '%Y-%m-%d %H:%M:%S')
        else:
            pass
        Trader_Registered_At = row['Trader_Registered_At'].strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(Trader_Registered_At, Int64):
            timestamp_seconds = Trader_Registered_At / 1000000000
            Trader_Registered_At = datetime.utcfromtimestamp(timestamp_seconds)
        elif isinstance(Trader_Registered_At, str):
            Trader_Registered_At = datetime.strptime(Trader_Registered_At, '%Y-%m-%d %H:%M:%S')
        else:
            pass

        if affilate not in preparedData:
            preparedData[affilate] = {
                'FTDs': 0,
                'Leads': 0,
                'na_counters': 0,
                'unassigned': 0,
                'pool': 0,
                'assigned': 0,
                'total_calls': 0,
                'login': 0,
                'not_login': 0,
            }

        affiliateData = preparedData[affilate]
        if Trader_Registered_At < previous_day_date:
            affiliateData['Leads'] += 1
            affiliateData['total_calls'] += 1 if 'Trader_Phone' in row else 0
            affiliateData['unassigned'] += 1 if check_unassigned(Trader_First_assigned_broker) else 0
            affiliateData['pool'] += 1 if check_unassigned(Brocker) else 0
            affiliateData['na_counters'] += Trader_Sale_Status in ['No answer 5 UP', 'No answer 1-5']
            affiliateData['login'] += 1 if Trader_Last_Login != empty_date else 0

        if Trader_Ftd_Date < previous_day_date:
            affiliateData['FTDs'] += Trader_Is_Ftd

    result = {}
    for affilate, affilateData in preparedData.items():
        FTDs = affilateData['FTDs']
        Leads = affilateData['Leads']
        total_calls = affilateData['total_calls']
        na_counters = affilateData['na_counters']
        unassigned = affilateData['unassigned']
        pool = affilateData['pool']
        login = affilateData['login']

        isLeads = bool(Leads)
        naRate = na_counters / Leads if isLeads else 0

        result[affilate] = {
            'FTDs': FTDs,
            'Leads': Leads,
            'Calls per FTD': round(total_calls / FTDs) if FTDs else 0,
            'CR': get_percent(FTDs / Leads) if isLeads else 0,
            'NA': get_percent(naRate),
            'AnRate': get_percent(1 - naRate),
            'UnAssigned Leads': get_percent(unassigned / Leads) if isLeads else 0,
            'Pool Customers VS Assigned': get_percent(pool / (Leads - pool)) if (Leads - pool) else 0,
            'Autologin': get_percent(login / Leads) if isLeads else 0,
            'Login': login,
            'NA Counters': na_counters,
        }

    return result

async def get_retention_data_prev_day():
    result = {}
    data = await execute_data_from_retention_crm_prev_day()
    preparedData = {}

    for row in data:
        affilate = row['Affiliate']
        Trader_Ftd_Date = row['Trader_Ftd_Date']
        if isinstance(Trader_Ftd_Date, Int64):
            timestamp_seconds = Trader_Ftd_Date / 1000000000
            Trader_Ftd_Date = datetime.utcfromtimestamp(timestamp_seconds)
        elif isinstance(Trader_Ftd_Date, str):
            Trader_Ftd_Date = Trader_Ftd_Date[:-1]
            Trader_Ftd_Date = datetime.strptime(Trader_Ftd_Date, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            pass
        Ticket_Created_At = row['Ticket_Created_At']
        for correctAffilate in affilateException:
            if affilate in affilateException[correctAffilate]:
                affilate = correctAffilate

        if affilate not in preparedData:
            preparedData[affilate] = {
                'FTDs': 0,
                'STDs': 0,
                'Total_WD': 0,
                'Total_NET': 0,
                'count_of_withdrawal': 0,
                'count_of_records': 0,
                'unassigned': 0,
            }

        if (Ticket_Created_At < previous_day_date):
            preparedData[affilate]['count_of_records'] += 1
            preparedData[affilate]['unassigned'] += 1 if check_unassigned(row['Ticket_Trader_First_Assigned_Broker']) else 0
            preparedData[affilate]['STDs'] += row['STD'] if row['STD'] != "-" else 0

            if row['Ticket_Type'] == "Deposit" and row['Ticket_Is_ftd'] != 1:
                preparedData[affilate]['Total_NET'] += row['Ticket_Amount_USD']

            if row['Ticket_Type'] == "Withdrawal":
                preparedData[affilate]['Total_WD'] += row['Ticket_Amount_USD']
                preparedData[affilate]['Total_NET'] -= row['Ticket_Amount_USD']
                preparedData[affilate]['count_of_withdrawal'] += 1
        if Trader_Ftd_Date is not None and isinstance(Trader_Ftd_Date, datetime):
            if (Trader_Ftd_Date < previous_day_date):
                preparedData[affilate]['FTDs'] += row['Ticket_Is_ftd']
        else: pass

    for affilate, affilateData in preparedData.items():
        result[affilate] = {}
        isFtds = bool(affilateData['FTDs'])
        isRecords = bool(affilateData['count_of_records'])
        result[affilate]['unassigned'] = affilateData['unassigned']
        result[affilate]['Total_WD'] = affilateData['Total_WD']
        result[affilate]['Total_NET'] = affilateData['Total_NET']
        result[affilate]['STDs'] = affilateData['STDs']
        result[affilate]['PV'] = affilateData['Total_NET'] / affilateData['FTDs'] if isFtds else 0
        result[affilate]['STD_Rate'] = affilateData['STDs'] / affilateData['FTDs'] if isFtds else 0
        result[affilate]['WD_Rate'] = affilateData['count_of_withdrawal'] / affilateData[
            'count_of_records'] if isRecords else 0
        result[affilate]['UnAssigned_Tickets'] = affilateData['unassigned'] / affilateData[
            'count_of_records'] if isRecords else 0

    return result

async def getTotalAffilatesDataCompare(props):
    ret, conv, paymentAnswers = await asyncio.gather(
        get_retention_data_compare(props),
        get_conversion_data_compare(props),
        execute_data_from_payment(props)
    )

    result = {}
    for date in conv:
        startCohort, endCohort = get_cohort_dates(date)
        result[date] = []
        # startCohort = np.datetime64(startCohort)
        # endCohort = np.datetime64(endCohort)
        for affiliate in conv[date]:
            retAffiliate = ret[date][affiliate]

            trafficCost = sum(
                float(item["payment"])
                for item in paymentAnswers
                if item['affiliate'] == affiliate and is_date(to_date(item['date'], utcDateFormat), startCohort, endCohort)
            )

            Net = retAffiliate['Net'] if retAffiliate else 0
            WD = retAffiliate['WD'] if retAffiliate else 0
            PV = retAffiliate['PV'] if retAffiliate else 0
            STD_Rate = retAffiliate['STD Rate'] if retAffiliate else 0
            WD_Rate = retAffiliate['WD Rate'] if retAffiliate else 0
            UnAssigned_Tickets = retAffiliate['UnAssigned Tickets'] if retAffiliate else 0
            FTDs = conv[date][affiliate]['FTDs']
            ROMI = (Net - trafficCost) / trafficCost if trafficCost else 0

            CPA = trafficCost / FTDs if FTDs else 0

            result[date].append({
                'Affiliate': affiliate,
                **conv[date][affiliate],
                'Net': Net,
                'WD': WD,
                'PV': round(PV),
                'STD Rate': STD_Rate,
                'ROMI': ROMI,
                'WD Rate': WD_Rate,
                'UnAssigned Tickets': UnAssigned_Tickets,
                'CPA actual': CPA
            })

        result[date].sort(key=lambda x: x['Affiliate'], reverse=True)

    return json.dumps(result)

async def get_total_affiliates_data():
    st = time.time()
    ret, conv, payment_answers = await asyncio.gather(
        get_retention_data(),
        get_conversion_data(),
        execute_data_from_payment()
    )

    result = []
    for affilate, data in conv.items():
        payment = next((row for row in payment_answers if row['affiliate'] == affilate), None)
        traffic_cost = payment['payment'] if payment else 0
        ret_affiliate = ret.get(affilate, None)
        Net = ret_affiliate['Total_NET'] if ret_affiliate else 0
        WD = ret_affiliate['Total_WD'] if ret_affiliate else 0
        PV = ret_affiliate['PV'] if ret_affiliate else 0
        STDs = ret_affiliate['STDs'] if ret_affiliate else 0
        STD_Rate = ret_affiliate['STD_Rate'] if ret_affiliate else 0
        WD_Rate = ret_affiliate['WD_Rate'] if ret_affiliate else 0
        UnAssigned_Tickets = ret_affiliate['UnAssigned_Tickets'] if ret_affiliate else 0
        FTDs = data.get('FTDs')
        ROMI = (Net - traffic_cost) / traffic_cost if traffic_cost else 0
        CPA = traffic_cost / FTDs if FTDs else 0

        result.append({
            'Affiliate': affilate,
            **data,
            'Net': round(Net),
            'WD': WD,
            'PV': round(PV),
            'STDs': STDs,
            'STD Rate': get_percent(STD_Rate),
            'ROMI': get_percent(ROMI),
            'WD Rate': get_percent(WD_Rate),
            'UnAssigned Tickets': get_percent(UnAssigned_Tickets),
            'CPA actual': round(CPA),
        })

    result.sort(key=lambda x: x['FTDs'], reverse=True)
    nd = time.time()

    return json.dumps(result)

async def get_total_affiliates_data_prev_day():
    st = time.time()
    ret, conv, payment_answers = await asyncio.gather(
        get_retention_data_prev_day(),
        get_conversion_data_prev_day(),
        execute_data_from_payment_prev_day()
    )

    result = []
    for affilate, data in conv.items():
        payment = next((row for row in payment_answers if row['affiliate'] == affilate), None)
        traffic_cost = payment['payment'] if payment else 0
        ret_affiliate = ret.get(affilate, None)
        Net = ret_affiliate['Total_NET'] if ret_affiliate else 0
        WD = ret_affiliate['Total_WD'] if ret_affiliate else 0
        PV = ret_affiliate['PV'] if ret_affiliate else 0
        STDs = ret_affiliate['STDs'] if ret_affiliate else 0
        STD_Rate = ret_affiliate['STD_Rate'] if ret_affiliate else 0
        WD_Rate = ret_affiliate['WD_Rate'] if ret_affiliate else 0
        UnAssigned_Tickets = ret_affiliate['UnAssigned_Tickets'] if ret_affiliate else 0
        FTDs = data.get('FTDs')
        ROMI = (Net - traffic_cost) / traffic_cost if traffic_cost else 0
        CPA = traffic_cost / FTDs if FTDs else 0

        result.append({
            'Affiliate': affilate,
            **data,
            'Net': round(Net),
            'WD': WD,
            'PV': round(PV),
            'STDs': STDs,
            'STD Rate': get_percent(STD_Rate),
            'ROMI': get_percent(ROMI),
            'WD Rate': get_percent(WD_Rate),
            'UnAssigned Tickets': get_percent(UnAssigned_Tickets),
            'CPA actual': round(CPA),
        })

    result.sort(key=lambda x: x['FTDs'], reverse=True)
    nd = time.time()

    return json.dumps(result)

async def get_total_builder_data(props):
    st = time.time()
    ret, conv = await asyncio.gather(
        get_retention_data_builder(props),
        get_conversion_data_builder(props),
    )
    total_count = ret['total_count'] + conv['total_count']
    result = []
    for trader_id, data in conv['result'].items():
        ret_trader = ret['result'].get(trader_id, None)
        Net = ret_trader['Total_NET'] if ret_trader else 0
        WD = ret_trader['Total_WD'] if ret_trader else 0
        PV = ret_trader['PV'] if ret_trader else 0
        STDs = ret_trader['STDs'] if ret_trader else 0
        STD_Rate = ret_trader['STD_Rate'] if ret_trader else 0
        WD_Rate = ret_trader['WD_Rate']  if ret_trader else 0
        UnAssigned_Tickets = ret_trader['UnAssigned_Tickets'] if ret_trader else 0
        FTDs = data.get('#FTDs')

        result.append({
            'Trader': trader_id,
            **data,
            'Net': round(Net),
            'WD': WD,
            'PV': round(PV),
            'STDs': STDs,
            'STD Rate': get_percent(STD_Rate),
            'WD Rate': get_percent(WD_Rate),
            'UnAssigned Tickets': get_percent(UnAssigned_Tickets),
        })

    result.sort(key=lambda x: x['#FTDs'], reverse=True)
    page_size = int(props['pageSize'])
    page = int(props['pageIndex'])
    # Pagination logic
    total_items = len(result)
    total_pages = math.ceil(total_items / page_size)

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_data = result[start_index:end_index]

    response_payload = {
        'records': paginated_data,
        'pagination': {
            'pageIndex': page,
            'pageSize': page_size,
            'total_items': total_count,
            'total_pages': total_pages
        }
    }

    nd = time.time()

    return response_payload


async def get_conversion_data_builder_full(props):
    return await execute_data_from_conversion_crm_builder(props)

async def get_retention_data_builder_full(props):
    return await execute_data_from_retention_crm_builder(props)
async def get_total_builder_data_props(props):
    st = time.time()
    ret_data_future = get_retention_data_builder_full(props)
    conv_data_future = get_conversion_data_builder_full(props)

    ret_data_result, conv_data_result = await asyncio.gather(ret_data_future, conv_data_future)

    ret_data = ret_data_result['data']
    conv_data = conv_data_result['data']
    print(conv_data)
    logging.debug(conv_data)
    total_count = max(ret_data_result['total_count'], conv_data_result['total_count'])
    logging.debug(props)
    dimensions = props.get('dimentions',['Customer_ID'])
    metrics = props.get('metrics', 'FTDs')
    combined_data = merge_data(conv_data, ret_data)
    prepared_data = defaultdict(lambda: {metric: 0 for metric in metrics})
    #print(conv_data)
    #logging.debug(conv_data)
    for row in combined_data:
        key = tuple(row.get(dim) for dim in dimensions)

        if key not in prepared_data:
            prepared_data[key] = {metric: 0 for metric in metrics}
            for dim in dimensions:
                prepared_data[key][dim] = row.get(dim)
        for metric in metrics:
            if metric == 'Leads':
                prepared_data[key][metric] += 1
            elif metric == 'FTDs':
                logging.debug(f"Here is metric FTDs")
                prepared_data[key][metric] += row.get('Trader_Is_Ftd', 0)
            elif metric == 'FTD_Sum':
                print(row.get('Ticket_Amount_USD', 0))
                logging.debug(row.get('Ticket_Amount_USD', 0))
                prepared_data[key][metric] += int(row.get('Ticket_Amount_USD', 0)) if row.get('Trader_Is_Ftd') else 0
            elif metric == 'std':
                prepared_data[key][metric] += row.get('STD', 0)
            elif metric == 'std_sum':
                prepared_data[key][metric] += int(row.get('Ticket_Amount_USD', 0)) if row.get('STD') else 0
            elif metric == 'rdp':
                if row.get('Ticket_Type') == "Deposit" and row.get('Trader_Is_Ftd') == 0:
                    prepared_data[key][metric] += 1
            elif metric == 'rdp_sum':
                if row.get('Ticket_Type') == "Deposit" and row.get('Trader_Is_Ftd') == 0:
                    prepared_data[key][metric] += int(row.get('Ticket_Amount_USD'))
            elif metric == 'Total_deposit':
                if row.get('Ticket_Type') == "Deposit":
                    prepared_data[key][metric] += int(row.get('Ticket_Amount_USD'))
            elif metric == 'WD':
                if row.get('Ticket_Type') == "Withdrawal":
                    prepared_data[key][metric] += int(row.get('Ticket_Amount_USD'))
            elif metric == 'Net':
                if row.get('Ticket_Type') == "Deposit":
                    prepared_data[key]['Total_deposit'] += int(row.get('Ticket_Amount_USD'))
                if row.get('Ticket_Type') == "Withdrawal":
                    prepared_data[key]['WD'] += int(row.get('Ticket_Amount_USD'))
                prepared_data[key][metric] = prepared_data[key]['Total_deposit'] - prepared_data[key]['WD']
            elif metric == 'PV':
                if row.get('Ticket_Type') == "Deposit":
                    prepared_data[key]['Total_deposit'] += int(row.get('Ticket_Amount_USD', 0))
                if row.get('Ticket_Type') == "Withdrawal":
                    prepared_data[key]['WD'] += int(row.get('Ticket_Amount_USD', 0))
                prepared_data[key]['Net'] = prepared_data[key]['Total_deposit'] - prepared_data[key]['WD']
                prepared_data[key]['FTDs'] = max(prepared_data[key]['FTDs'], 1)
                prepared_data[key][metric] = prepared_data[key]['Net'] / prepared_data[key]['FTDs']
            elif metric == 'STD_rate':
                prepared_data[key]['std'] = max(prepared_data[key]['std'], 1)
                prepared_data[key][metric] = get_percent(prepared_data[key]['std'] / prepared_data[key]['FTDs'])
            elif metric == 'CR':
                prepared_data[key][metric] = get_percent(prepared_data[key]['FTDs'] / prepared_data[key]['Leads'])
            elif metric == 'InCR':
                reg_month = row.get('Trader_Registered_At').month if row.get('Trader_Registered_At') else None
                ftd_month = row.get('Trader_Ftd_Date').month if row.get('Trader_Ftd_Date') else None
                if reg_month == ftd_month:
                    prepared_data[key][metric] = get_percent(prepared_data[key]['FTDs'] / prepared_data[key]['Leads'])
            elif metric == 'InTRV':
                created_month = row.get('Ticket_Created_At').month if row.get('Ticket_Created_At') else None
                ftd_month = row.get('Trader_Ftd_Date').month if row.get('Trader_Ftd_Date') else None
                if created_month == ftd_month:
                    prepared_data[key][metric] = prepared_data[key]['Net'] / prepared_data[key]['FTDs']
            elif metric == 'NA':
                if row.get('Trader_Sale_Status') in ['No answer 5 UP', 'No answer 1-5']:
                    prepared_data[key]['NA_Count'] += 1
                prepared_data[key][metric] = get_percent(prepared_data[key]['NA_Count'] / prepared_data[key]['Leads'])
            elif metric == 'Autologin':
                if row.get('Trader_Last_Login'):
                    prepared_data[key]['Autologin_Count'] += 1
                prepared_data[key][metric] = get_percent(prepared_data[key]['Autologin_Count'] / prepared_data[key]['Leads'])
            elif metric == 'CallAgain':
                if row.get('Trader_Sale_Status') == 'Call Again':
                    prepared_data[key]['CallAgain_Count'] += 1
                prepared_data[key][metric] = get_percent(prepared_data[key]['CallAgain_Count'] / prepared_data[key]['Leads'])
            elif metric == 'CallBack':
                if row.get('Trader_Sale_Status') == 'Call Back':
                    prepared_data[key]['CallBack_Count'] += 1
                prepared_data[key][metric] = get_percent(prepared_data[key]['CallBack_Count'] / prepared_data[key]['Leads'])

    result = [
        {**trader_data, **{dim: key[i] for i, dim in enumerate(dimensions)}}
        for key, trader_data in prepared_data.items()
    ]

    total_count = len(result)
    page_index = props.get('pageIndex', 0)
    page_size = props.get('pageSize', 20)
    start = page_index * page_size
    end = start + page_size

    paginated_result = result[start:end]
    print("paginated result : ", paginated_result)
    print("=============================================================================================================")


    return ({
        'pagination': {
            'pageIndex': page_index,
            'pageSize': page_size,
            'total_items': total_count,
            'total_pages': round(total_count/page_size,0)
        },
        'records': result
    })


