import tornado.ioloop
import tornado.web
import tornado.httpserver

from btc.handler import BTC_GetAccount,BTC_GetAccountAddress, BTC_GetNewAddress
from btc.handler import BTC_GetBalance, BTC_GetAccountBalance, BTC_ListAccounts
from btc.handler import BTC_SendFrom
from btc.handler import BTC_ListUTXO, BTC_CreateRawTransaction, BTC_SignRawTransaction, BTC_SendRawTransaction
from btc.handler import BTC_GetRawTransaction, BTC_ListTransActions, BTC_CrawlTxData
from btc.handler import BTC_CreateRawTransactionEx,BTC_SignRawTransactionEx

from usdt.handler import uBTC_GetAccountAddress,uBTC_GetNewAddress
from usdt.handler import uBTC_GetBalance, uBTC_ListUTXO, uBTC_ListAccounts, OMNI_GetBalance, OMNI_Send
from usdt.handler import OMNI_CreateRawTransaction, uBTC_CreateRawTransaction, uBTC_SignRawTransaction, uBTC_SendRawTransaction
from usdt.handler import OMNI_ListTransActions, OMNI_CrawlTxData

from eth.handler import ETH_ListAccounts,ETH_GetBalance,ETH_NewAccount,ETH_SendTransaction
from eth.handler import ETH_CreateRawTransaction, ETH_SignRawTransaction, ETH_SendRawTransaction
from eth.handler import ETH_BlockNumber, ETH_GetTransactionFromBlock, ETH_GetBlockTransactionCount, ETH_GetBlockTransactions, ETH_CrawlTxData
from eth.handler import ETH_GetTransactionByHash,ETH_GetBlockByNumber

from owt.handler import OWT_ListAccounts, OWT_GetBalance, OWT_NewAccount, OWT_SendTransaction
from owt.handler import OWT_CreateRawTransaction, OWT_SignRawTransaction, OWT_SendRawTransaction
from owt.handler import OWT_BlockNumber, OWT_GetTransactionFromBlock, OWT_GetBlockTransactionCount, OWT_GetBlockTransactions, OWT_CrawlTxData
from owt.handler import OWT_GetTransactionByHash,OWT_GetBlockByNumber

from up.handler import UP_ListAccounts, UP_GetBalance, UP_NewAccount, UP_SendTransaction
from up.handler import UP_BlockNumber, UP_GetTransactionByHash, UP_GetBlockByNumber
from up.handler import UP_CreateRawTransaction, UP_SignRawTransaction, UP_SendRawTransaction
from up.handler import UP_BlockNumber, UP_GetTransactionFromBlock, UP_GetBlockTransactionCount, UP_GetBlockTransactions, UP_CrawlTxData
from up.handler import UP_GetTransactionByHash,UP_GetBlockByNumber

from base_handler import BaseHandler

class MainHandler(BaseHandler):
    def get(self):
        self.write("B!tSp@ce Falcon, 2018~")

