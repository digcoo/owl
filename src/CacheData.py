#encoding=utf-8
import jsonpickle
import traceback

from utils.SinaStockUtils import *
from dbs.GeodeClient import *

class CacheData:
    hist_times = None
    hist_days = None
    hist_weeks = None
    hist_months = None
    morn_hit_symbols = []
    suspend_symbols = []		#今日停盘的票
    market_symbols = []			#正常交易的票
    re_market_symbols = []		#今日复盘的票

    @staticmethod
    def set_hit_symbols(hit_stocks):
	del CacheData.morn_hit_symbols[0:len(CacheData.morn_hit_symbols)]
	for hit_stock in hit_stocks:
	    CacheData.morn_hit_symbols.append(hit_stock[0])


    @staticmethod
    def is_market_open():
	try:
	    stock_day = SinaStockUtils.get_sina_stock_day('sh000001')
	    if stock_day is not None and len(stock_day) > 0 and  stock_day[0].day == TimeUtils.get_current_datestamp():
		return True

	except Exception, e:
	    traceback.print_exc()
	return False


    @staticmethod
    def init():
	try:
	    if CacheData.is_market_open():
		all_symbols = GeodeClient.get_instance().query_all_stock_symbols()
#		LogUtils.info('all_symbols_size = ' + str(len(all_symbols))) 
		all_stocks = GeodeClient.get_instance().query_all_stocks()
#		LogUtils.info('all_stocks_size = ' + str(len(all_stocks)))
		#获取当天数据
		current_stocks_day = SinaStockUtils.get_current_stock_days(all_symbols)
#		LogUtils.info('current_stocks_day_size = ' + str(len(current_stocks_day)))
		#组合当天交易股票(suspend_stocks, market_stocks, re_market_stocks)
		(suspend_stocks, market_stocks, re_market_stocks) = ParseUtil.compose_stocks_market(all_stocks, current_stocks_day)
#		print 'suspend_stocks_size = ' + str(len(CacheData.suspend_stocks))
#		print 'market_stocks_size = ' + str(len(CacheData.market_stocks))
#		print 're_market_stocks_size = ' + str(len(CacheData.re_market_stocks))
#               LogUtils.info('syspend_stocks : ' + jsonpickle.encode(CacheData.suspend_stocks))

		(CacheData.suspend_symbols, CacheData.market_symbols, CacheData.re_market_symbols) = CacheData.compose_symbols(suspend_stocks, market_stocks, re_market_stocks)	
	except Exception, e:
	    traceback.print_exc()

    '''
    @staticmethod
    def compose_stocks_market(all_stocks, current_stocks_day):
	market_symbols = []
	market_stocks = []
	re_market_stocks = []
	suspend_stocks = []
	all_stocks_map = CacheData.compose_stocks_map(all_stocks)
	for current_stock_day in current_stocks_day:
	    update_stock = all_stocks_map[current_stock_day.symbol]
	    update_stock.status = 'on_market'
	    market_symbols.append(current_stock_day.symbol)
	    market_stocks.append(update_stock)

	for stock in all_stocks:
	    if stock.id not in market_symbols:
		update_stock = all_stocks_map[stock.id]
		update_stock.status = 'suspend'
		suspend_stocks.append(all_stocks_map[stock.id])

	    if stock.status == 'suspend' and stock.id in market_symbols:
                update_stock = all_stocks_map[stock.id]
                update_stock.status = 'suspend'
		re_market_stocks.append(update_stock)
	
	return (suspend_stocks, market_stocks, re_market_stocks)
    '''

    @staticmethod
    def compose_symbols(suspend_stocks, market_stocks, re_market_stocks):
	suspend_symbols = []
	market_symbols = []
	re_market_symbols = []
	for stock in suspend_stocks:
	    suspend_symbols.append(stock.id)

	for stock in market_stocks:
	    market_symbols.append(stock.id)

	for stock in re_market_stocks:
	    re_market_symbols.append(stock.id)
	return (suspend_symbols, market_symbols, re_market_symbols)


    @staticmethod
    def compose_stocks_map(all_stocks):
	all_stocks_map = {}
	for stock in all_stocks:
	    all_stocks_map[stock.id] = stock
	return all_stocks_map

if __name__ == '__main__':
    CacheData.init()
#    print CacheData.is_market_open()
