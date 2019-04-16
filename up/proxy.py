#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 14:30:38 2018

@author: frank
"""

import json
import warnings

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.models import Response
from ethereum.abi import encode_abi, decode_abi

import ethereum.utils as utils
from utils import hex_to_dec, clean_hex, validate_block

from constants import BLOCK_TAGS, BLOCK_TAG_LATEST,UP_RPC_PORT

GUP_DEFAULT_RPC_PORT = UP_RPC_PORT
UP_DEFAULT_RPC_PORT = UP_RPC_PORT
PARITY_DEFAULT_RPC_PORT = UP_RPC_PORT
PYUPAPP_DEFAULT_RPC_PORT = 4000
MAX_RETRIES = 3
JSON_MEDIA_TYPE = 'application/json'

class UnitedProneProxy(object):
    '''
    Ethereum JSON-RPC client class
    '''

    DEFAULT_GAS_PER_TX = 90000
    DEFAULT_GAS_PRICE = 50 * 10**9  # 50 gwei

    def __init__(self, host='localhost', port=GUP_DEFAULT_RPC_PORT, tls=False):
        self.host = host
        self.port = port
        self.tls = tls
        self.session = requests.Session()
        self.session.mount(self.host, HTTPAdapter(max_retries=MAX_RETRIES))

    def _call(self, method, params=None, _id=1):

        params = params or []
        data = {
            'jsonrpc': '2.0',
            'method':  method,
            'params':  params,
            'id':      _id,
        }
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}'.format(scheme, self.host, self.port)
        headers = {'Content-Type': JSON_MEDIA_TYPE}
        Response()
        try:
            r = self.session.post(url, headers=headers, data=json.dumps(data))
        except RequestsConnectionError:
            pass#raise BadConnectionError
        if r.status_code / 100 != 2:
            pass#raise BadStatusCodeError(r.status_code)
        try:
            response = r.json()
        except ValueError:
            pass#raise BadJsonError(r.text)
        try:
            return response['result']
        except KeyError:
            pass#raise BadResponseError(response)

    def _encode_function(self, signature, param_values):

        prefix = utils.big_endian_to_int(utils.sha3(signature)[:4])

        if signature.find('(') == -1:
            raise RuntimeError('Invalid function signature. Missing "(" and/or ")"...')

        if signature.find(')') - signature.find('(') == 1:
            return utils.encode_int(prefix)

        types = signature[signature.find('(') + 1: signature.find(')')].split(',')
        encoded_params = encode_abi(types, param_values)
        return utils.zpad(utils.encode_int(prefix), 4) + encoded_params

################################################################################
# high-level methods
################################################################################

    def transfer(self, from_, to, amount):
        '''
        Send wei from one address to another
        '''
        return self.up_sendTransaction(from_address=from_, to_address=to, value=amount)

    def create_contract(self, from_, code, gas, sig=None, args=None):
        '''
        Create a contract on the blockchain from compiled EVM code. Returns the
        transaction hash.
        '''
        from_ = from_ or self.up_coinbase()
        if sig is not None and args is not None:
             types = sig[sig.find('(') + 1: sig.find(')')].split(',')
             encoded_params = encode_abi(types, args)
             code += encoded_params.encode('hex')
        return self.up_sendTransaction(from_address=from_, gas=gas, data=code)

    def get_contract_address(self, tx):
        '''
        Get the address for a contract from the transaction that created it
        '''
        receipt = self.up_getTransactionReceipt(tx)
        return receipt['contractAddress']

    def call(self, address, sig, args, result_types):
        '''
        Call a contract function on the RPC server, without sending a
        transaction (useful for reading data)
        '''
        data = self._encode_function(sig, args)
        data_hex = data.encode('hex')
        response = self.up_call(to_address=address, data=data_hex)
        return decode_abi(result_types, response[2:].decode('hex'))

    def call_with_transaction(self, from_, address, sig, args, gas=None, gas_price=None, value=None):
        '''
        Call a contract function by sending a transaction (useful for storing
        data)
        '''
        gas = gas or self.DEFAULT_GAS_PER_TX
        gas_price = gas_price or self.DEFAULT_GAS_PRICE
        data = self._encode_function(sig, args)
        data_hex = data.encode('hex')
        return self.up_sendTransaction(from_address=from_, to_address=address, data=data_hex, gas=gas,
                                        gas_price=gas_price, value=value)

################################################################################
# JSON-RPC methods
################################################################################

    def web3_clientVersion(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#web3_clientversion

        TESTED
        '''
        return self._call('web3_clientVersion')

    def web3_sha3(self, data):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#web3_sha3

        TESTED
        '''
        data = str(data).encode('hex')
        return self._call('web3_sha3', [data])

    def net_version(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#net_version

        TESTED
        '''
        return self._call('net_version')

    def net_listening(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#net_listening

        TESTED
        '''
        return self._call('net_listening')

    def net_peerCount(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#net_peercount

        TESTED
        '''
        return hex_to_dec(self._call('net_peerCount'))

    def up_protocolVersion(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_protocolversion

        TESTED
        '''
        return self._call('up_protocolVersion')

    def up_syncing(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_syncing

        TESTED
        '''
        return self._call('up_syncing')

    def up_coinbase(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_coinbase

        TESTED
        '''
        return self._call('up_coinbase')

    def up_mining(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_mining

        TESTED
        '''
        return self._call('up_mining')

    def up_hashrate(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_hashrate

        TESTED
        '''
        return hex_to_dec(self._call('up_hashrate'))

    def up_gasPrice(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_gasprice

        TESTED
        '''
        return hex_to_dec(self._call('up_gasPrice'))

    def up_accounts(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_accounts

        TESTED
        '''
        return self._call('up_accounts')

    def up_blockNumber(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_blocknumber

        TESTED
        '''
        return hex_to_dec(self._call('up_blockNumber'))

    def up_getBalance(self, address=None, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getbalance

        TESTED
        '''
        address = address or self.up_coinbase()
        block = validate_block(block)
        return hex_to_dec(self._call('up_getBalance', [address, block]))

    def up_getStorageAt(self, address=None, position=0, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getstorageat

        TESTED
        '''
        block = validate_block(block)
        return self._call('up_getStorageAt', [address, hex(position), block])

    def up_getTransactionCount(self, address, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_gettransactioncount

        TESTED
        '''
        block = validate_block(block)
        return hex_to_dec(self._call('up_getTransactionCount', [address, block]))

    def up_getBlockTransactionCountByHash(self, block_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getblocktransactioncountbyhash

        TESTED
        '''
        return hex_to_dec(self._call('up_getBlockTransactionCountByHash', [block_hash]))

    def up_getBlockTransactionCountByNumber(self, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getblocktransactioncountbynumber

        TESTED
        '''
        block = validate_block(block)
        return hex_to_dec(self._call('up_getBlockTransactionCountByNumber', [block]))

    def up_getUncleCountByBlockHash(self, block_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getunclecountbyblockhash

        TESTED
        '''
        return hex_to_dec(self._call('up_getUncleCountByBlockHash', [block_hash]))

    def up_getUncleCountByBlockNumber(self, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getunclecountbyblocknumber

        TESTED
        '''
        block = validate_block(block)
        return hex_to_dec(self._call('up_getUncleCountByBlockNumber', [block]))

    def up_getCode(self, address, default_block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getcode

        NEEDS TESTING
        '''
        if isinstance(default_block, basestring):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        return self._call('up_getCode', [address, default_block])

    def up_sign(self, address, data):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_sign

        NEEDS TESTING
        '''
        return self._call('up_sign', [address, data])

    def up_sendTransaction(self, to_address=None, from_address=None, gas=None, gas_price=None, value=None, data=None,
                            nonce=None):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_sendtransaction

        NEEDS TESTING
        '''
        params = {}
        params['from'] = from_address or self.up_coinbase()
        if to_address is not None:
            params['to'] = to_address
        if gas is not None:
            params['gas'] = clean_hex(gas)
        if gas_price is not None:
            params['gasPrice'] = clean_hex(gas_price)#hex(gas_price)[:-1]
        if value is not None:
            params['value'] = clean_hex(value)#hex(value)[:-1]
        if data is not None:
            params['data'] = data
        if nonce is not None:
            params['nonce'] = clean_hex(nonce)
        return self._call('up_sendTransaction', [params])

    def up_sendRawTransaction(self, data):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_sendrawtransaction

        NEEDS TESTING
        '''
        return self._call('up_sendRawTransaction', [data])

    def up_call(self, to_address, from_address=None, gas=None, gas_price=None, value=None, data=None,
                 default_block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_call

        NEEDS TESTING
        '''
        if isinstance(default_block, basestring):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        obj = {}
        obj['to'] = to_address
        if from_address is not None:
            obj['from'] = from_address
        if gas is not None:
            obj['gas'] = hex(gas)
        if gas_price is not None:
            obj['gasPrice'] = clean_hex(gas_price)
        if value is not None:
            obj['value'] = value
        if data is not None:
            obj['data'] = data
        return self._call('up_call', [obj, default_block])

    def up_estimateGas(self, to_address=None, from_address=None, gas=None, gas_price=None, value=None, data=None,
                        default_block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_estimategas

        NEEDS TESTING
        '''
        if isinstance(default_block, basestring):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        obj = {}
        if to_address is not None:
            obj['to'] = to_address
        if from_address is not None:
            obj['from'] = from_address
        if gas is not None:
            obj['gas'] = hex(gas)
        if gas_price is not None:
            obj['gasPrice'] = clean_hex(gas_price)
        if value is not None:
            obj['value'] = value
        if data is not None:
            obj['data'] = data
        return hex_to_dec(self._call('up_estimateGas', [obj, default_block]))

    def up_getBlockByHash(self, block_hash, tx_objects=True):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getblockbyhash

        TESTED
        '''
        return self._call('up_getBlockByHash', [block_hash, tx_objects])

    def up_getBlockByNumber(self, block=BLOCK_TAG_LATEST, tx_objects=True):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getblockbynumber

        TESTED
        '''
        block = validate_block(block)
        return self._call('up_getBlockByNumber', [block, tx_objects])

    def up_getTransactionByHash(self, tx_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_gettransactionbyhash

        TESTED
        '''
        return self._call('up_getTransactionByHash', [tx_hash])

    def up_getTransactionByBlockHashAndIndex(self, block_hash, index=0):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_gettransactionbyblockhashandindex

        TESTED
        '''
        return self._call('up_getTransactionByBlockHashAndIndex', [block_hash, hex(index)])

    def up_getTransactionByBlockNumberAndIndex(self, block=BLOCK_TAG_LATEST, index=0):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_gettransactionbyblocknumberandindex

        TESTED
        '''
        block = validate_block(block)
        return self._call('up_getTransactionByBlockNumberAndIndex', [block, hex(index)])

    def up_getTransactionReceipt(self, tx_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_gettransactionreceipt

        TESTED
        '''
        return self._call('up_getTransactionReceipt', [tx_hash])

    def up_getUncleByBlockHashAndIndex(self, block_hash, index=0):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getunclebyblockhashandindex

        TESTED
        '''
        return self._call('up_getUncleByBlockHashAndIndex', [block_hash, hex(index)])

    def up_getUncleByBlockNumberAndIndex(self, block=BLOCK_TAG_LATEST, index=0):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getunclebyblocknumberandindex

        TESTED
        '''
        block = validate_block(block)
        return self._call('up_getUncleByBlockNumberAndIndex', [block, hex(index)])

    def up_getCompilers(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getcompilers

        TESTED
        '''
        return self._call('up_getCompilers')

    def up_compileSolidity(self, code):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_compilesolidity

        TESTED
        '''
        return self._call('up_compileSolidity', [code])

    def up_compileLLL(self, code):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_compilelll

        N/A
        '''
        return self._call('up_compileLLL', [code])

    def up_compileSerpent(self, code):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_compileserpent

        N/A
        '''
        return self._call('up_compileSerpent', [code])

    def up_newFilter(self, from_block=BLOCK_TAG_LATEST, to_block=BLOCK_TAG_LATEST, address=None, topics=None):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_newfilter

        NEEDS TESTING
        '''
        _filter = {
            'fromBlock': from_block,
            'toBlock':   to_block,
            'address':   address,
            'topics':    topics,
        }
        return self._call('up_newFilter', [_filter])

    def up_newBlockFilter(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_newblockfilter

        TESTED
        '''
        return self._call('up_newBlockFilter')

    def up_newPendingTransactionFilter(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_newpendingtransactionfilter

        TESTED
        '''
        return hex_to_dec(self._call('up_newPendingTransactionFilter'))

    def up_pendingTransactions(self):
        return self._call('up_pendingTransactions')
    
    def up_uninstallFilter(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_uninstallfilter

        NEEDS TESTING
        '''
        return self._call('up_uninstallFilter', [filter_id])

    def up_getFilterChanges(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getfilterchanges

        NEEDS TESTING
        '''
        return self._call('up_getFilterChanges', [filter_id])

    def up_getFilterLogs(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getfilterlogs

        NEEDS TESTING
        '''
        return self._call('up_getFilterLogs', [filter_id])

    def up_getLogs(self, filter_object):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getlogs

        NEEDS TESTING
        '''
        return self._call('up_getLogs', [filter_object])

    def up_getWork(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_getwork

        TESTED
        '''
        return self._call('up_getWork')

    def up_submitWork(self, nonce, header, mix_digest):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_submitwork

        NEEDS TESTING
        '''
        return self._call('up_submitWork', [nonce, header, mix_digest])

    def up_submitHashrate(self, hash_rate, client_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#up_submithashrate

        TESTED
        '''
        return self._call('up_submitHashrate', [hex(hash_rate), client_id])

    def db_putString(self, db_name, key, value):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_putstring

        TESTED
        '''
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_putString', [db_name, key, value])

    def db_getString(self, db_name, key):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_getstring

        TESTED
        '''
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_getString', [db_name, key])

    def db_putHex(self, db_name, key, value):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_puthex

        TESTED
        '''
        if not value.startswith('0x'):
            value = '0x{}'.format(value)
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_putHex', [db_name, key, value])

    def db_getHex(self, db_name, key):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_gethex

        TESTED
        '''
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_getHex', [db_name, key])

    def personal_newAccount(self,passphrase):
        return self._call('personal_newAccount', [passphrase])

    def personal_unlockAccount(self,account,passphrase):
        return self._call('personal_unlockAccount', [account,passphrase])

    def shh_version(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_version

        N/A
        '''
        return self._call('shh_version')

    def shh_post(self, topics, payload, priority, ttl, from_=None, to=None):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_post

        NEEDS TESTING
        '''
        whisper_object = {
            'from':     from_,
            'to':       to,
            'topics':   topics,
            'payload':  payload,
            'priority': hex(priority),
            'ttl':      hex(ttl),
        }
        return self._call('shh_post', [whisper_object])

    def shh_newIdentity(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newidentity

        N/A
        '''
        return self._call('shh_newIdentity')

    def shh_hasIdentity(self, address):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_hasidentity

        NEEDS TESTING
        '''
        return self._call('shh_hasIdentity', [address])

    def shh_newGroup(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newgroup

        N/A
        '''
        return self._call('shh_newGroup')

    def shh_addToGroup(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_addtogroup

        NEEDS TESTING
        '''
        return self._call('shh_addToGroup')

    def shh_newFilter(self, to, topics):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newfilter

        NEEDS TESTING
        '''
        _filter = {
            'to':     to,
            'topics': topics,
        }
        return self._call('shh_newFilter', [_filter])

    def shh_uninstallFilter(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_uninstallfilter

        NEEDS TESTING
        '''
        return self._call('shh_uninstallFilter', [filter_id])

    def shh_getFilterChanges(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_getfilterchanges

        NEEDS TESTING
        '''
        return self._call('shh_getFilterChanges', [filter_id])

    def shh_getMessages(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_getmessages

        NEEDS TESTING
        '''
        return self._call('shh_getMessages', [filter_id])


class ParityEthJsonRpc(UnitedProneProxy):
    '''
    EthJsonRpc subclass for Parity-specific methods
    '''

    def __init__(self, host='localhost', port=PARITY_DEFAULT_RPC_PORT, tls=False):
        UnitedProneProxy.__init__(self, host=host, port=port, tls=tls)

    def trace_filter(self, from_block=None, to_block=None, from_addresses=None, to_addresses=None):
        '''
        https://github.com/ethcore/parity/wiki/JSONRPC-trace-module#trace_filter

        TESTED
        '''
        params = {}
        if from_block is not None:
            from_block = validate_block(from_block)
            params['fromBlock'] = from_block
        if to_block is not None:
            to_block = validate_block(to_block)
            params['toBlock'] = to_block
        if from_addresses is not None:
            if not isinstance(from_addresses, list):
                from_addresses = [from_addresses]
            params['fromAddress'] = from_addresses
        if to_addresses is not None:
            if not isinstance(to_addresses, list):
                to_addresses = [to_addresses]
            params['toAddress'] = to_addresses
        return self._call('trace_filter', [params])

    def trace_get(self, tx_hash, positions):
        '''
        https://github.com/ethcore/parity/wiki/JSONRPC-trace-module#trace_get

        NEEDS TESTING
        '''
        if not isinstance(positions, list):
            positions = [positions]
        return self._call('trace_get', [tx_hash, positions])

    def trace_transaction(self, tx_hash):
        '''
        https://github.com/ethcore/parity/wiki/JSONRPC-trace-module#trace_transaction

        TESTED
        '''
        return self._call('trace_transaction', [tx_hash])

    def trace_block(self, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethcore/parity/wiki/JSONRPC-trace-module#trace_block

        TESTED
        '''
        block = validate_block(block)
        return self._call('trace_block', [block])
