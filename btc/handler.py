"""
Created on Thu Mar 15 14:30:38 2019
@author: kojy
"""

import json
from utils import decimal_default,get_linenumber
from base_handler import BaseHandler
from .proxy import AuthServiceProxy
from constants import BTC_RPC_URL

class BTC_GetAccount(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20180325
        try:
            commands = [["getaccount",self.get_argument("address")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetAccount error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetAccountAddress(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20180325
        try:
            commands = [["getaccountaddress",self.get_argument("account")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetAccoutAddress error:{0} in {1}".format(e,get_linenumber()))
            
class BTC_GetAccountBalance(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20180325
        try:
            account = self.get_argument("account").decode("utf-8")
            if account is None or len(account) == 0:
                self.write(json.dumps(BaseHandler.error_ret()))
                return 
            commands = [["getbalance", account]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetAccountBalance error:{0} in {1}".format(e,get_linenumber()))

# created by kojy
# in 2018/03/25
class BTC_GetNewAddress(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20180325
        try:
            account = self.get_argument("account")
            address_type = self.get_argument("address_type") if not self.get_argument("address_type") == "" else "legacy"
            commands = [["getnewaddress",account,address_type]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetNewAddress error:{0} in {1}".format(e,get_linenumber()))
           
class BTC_ListAccounts(BaseHandler):    
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20180325
        data = None
        try:
            minconf = int(self.get_argument("minconf")) if not self.get_argument("minconf") == "" else 0
            commands = [["listaccounts",minconf]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_ListAccounts error:{0} in {1}".format(e,get_linenumber()))

class BTC_WalletPassphrase(BaseHandler):
    @staticmethod
    def unlock(rpcconn,passphrase,unlocktime=120):
        commands = [["walletpassphrase", passphrase, unlocktime]]
        data = rpcconn.batch_(commands)

    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20180325
        try:
            data = BTC_WalletPassphrase.unlock(btc_rpc_connection,self.get_argument("passphrase"))
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_WalletPassphrase error:{0} in {1}".format(e,get_linenumber()))

class BTC_SendFrom(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20180325
        try:
            # unlock wallet
            BTC_WalletPassphrase.unlock(btc_rpc_connection,self.get_argument("passphrase"))
            # send
            commands = [["sendfrom",self.get_argument("fromaccount"),self.get_argument("toaddress"),float(self.get_argument("amount"))]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_Sendfrom error:{0} in {1}".format(e,get_linenumber()))
           
####################################################################################################################
# Cold Wallet ######################################################################################################
####################################################################################################################

from utils import encode,decode,calcFee

class BTC_GetBalance(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20180325
        try:
            addr = self.get_argument("address")
            data = BTC_ListUTXO.utxo(btc_rpc_connection,addr)
            if not data:
                self.write(json.dumps(BaseHandler.error_ret_with_data("utxo no available")))
            from utils import accumulate
            self.write(json.dumps(BaseHandler.success_ret_with_data(accumulate(data)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetBalance error:{0} in {1}".format(e,get_linenumber()))

class BTC_ListUTXO(BaseHandler):
    @staticmethod
    def utxo(rpcconn,addr,minconf=0,maxconf=9999999):
        commands = [["listunspent", minconf, maxconf, [addr]]]
        return rpcconn.batch_(commands)[0]

    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)# todo-kojy-20180325
        data = None
        try:
            minconf = int(self.get_argument("minconf")) if not self.get_argument("minconf") == "" else 0
            maxconf = int(self.get_argument("maxconf")) if not self.get_argument("maxconf") == "" else 9999999
            addr = self.get_argument("address")
            data = BTC_ListUTXO.utxo(btc_rpc_connection,addr,minconf,maxconf)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetUTXO error:{0} in {1}".format(e,get_linenumber()))

class BTC_CreateRawTransaction(BaseHandler):
    @staticmethod
    def process(rpcconn,from_addr,to_addr,amount):
        # utxos
        all = BTC_ListUTXO.utxo(rpcconn,from_addr)
        # recommend
        from utils import recommended
        selected,aggregate = recommended(all,amount)
        # check if enough
        from utils import calcFee
        fee = calcFee(len(selected))
        if aggregate < fee + amount:
            return False,"budget not enough"
        # make augmentations
        from utils import filtered
        param_in = [filtered(item,["txid","vout"]) for item in selected]
        param_out = {to_addr:amount,from_addr:aggregate-amount-fee}
        # create raw transaction
        commands = [["createrawtransaction",param_in,param_out]]
        return True, rpcconn.batch_(commands)

    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20190310
        try:
            from_addr = self.get_argument("from") if self.get_argument("from") else '2N8jq3e7eBhrrd9d1dMNCvkwtsvN9md2Hmd'
            to_addr = self.get_argument("to") if self.get_argument("to") else '2MzrgJmFfHB1mz4QqwuSWePbb183TxHR1wA'
            amount = float(self.get_argument("amount"))
            ret, rsp = BTC_CreateRawTransaction.process(btc_rpc_connection,from_addr,to_addr,amount)
            if not ret:
                self.write(json.dumps(BaseHandler.error_ret_with_data(rsp)))
                return 
            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_CreatRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class BTC_SignRawTransaction(BaseHandler):
    @staticmethod
    def calcprevtx(rpc_connection,addr,amount):
        # utxos
        all = BTC_ListUTXO.utxo(rpc_connection,addr)
        # recommend
        from utils import recommended
        selected,aggregate = recommended(all,amount)
        # make augmentations
        from utils import filtered
        return [filtered(item,["txid","vout","amount","redeemScript","scriptPubKey"]) for item in selected]

    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20190310
        try:
            rawdata = self.get_argument("rawdata") if self.get_argument("rawdata") else '02000000011d9c5db5afc7b8f9606569a9d470c435764b8dbf372c473d152c0cff1a77f5f10100000000ffffffff024d9083000000000017a914a9f2cc6c49785beabd9eb26d6d4d1f17fd365d308780841e000000000017a914537d68a8c0e4c04262f419a81aed12ffbad148408700000000'
            privkey = self.get_argument("privkey") if self.get_argument("privkey") else 'cU27rdRN2uazREh9bBiWQq9e1ZPLAmEguk8ZBuBWKf6a8oav6y73'
            addr = self.get_argument("address") if self.get_argument("address") else '2N8jq3e7eBhrrd9d1dMNCvkwtsvN9md2Hmd'
            amount = self.get_argument("amount")
            param_in = BTC_SignRawTransaction.calcprevtx(btc_rpc_connection,addr,amount)
            commands = [["signrawtransactionwithkey",rawdata,[privkey],param_in]]        
            rsp = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_SignRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class BTC_SendRawTransaction(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20190310
        try:
            rawdata = self.get_argument("rawdata") if self.get_argument("rawdata") else '020000000001011d9c5db5afc7b8f9606569a9d470c435764b8dbf372c473d152c0cff1a77f5f101000000171600142bf9ada27ec30b4f293ec6f61d98ca00c4d4bb2affffffff024d9083000000000017a914a9f2cc6c49785beabd9eb26d6d4d1f17fd365d308780841e000000000017a914537d68a8c0e4c04262f419a81aed12ffbad1484087024730440220327a6068844a484eb9887fe9d4645fe495d4e280b79013727e375d5e3e8ba86c0220124c779b6e412ef684e897f07fb959807c42b8c128cdbecac28e0de44711b39c012103760b1cfa248f4bf9a95e4812547da273eeccb1cef88a520267685263609e090b00000000'
            commands = [["sendrawtransaction",rawdata]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_SendRawTransaction error:{0} in {1}".format(e,get_linenumber()))

####################################################################################################################
# Timer ############################################################################################################
####################################################################################################################

class BTC_ListTransActions(BaseHandler):
    @staticmethod
    def process(rpc_connection,account="*",tx_counts=10,skips=0):
        commands = [["listtransactions",account,tx_counts,skips]]
        data = rpc_connection.batch_(commands)
        from utils import filtered
        return [filtered(item,["address","category","amount","confirmations","txid","time"]) for item in data[0]]

    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20190315
        try:
            account = self.get_argument("account") if self.get_argument("account") else "*"
            tx_counts = int(self.get_argument("count")) if self.get_argument("count") else 10
            skips = int(self.get_argument("skips")) if self.get_argument("skips") else 0
            data = BTC_ListTransActions.process(btc_rpc_connection,account,tx_counts,skips)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_ListTransActions error:{0} in {1}".format(e,get_linenumber()))

####################################################################################################################
# Block Monitoring #################################################################################################
####################################################################################################################

class BTC_GetBlockCount(BaseHandler):
    def process(rpcconn):
        commands = [["getblockcount"]]
        return rpcconn.batch_(commands)

    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20190310
        try:
            commands = [["getblockcount"]]
            data = BTC_GetBlockCount.process(btc_rpc_connection)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetBlockCount error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetBlockHash(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20190310
        try:
            rawdata = self.get_argument("rawdata") if self.get_argument("rawdata") else BTC_GetBlockCount.process(btc_rpc_connection)
            commands = [["getblockhash"]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetBlockHash error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetTransaction(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20180325
        try:
            commands = [["gettransaction",self.get_argument("txid")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetTransaction error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetRawTransaction(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20180325
        try:
            commands = [["getrawtransaction",self.get_argument("txid"),True]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetTransaction error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetBlock(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-kojy-20190310
        try:
            blkhash = self.get_argument("blkhash") if self.get_argument("rawdata") else BTC_GetBlockCount.process(btc_rpc_connection)
            commands = [["getblockhash"]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetBlockHash error:{0} in {1}".format(e,get_linenumber()))