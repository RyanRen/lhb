#!/usr/bin/env python
# -*- encoding:utf-8 -*-


# 龙虎榜数据分析系统
# lhb.py @ v0.1
# Ryan @ 2018/07/26


import requests
import sys
import time
import json

REQUEST_TIMEOUT = 10
REQUEST_RETRY = 3
REQUEST_SLEEP = 0.001

REQUEST_ERROR_MSG = '重复请求已达最大次数，无法获取数据！'

def LHB_Stock_Info(content, date):
	if content == None:
		print('Content load is empty, quit!')
		return 
	else:
		json_raw = content[content.find('_1=')+3:]
		#print(json_raw)
		json_Dict = json.loads(json_raw, encoding='utf-8')
		#print(json_Dict)
		if json_Dict['data'] != '':
			for item in json_Dict['data']:
				SCode = item['SCode']
				#print('**股票%s**上榜原因:%s'%(item['SCode'], item['Ctypedes']))
				#龙虎榜个股信息URL：http://data.eastmoney.com/stock/lhb,2018-07-26,600186.html
				LHB_STOCK_URL = '%sdata.%s/stock/lhb,%s,%s.html'
				url = LHB_STOCK_URL%('http://', 'eastmoney.com', date, SCode)
				#print(url)
				for _ in range(REQUEST_RETRY):
					time.sleep(REQUEST_SLEEP)
					try:
						res = requests.get(url, timeout=REQUEST_TIMEOUT)
						#res = requests.get(url, timeout=0.001)
					except requests.exceptions.RequestException as e:
						print(e)
					else:			
						print('成功获取股票代码%s:%s当天的龙虎榜数据！'%(SCode,date))
						break
					if _==2:
						print('经过多次尝试：无法获取股票代码%s:%s当天的龙虎榜数据！'%(SCode,date))
	return


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
	LHB_Stock_Info(data, '2018-07-26')
	
	sys.exit(0)

	

	