def make_app():
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/btc/getaccountbalance", BTC_GetAccountBalance),
        (r"/btc/getbalance", BTC_GetBalance),
        (r"/btc/getnewaddress", BTC_GetNewAddress),
        (r"/btc/getaccount", BTC_GetAccount),
        (r"/btc/getaccountaddress", BTC_GetAccountAddress),
        (r"/btc/listaccounts", BTC_ListAccounts),
        (r"/btc/sendfrom", BTC_SendFrom),
        (r"/btc/getunspents", BTC_ListUTXO),
        ############ bitcoin cold wallet #######################
        (r"/btc/createrawtransaction", BTC_CreateRawTransaction),
        (r"/btc/createrawtransactionex", BTC_CreateRawTransactionEx),
        (r"/btc/signrawtransaction", BTC_SignRawTransaction),
        (r"/btc/signrawtransactionex", BTC_SignRawTransactionEx),
        (r"/btc/sendrawtransaction", BTC_SendRawTransaction),
        ############ bitcoin timer #############################
        (r"/btc/listtransactions", BTC_ListTransActions),
        (r"/btc/getrawtransaction", BTC_GetRawTransaction),
        (r"/btc/crawltransactions", BTC_CrawlTxData),
        ############ usdt account ##############################
        (r"/usdt/getnewaddress", uBTC_GetNewAddress),
        (r"/usdt/getaccountaddress", uBTC_GetAccountAddress),
        (r"/usdt/getunspents", uBTC_ListUTXO),
        (r"/usdt/btc/getbalance", uBTC_GetBalance),
        (r"/usdt/getbalance", OMNI_GetBalance),
        (r"/usdt/btc/listaccounts", uBTC_ListAccounts),
        (r"/usdt/send", OMNI_Send),
        ############ usdt timer ################################
        (r"/usdt/listtransactions", OMNI_ListTransActions),
        (r"/usdt/crawltransactions", OMNI_CrawlTxData),
        ############ omni cold wallet ##########################
        (r"/usdt/createrawtransaction", OMNI_CreateRawTransaction),
        (r"/usdt/btc/createrawtransaction", uBTC_CreateRawTransaction),
        (r"/usdt/signrawtransaction", uBTC_SignRawTransaction),
        (r"/usdt/sendrawtransaction", uBTC_SendRawTransaction),
        ############ ethereum account ##########################
        (r"/eth/listaccounts", ETH_ListAccounts),
        (r"/eth/newaccount", ETH_NewAccount),
        (r"/eth/getbalance", ETH_GetBalance),
        (r"/eth/sendtransaction", ETH_SendTransaction),
        ############ ethereum cold wallet ######################
        (r"/eth/createrawtransaction", ETH_CreateRawTransaction),
        (r"/eth/signrawtransaction", ETH_SignRawTransaction),
        (r"/eth/sendrawtransaction", ETH_SendRawTransaction),
        ############ ethereum timer ############################
        (r"/eth/crawltransactions", ETH_CrawlTxData),
        (r"/eth/gettransactions", ETH_GetBlockTransactions),
        (r"/eth/blocknumber", ETH_BlockNumber),
        (r"/eth/blocktransactioncount", ETH_GetBlockTransactionCount),
        (r"/eth/gettransactionfromblock", ETH_GetTransactionFromBlock),
        (r"/eth/getransaction", ETH_GetTransactionByHash),
        (r"/eth/getblock", ETH_GetBlockByNumber),
        ########################################################
        (r"/owt/listaccounts", OWT_ListAccounts),
        (r"/owt/newaccount", OWT_NewAccount),
        (r"/owt/getbalance", OWT_GetBalance),
        (r"/owt/sendtransaction", OWT_SendTransaction),
        ############ owt cold wallet ######################
        (r"/owt/createrawtransaction", OWT_CreateRawTransaction),
        (r"/owt/signrawtransaction", OWT_SignRawTransaction),
        (r"/owt/sendrawtransaction", OWT_SendRawTransaction),
        ############ owt timer ############################
        (r"/owt/crawltransactions", OWT_CrawlTxData),
        (r"/owt/gettransactions", OWT_GetBlockTransactions),
        (r"/owt/blocknumber", OWT_BlockNumber),
        (r"/owt/blocktransactioncount", OWT_GetBlockTransactionCount),
        (r"/owt/gettransactionfromblock", OWT_GetTransactionFromBlock),
        (r"/owt/getransaction", OWT_GetTransactionByHash),
        (r"/owt/getblock", OWT_GetBlockByNumber),
        ########################################################
        (r"/up/listaccounts", UP_ListAccounts),
        (r"/up/newaccount", UP_NewAccount),
        (r"/up/getbalance", UP_GetBalance),
        (r"/up/sendtransaction", UP_SendTransaction),
        (r"/up/getblock", UP_GetBlockByNumber),
        (r"/up/blocknumber", UP_BlockNumber),
        (r"/up/getransaction", UP_GetTransactionByHash),
        ############ up cold wallet ######################
        (r"/up/createrawtransaction", UP_CreateRawTransaction),
        (r"/up/signrawtransaction", UP_SignRawTransaction),
        (r"/up/sendrawtransaction", UP_SendRawTransaction),
        ############ up timer ############################
        (r"/up/crawltransactions", UP_CrawlTxData),
        (r"/up/gettransactions", UP_GetBlockTransactions),
        (r"/up/blocknumber", UP_BlockNumber),
        (r"/up/blocktransactioncount", UP_GetBlockTransactionCount),
        (r"/up/gettransactionfromblock", UP_GetTransactionFromBlock),
        (r"/up/getransaction", UP_GetTransactionByHash),
        (r"/up/getblock", UP_GetBlockByNumber),
    ], debug = True
    )
    return application

def main():
    from constants import PORT
    print('tornado running...')
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app, decompress_request=True)
    http_server.listen(PORT)
    http_server.start(1)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
