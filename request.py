#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 13:01:16 2018

@author: frank
"""
from btc.request import listaccounts

if __name__ == "__main__":
    accounts = listaccounts()
    print(accounts)
