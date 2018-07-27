#!/usr/bin/env python
# -*- encoding:utf-8 -*-


# 龙虎榜数据分析系统
# lhb.py @ v0.1
# Ryan @ 2018/07/26

import requests
import sys
import time

REQUEST_TIMEOUT = 10
REQUEST_RETRY = 3
REQUEST_SLEEP = 0.001

REQUEST_ERROR_MSG = '重复请求已达最大次数，无法获取数据！'


def LHB_Daily_Sumary(date):
	print('请求'+date+'龙虎榜信息...')

	#龙虎榜URL，样例：http://data.eastmoney.com/DataCenter_V3/stock2016/TradeDetail/pagesize=200,page=1,sortRule=-1,sortType=,startDate=2018-07-20,endDate=2018-07-20,gpfw=0,js=vardata_tab_1.html
	LHB_URL = '%sdata.%s/DataCenter_V3/stock2016/TradeDetail/pagesize=200,page=1,sortRule=-1,sortType=,startDate=%s,endDate=%s,gpfw=0,js=vardata_tab_1.html'
	url = LHB_URL%('http://', 'eastmoney.com', date, date)
	#print(url)

	for _ in range(REQUEST_RETRY):
		time.sleep(REQUEST_SLEEP)
		try:
			#请求超时5秒，重复请求3次
			#print(str(_+1)+'次尝试请求')
			res = requests.get(url, timeout=REQUEST_TIMEOUT)									
		except requests.exceptions.RequestException as e:
			print(e)
		else:			
			print('成功获取'+date+'数据！')
			return res.text		
	print(REQUEST_ERROR_MSG)
	return None
	


if __name__ == '__main__':
	print('龙虎榜数据分析程序V1.0')

	data = LHB_Daily_Sumary('2018-07-26')
	#print(data)
	
	sys.exit(0)

	

	