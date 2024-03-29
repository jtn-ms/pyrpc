
"""
Created on Thu Mar 15 14:30:38 2019
@author: junying
"""
import json
from utils import decimal_default,get_linenumber
from base_handler import BaseHandler
from .proxy import AuthServiceProxy
from constants import OMNI_RPC_URL,OMNI_PROPERTY_ID,OMNI_TRANSACTION_FEE,OMNI_TRANSACTION_RECIPIENT_GAIN

####################################################################################################################
# Bitcoin Functions ################################################################################################
####################################################################################################################

class uBTC_GetAccountAddress(BaseHandler):
    def get(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20180325
        try:
            commands = [["getaccountaddress",self.get_argument("account")]]
            data = omni_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("uBTC_GetAccountAddress error:{0} in {1}".format(e,get_linenumber()))
            
class uBTC_GetNewAddress(BaseHandler):
    def post(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20180325
        try:
            address_type = self.get_argument("address_type") if not self.get_argument("address_type") == "" else "legacy"
            commands = [["getnewaddress",self.get_argument("account"),address_type]]
            data = omni_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("uBTC_GetNewAddress error:{0} in {1}".format(e,get_linenumber()))

class uBTC_ListAccounts(BaseHandler):    
    def get(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20180325
        data = None
        try:
            minconf = int(self.get_argument("minconf")) if not self.get_argument("minconf") == "" else 0
            commands = [["listaccounts",minconf]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("uBTC_ListAccounts error:{0} in {1}".format(e,get_linenumber()))

class uBTC_ListUTXO(BaseHandler):
    def post(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)# todo-junying-20180325
        try:
            minconf = int(self.get_argument("minconf")) if not self.get_argument("minconf") == "" else 0
            maxconf = int(self.get_argument("maxconf")) if not self.get_argument("maxconf") == "" else 9999999
            from btc.handler import BTC_ListUTXO
            data = BTC_ListUTXO.utxo(omni_rpc_connection,self.get_argument("address"),minconf,maxconf)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("uBTC_ListUTXO error:{0} in {1}".format(e,get_linenumber()))


class uBTC_GetBalance(BaseHandler):
    def get(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20180325
        try:
            from btc.handler import BTC_ListUTXO
            data = BTC_ListUTXO.utxo(omni_rpc_connection,self.get_argument("address"))
            if not data:
                self.write(json.dumps(BaseHandler.error_ret_with_data("utxo no available")))
            from utils import accumulate
            self.write(json.dumps(BaseHandler.success_ret_with_data(accumulate(data)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("uBTC_GetBalance error:{0} in {1}".format(e,get_linenumber()))

class uBTC_CreateRawTransaction(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20190310
        try:
            from_addr = str(self.get_argument("from")) if self.get_argument("from") else '2N8jq3e7eBhrrd9d1dMNCvkwtsvN9md2Hmd'
            to_addr = str(self.get_argument("to")) if self.get_argument("to") else '2MzrgJmFfHB1mz4QqwuSWePbb183TxHR1wA'
            amount = float(self.get_argument("amount"))
            from btc.handler import BTC_CreateRawTransaction
            ret, rsp = BTC_CreateRawTransaction.process(btc_rpc_connection,from_addr,to_addr,amount)
            if not ret:
                self.write(json.dumps(BaseHandler.error_ret_with_data(rsp)))
                return 
            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("uBTC_CreateRawTransaction error:{0} in {1}".format(e,get_linenumber()))

from decimal import Decimal

class uBTC_SignRawTransaction(BaseHandler):
    def get_argument_ex(self,str):
        from utils import json2dict
        str2dict = json2dict(self.request.body)
        return str2dict[str] if str in str2dict.keys() else False
        
    def post(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20190310
        try:
            rawdata = self.get_argument("rawdata") if self.get_argument("rawdata") else '02000000011d9c5db5afc7b8f9606569a9d470c435764b8dbf372c473d152c0cff1a77f5f10100000000ffffffff024d9083000000000017a914a9f2cc6c49785beabd9eb26d6d4d1f17fd365d308780841e000000000017a914537d68a8c0e4c04262f419a81aed12ffbad148408700000000'
            privkey = self.get_argument("privkey") if self.get_argument("privkey") else 'cTe4efinSJLgj8BYdkvnH27Dd6QCM6eeZYRPb6ifGLzuS8oH1gam'
            addr = self.get_argument("address") if self.get_argument("address") else 'mtwEVo8FVJrMcms1GyzhbTUSafwDKvyjsq'
            amount = Decimal(self.get_argument("amount")) if self.get_argument("amount") else Decimal(OMNI_TRANSACTION_FEE)
            from btc.handler import BTC_SignRawTransaction
            param_in = BTC_SignRawTransaction.calcprevtx(btc_rpc_connection,addr,amount)
            # sign raw transaction
            commands = [["signrawtransaction",rawdata,param_in,[privkey]]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("uBTC_SignRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class uBTC_SendRawTransaction(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20190310
        try:
            commands = [["sendrawtransaction",self.get_argument("rawdata")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("uBTC_SendRawTransaction error:{0} in {1}".format(e,get_linenumber()))            

####################################################################################################################
# Omni Functions ###################################################################################################
####################################################################################################################

class OMNI_GetBalance(BaseHandler):
    def get(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20190313
        try:
            commands = [["omni_getbalance", self.get_argument("address"), OMNI_PROPERTY_ID]] # usdt: 31
            data = omni_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("OMNI_GetBalance error:{0} in {1}".format(e,get_linenumber()))
           
class OMNI_Send(BaseHandler):
    def post(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20180325
        try:
            from_addr = self.get_argument("fromaddress") if self.get_argument("fromaddress") else 'mtwEVo8FVJrMcms1GyzhbTUSafwDKvyjsq'
            to_addr = self.get_argument("toaddress") if self.get_argument("toaddress") else 'mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE'
            from btc.handler import BTC_WalletPassphrase
            BTC_WalletPassphrase.unlock(omni_rpc_connection,self.get_argument("passphrase"))
            commands = [["omni_send",from_addr,to_addr,OMNI_PROPERTY_ID,self.get_argument("amount")]]
            data = omni_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("OMNI_Send error:{0} in {1}".format(e,get_linenumber()))

####################################################################################################################
# Omni Cold Wallet #################################################################################################
####################################################################################################################

from utils import encode,decode,calcFee

class OMNI_CreateRawTransaction(BaseHandler):
    @staticmethod
    def omni_createpayload_simplesend(omni_rpc_connection,amount):
        commands = [["omni_createpayload_simplesend",OMNI_PROPERTY_ID,amount]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def createrawtransaction(omni_rpc_connection,utxos,remain={}):
        commands = [["createrawtransaction",utxos,remain]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def omni_createrawtx_opreturn(omni_rpc_connection,rawdata1,rawdata2):
        commands = [["omni_createrawtx_opreturn",rawdata1,rawdata2]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def omni_createrawtx_reference(omni_rpc_connection,rawdata,toaddress):
        commands = [["omni_createrawtx_reference",rawdata,toaddress]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def omni_createrawtx_change(omni_rpc_connection,rawdata,utxos,fromaddress,fee):
        commands = [["omni_createrawtx_change",rawdata,utxos,fromaddress,fee]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    def post(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20190313
        try:
            # get arguments
            from_addr = self.get_argument("from") if self.get_argument("from") else 'mtwEVo8FVJrMcms1GyzhbTUSafwDKvyjsq'
            to_addr = self.get_argument("to") if self.get_argument("to") else 'mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE'
            amount = self.get_argument("amount")
            fee = Decimal(self.get_argument("fee")) if self.get_argument("fee") else Decimal(OMNI_TRANSACTION_FEE)
            # utxos
            from btc.handler import BTC_ListUTXO
            all = BTC_ListUTXO.utxo(omni_rpc_connection,from_addr)
            # recommend
            from utils import recommended
            selected,aggregate = recommended(all,fee)
            # check if enough
            from utils import calcFee
            fee_ = max(fee,calcFee(len(selected)))
            if aggregate < fee_:
                self.write(json.dumps(BaseHandler.error_ret_with_data("budget not enough")))
                return
            # omni_createpayload_simplesend
            rawdata1 = OMNI_CreateRawTransaction.omni_createpayload_simplesend(omni_rpc_connection,amount)
            # createrawtransaction
            from utils import filtered
            # deletekey(selected,u'vout'); addkey(selected,u'vout',1)
            param_in = [filtered(item,["txid","vout"]) for item in selected]
            param_out = {from_addr:aggregate - fee_}
            rawdata2 = OMNI_CreateRawTransaction.createrawtransaction(omni_rpc_connection,param_in,param_out)
            # omni_createrawtx_opreturn
            rawdata3 = OMNI_CreateRawTransaction.omni_createrawtx_opreturn(omni_rpc_connection,rawdata2,rawdata1)
            # omni_createrawtx_reference
            rawdata4 = OMNI_CreateRawTransaction.omni_createrawtx_reference(omni_rpc_connection,rawdata3,to_addr)
            # omni_createrawtx_change
            param_in = [filtered(item,["txid","vout","scriptPubKey","amount"]) for item in selected]
            from utils import distribute
            param_in = distribute(param_in,'amount','value',aggregate - fee_)
            rawhex = OMNI_CreateRawTransaction.omni_createrawtx_change(omni_rpc_connection,rawdata4,param_in,from_addr,fee_)
            # return
            self.write(json.dumps(BaseHandler.success_ret_with_data({"hex":rawhex,"utxos":selected}), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("OMNI_CreateRawTransaction error:{0} in {1}".format(e,get_linenumber()))

####################################################################################################################
# Timer ############################################################################################################
####################################################################################################################

class OMNI_ListTransActions(BaseHandler):
    @staticmethod
    def blknumbers(rpc_connection,account="*",tx_counts=10):
        commands = [["omni_listtransactions",account,tx_counts]]
        data = rpc_connection.batch_(commands)
        return [item['block'] for item in data[0] if "block" in item]

    @staticmethod
    def process(rpc_connection,account="*",tx_counts=10,skips=0):
        commands = [["omni_listtransactions",account,tx_counts,skips]]
        data = rpc_connection.batch_(commands)
        from utils import filtered
        return [filtered(item,["txid","sendingaddress","referenceaddress","amount","propertyid","blocktime","confirmations","block"]) for item in data[0]]

    def get(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20180325
        try:
            address = self.get_argument("address") if self.get_argument("address") else "*"
            tx_counts = int(self.get_argument("count")) if self.get_argument("count") else 10
            skips = int(self.get_argument("skips")) if self.get_argument("skips") else 0
            data = OMNI_ListTransActions.process(omni_rpc_connection,address,tx_counts,skips)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("OMNI_ListTransActions error:{0} in {1}".format(e,get_linenumber()))

class OMNI_CrawlTxData(BaseHandler):
    @staticmethod
    def process(rpc_connection,lastscannedblknumber):
        count = 10
        while 1:
            transactions = OMNI_ListTransActions.process(rpc_connection,'*',count)
            blknumbers = [int(item['block']) for item in transactions if 'block' in item.keys()]
            if len(blknumbers) == 0 or blknumbers[0] < lastscannedblknumber: return []
            if lastscannedblknumber in blknumbers: return [transaction for transaction in transactions if int(transaction['block'] >= lastscannedblknumber)]
            if count > len(blknumbers): return transactions
            count += 2 * (blknumbers[::-1][0] - lastscannedblknumber)

    def post(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20180325
        try:
            blknumber = int(self.get_argument("blknumber"))
            data = OMNI_CrawlTxData.process(omni_rpc_connection,blknumber)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("OMNI_ListTransActions error:{0} in {1}".format(e,get_linenumber()))

####################################################################################################################
# Else #############################################################################################################
####################################################################################################################

class uBTC_GetBlockCount(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20190310
        try:
            from btc.handler import BTC_GetBlockCount
            lastblknumber = BTC_GetBlockCount.process(btc_rpc_connection)
            self.write(json.dumps(BaseHandler.success_ret_with_data(lastblknumber), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetBlockCount error:{0} in {1}".format(e,get_linenumber()))

class OMNI_GetTransaction(BaseHandler):
    @staticmethod
    def process(rpc_connection,txid):
        commands = [["omi_gettransaction",txid]]
        transaction = rpc_connection.batch_(commands)
        from utils import filtered
        return filtered(transaction,["txid","sendingaddress","referenceaddress","amount","propertyid","blocktime","confirmations","block"])

    def post(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20180325
        try:
            data = OMNI_GetTransaction.process(btc_rpc_connection,self.get_argument("txid"))
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetTransaction error:{0} in {1}".format(e,get_linenumber()))

class OMNI_ListBlockTransActions(BaseHandler):
    @staticmethod
    def process(rpc_connection,blknumber):
        commands = [["omni_listblocktransactions",blknumber]]
        txhashes = rpc_connection.batch_(commands)
        transactions = []
        for txhash in txhashes:
            transactions.append(OMNI_GetTransaction.process(rpc_connection,txhash))
        return transactions

    def post(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)#todo-junying-20180325
        try:
            data = OMNI_ListBlockTransActions.process(btc_rpc_connection,self.get_argument("blknumber"))
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetTransaction error:{0} in {1}".format(e,get_linenumber()))
