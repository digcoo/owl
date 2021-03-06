# encoding=utf-8
from sys import path
path.append('/home/ubuntu/scripts/quant')
path.append('/home/ubuntu/scripts/utils')
path.append('/home/ubuntu/scripts/vo')
import time
import traceback
import jsonpickle as json
from BaseStockUtils import *
from GeodeClient import *
from CommonUtils import *
from IndicatorUtils import *

'''
1、昨天吊T模型:T
'''
class ModelT:

    def __init__(self, hist_days, todaystamp):
	self.todaystamp = todaystamp
        self.cache_hist_days = hist_days      
        self.candidate_stocks = self.prepare_candidate_stocks()
#	print 'model_t candidate : ' + json.encode(self.candidate_stocks)

    def prepare_candidate_stocks(self):
	candidate_stocks = {}
	for symbol in self.cache_hist_days.keys():
            hist_days = self.cache_hist_days[symbol]
	    hit = self.match_candidate_model(hist_days)
	    if hit is not None:
		candidate_stocks[symbol] = hit
	return candidate_stocks

    # todo : 模型计算 
    def match_candidate_model(self, hist_days):
	try:
	    if hist_days is not None and len(hist_days) > 0:
		return self.T(hist_days)
	except Exception, e:
	    print e
	return None


    #上吊线
    def T(self, hist_days):
	try:
	    last1_upper_shadow = BaseStockUtils.pre_upper_shadow(hist_days, 1, self.todaystamp)		#上影线
	    last1_lower_shadow = BaseStockUtils.pre_lower_shadow(hist_days, 1, self.todaystamp)		#下影线
            last1_column_shadow = BaseStockUtils.pre_column_shadow(hist_days, 1, self.todaystamp)		#实体柱
	    last1_is_red = BaseStockUtils.pre_is_red(hist_days, 1, self.todaystamp)				#昨日收红
	    last1_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)

	    is_candidate = True
	    is_candidate = is_candidate & (last1_lower_shadow > 0.016)			#下影线
	    is_candidate = is_candidate & ((last1_upper_shadow < 0.015) & (last1_upper_shadow < 0.5 *last1_lower_shadow))			#上影线
#	    is_candidate = is_candidate & (last1_column_shadow > last1_upper_shadow)	#实体柱
	    is_candidate = is_candidate & (last1_stock_day.close > 0.997 * last1_stock_day.op)	#收盘价	
#	    is_candidate = is_candidate & (last1_is_red)    #昨日收红

	    if is_candidate:
                return ('TT', )
	except Exception, e:
	    return None


    def match(self, realtime_stock_day):
	try:

            if realtime_stock_day.symbol not in self.candidate_stocks.keys():
                return None

	    hist_days = self.cache_hist_days.get(realtime_stock_day.symbol)

	    last_stock_day = BaseStockUtils.pre_stock_day(hist_days, 1, self.todaystamp)

	    if last_stock_day is None:
		return None

	    above_pressure_ma = IndicatorUtils.above_pressure_ma_tup(hist_days, self.todaystamp, realtime_stock_day.close)

            is_hit = True
            #is_hit = is_hit & (realtime_stock_day.op > 0.997 * last_stock_day.close)         #高开 
            is_hit = is_hit & (realtime_stock_day.close > realtime_stock_day.op)                #当前价高于开盘价
            is_hit = is_hit & (realtime_stock_day.close > 1.004 * last_stock_day.close)         #当前价高于昨天收盘价
            is_hit = is_hit & (realtime_stock_day.close > round(realtime_stock_day.money/realtime_stock_day.vol, 5))         #当前价高于均价
#	    is_hit = is_hit & (BaseStockUtils.change_shadow2(realtime_stock_day) < 0.055)	#涨幅
	    is_hit = is_hit & (abs(BaseStockUtils.lower_shadow(realtime_stock_day)) < 0.015)             #下影线
	    is_hit = is_hit & (realtime_stock_day.close > IndicatorUtils.MA(hist_days, 5, self.todaystamp))     #当前价高于MA5
#	    is_hit = is_hit & (above_pressure_ma is None or realtime_stock_day.close < 0.99 * above_pressure_ma[1])     #当前价偏离上方阻力位

            if is_hit:
		return (self.candidate_stocks[realtime_stock_day.symbol][0] + '-0', )

	except Exception, e:
	    traceback.print_exc()
	return None
