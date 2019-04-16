#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 13:01:16 2018

@author: frank
"""

import requests
import json

from utils import str2dict, list2dict, post, get

def btc_accounts(minconf=''):
    fname = 'btc/listaccounts'
    params = {'minconf':minconf}
    res = get(fname,params)
    if res.status_code != 200:
        return []
    res_dict = str2dict(res.text)
    if res_dict['success'] == 'false' or \
       'data' not in res_dict.keys():
        return []
    return list(list2dict(res_dict['data']).keys())

def btc_transactions_all(accounts):
    transactions = []
    for account in accounts:
        transactions += btc_transactions(account)
    return  [transaction for transaction in transactions if transaction]
    
def btc_transactions(account='',
                     count=10,
                     skips=0):
    fname = 'btc/listtransactions'
    params = {
                'account':account,
                'count':count,
                'from':skips
             }
    res = post(fname,params)
    if res.status_code != 200:
        return []
    res_dict = str2dict(res.text)
    if res_dict['success'] == 'false' or \
       'data' not in res_dict.keys():
        return []
    result = list2dict(res_dict['data'])
    return result if isinstance(result,list) else [result]

if __name__ == "__main__":
    accounts = btc_accounts()
    print accounts
