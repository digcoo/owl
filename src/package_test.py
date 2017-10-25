import traceback

from vo.StockInfo import *
from utils.TimeUtils import *
from utils.FileUtils import *
from dbs.GeodeClient import *
#from web.RecommendPoolServer import *
from spider.StockListIncSpider import *

def stock_list_inc_start():
    try:

        stock_list_inc_spider = StockListIncSpider()
        stock_list_inc_spider.get_stock_list()

    except Exception, e:
	traceback.print_exc()


if __name__ == '__main__':
    try:

        stock_list_inc_start()

    except Exception, e:
        traceback.print_exc()

