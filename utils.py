"""
Created on Thu Mar 15 14:30:38 2019
@author: junying
"""

import decimal
import sys
import json

def str_to_decimal(x):
    if sys.version[0] > 2:
        return int(x)
    else:
        return long(x)

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def get_linenumber():
    return sys.exc_info()[2].tb_lineno

def hex_to_dec(x):
    '''
    Convert hex to decimal
    '''
    return int(x, 16)


def clean_hex(d):
    '''
    Convert decimal to hex and remove the "L" suffix that is appended to large
    numbers
    '''
    return hex(d).rstrip('L')

def str2dict(string):
    json_acceptable_string = string.replace("'", "\"")
    return json.loads(json_acceptable_string)

"""
IN: [[{}]]
OUT:  {}
IN: [[{},{}]]
OUT: [{},{}]
"""

from constants import IP_ADDR, PORT

def list2dict(var):
    if isinstance(var,dict): return var
    elif isinstance(var,list):
        if len(var) == 1: return list2dict(var[0])
        elif all(isinstance(item,dict) for item in var): return var
    return {}

import requests
def post(fname='eth/listaccounts',params={}):
    try:
        return True, requests.post('http://%s:%d/%s'%(IP_ADDR,PORT,fname),params)
    except Exception as e:
        #print("post operation err: {0}".format(e))
        return False,"connection failure!!!"

def get(fname='eth/listaccounts',params={}):
    try:
        return True,requests.get('http://%s:%d/%s'%(IP_ADDR,PORT,fname),params)
    except Exception as e:
        # print("post operation err: {0}".format(e))   
        return False,"connection failure!!!"

##################################################################
## ethereum ######################################################
##################################################################

from constants import BLOCK_TAGS

def validate_block(block):
    if isinstance(block, basestring):
        if block not in BLOCK_TAGS:
            raise ValueError('invalid block tag')
    if isinstance(block, int):
        block = hex(block)
    return block

def wei_to_ether(wei):
    '''
    Convert wei to ether
    '''
    return 1.0 * wei / 10**18

def ether_to_wei(ether):
    '''
    Convert ether to wei
    '''
    return ether * 10**18

def get_privkey(filename,passwd):
    with open(filename) as f:
        import json
        data = json.load(f)
        from ethereum.tools.keys import decode_keystore_json
        from rlp.utils import encode_hex
        return encode_hex(decode_keystore_json(data,passwd))
        
"""
$ python utils.py UTC--2019-03-14T08-21-57.582333053Z--a69cbac58e16f007cb553a59651725fed671c335 123
c9cd37e7d47825219002a06bdb2debcb73d89c15b6a50c1f332d4985a62b2610
"""
def test_get_privkey():
    import sys
    if len(sys.argv) > 2:
        privkey = get_privkey(sys.argv[1],sys.argv[2])
        print(privkey)
        from ethereum.utils import privtoaddr
        from rlp.utils import decode_hex
        print(privtoaddr(decode_hex(privkey)))

##################################################################
## bitcoin #######################################################
##################################################################
"""
IN:  [{u'shape':u'rectangle', u'amount':3},{u'shape':u'circle', u'amount':5},{u'shape':u'ellipse', u'amount':2}],['amount']
OUT: [{'amount':3},{'amount':5},{'amount':2}]
"""
def filtered(origin,selected=["txid","vout"]):
    ### remove keys
    import copy
    clone = copy.deepcopy(origin)
    unwanted = set(origin.keys()) - set(selected)
    for unwanted_key in unwanted: del clone[unwanted_key]
    ### remove unicode
    for key,value in clone.items():
        if isinstance(key,unicode): clone[str(key)] = str(clone.pop(key)) if isinstance(value,unicode) else clone.pop(key)
    return clone    

"""
IN:  [{'shape':'rectangle', 'colr':'blue'}],'colr','color'
OUT: [{'shape':'rectangle', 'color':'blue'}]
"""
def alterkeyname(origin,oldkey,newkey):
    import copy
    clone = copy.deepcopy(origin)
    value = clone[oldkey]
    if isinstance(value,decimal.Decimal): clone[newkey] = float(clone.pop(oldkey))
    else: clone[newkey] = clone.pop(oldkey)
    return clone

def calcFee(iInTxCount,iOutTxCount=2):
    from decimal import Decimal    
    from decimal import getcontext
    getcontext().prec = 8
    return Decimal(str((148 * iInTxCount + 34 * iOutTxCount + 10))) *  Decimal('0.00000012')

"""
IN:  [{'shape':'rectangle', 'amount':3},{'shape':'circle', 'amount':5},{'shape':'ellipse', 'amount':2}],5
OUT: [{'shape':'rectangle', 'amount':3},{'shape':'circle', 'amount':5}],8
"""
def recommended(all,amount):
    selected = []
    from decimal import Decimal    
    aggregate = Decimal('0')
    for utxo in [item for item in all if int(item["confirmations"]) >= 1]:
        if aggregate > Decimal(str(amount)): break
        selected.append(utxo)
        #aggregate += float(utxo["amount"])
        aggregate += Decimal(str((utxo["amount"])))
    return selected,aggregate

"""
IN:  [{'shape':'rectangle'}],'colr','blue'
OUT: [{'shape':'rectangle', 'colr':'blue'}]
"""
def addkey(origin,key,value):
    if isinstance(origin,dict): origin[key] = value
    elif isinstance(origin,list):
        for item in origin: item[key] = value

"""
IN:  [{'shape':'rectangle', 'colr':'blue'}], 'colr'
OUT: [{'shape':'rectangle'}]
"""
def deletekey(origin,key):
    if isinstance(origin,dict): del origin[key]
    elif isinstance(origin,list):
        for item in origin: del item[key]

"""
IN:  [{'shape':'rectangle', 'amount':3},{'shape':'circle', 'amount':6}]
OUT: 9
"""
def accumulate(all):
    aggregate = 0
    for item in all: aggregate += float(item["amount"]) if int(item["confirmations"]) >= 6 else 0
    return aggregate

def distribute(all,oldkey,newkey,amount):
    filtered = []
    for item in all:
        value = float(item.pop(oldkey))
        item[newkey] = amount
        filtered.append(item)
    return filtered
    
##################################################################
## encryption ####################################################
##################################################################

"""
IN:  [{'txid':'123456789','amount':0.233}]
OUT: 5b7b22616d6f756e74223a20302e3233332c202274786964223a2022313233343536373839227d5d
"""
def encode(data):
    from rlp.utils import encode_hex
    return encode_hex(json.dumps(data))

"""
IN:  5b7b22616d6f756e74223a20302e3233332c202274786964223a2022313233343536373839227d5d
OUT: [{'txid':'123456789','amount':0.233}]
"""
def decode(data):
    from rlp.utils import decode_hex
    decoded = decode_hex(data)
    return json.loads(decoded)

"""
IN: '{"foo":"bar", "foo2":"bar2"}'
OUT: {'foo': 'bar', 'foo2': 'bar2'}
"""
def str2dict(str):
    import yaml
    return yaml.load(str)

def json2dict(str):
    return json.loads(str)

if __name__ == "__main__":
    test_get_privkey()