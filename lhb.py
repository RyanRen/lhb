#!/usr/bin/env python
# -*- encoding:utf-8 -*-


# 龙虎榜数据分析系统
# lhb.py @ v0.1
# Ryan @ 2018/07/26


import requests
import sys
import time
import json
import lxml.html
from lxml import etree
from pandas.compat import StringIO
import MySQLdb
from datetime import date, timedelta


REQUEST_TIMEOUT = 10
REQUEST_RETRY = 3
REQUEST_SLEEP = 0.001

REQUEST_ERROR_MSG = '重复请求已达最大次数，无法获取数据！'


def LHB_Stock_Details(content, date):
    content = content.decode('GBK')
    # print(content)
    html = lxml.html.parse(StringIO(content))
    div_list = html.xpath(u"//div[@class=\"content-sepe\"]")
    # for item in div_list:
    # 	print(etree.tostring(item).decode('utf-8'))

    for item_div in div_list:
        table_list = item_div.xpath(u"./table/tbody")
        # print("table count %d"%(len(table_list)))
        for item_t in table_list:
            # print('-------print table content-------')
            # print(etree.tostring(item_t).decode('utf-8'))
            # item_t = lxml.html.parse(StringIO(etree.tostring(item_t).decode('utf-8')))
            row_list = item_t.xpath(u"./tr")
            # print('row count %d'%(len(row_list)))
            for item_row in row_list:
                colume_list = item_row.xpath('./td')

                # print(len(colume_list))
                if len(colume_list) == 7:

                    # print(colume_list[0].text)
                    # 营业部名称
                    print((colume_list[1].xpath(
                        "./div[@class=\"sc-name\"]/a"))[1].text)
                    # 营业部代码
                    # item = colume_list[1].xpath("./div/input")
                    print(colume_list[1].xpath(
                        "./div/input")[0].attrib['value'])
                    if colume_list[1].xpath("./div/input")[0].attrib['value'] == '':
                        print("机构席位10000")
                    # 买入金额（万）
                    print(colume_list[2].text)
                    if(colume_list[2] == None):
                        BMoney = 0

                    # 买入占比
                    print(colume_list[3].text)

                    # 卖出金额（万）
                    print(colume_list[4].text)

                    # 卖出占比
                    print(colume_list[5].text)

    return


def LHB_Stock_Info(content, date):
    if content == None:
        print('Content load is empty, quit!')
        return
    else:
        json_raw = content[content.find('_1=') + 3:]
        # print(json_raw)
        json_Dict = json.loads(json_raw, encoding='utf-8')
        # print(json_Dict)
        if json_Dict['data'] != '':
            for item in json_Dict['data']:
                SCode = item['SCode']
                # print('**股票%s**上榜原因:%s'%(item['SCode'], item['Ctypedes']))
                # 龙虎榜个股信息URL：http://data.eastmoney.com/stock/lhb,2018-07-26,600186.html
                LHB_STOCK_URL = '%sdata.%s/stock/lhb,%s,%s.html'
                url = LHB_STOCK_URL % ('http://', 'eastmoney.com', date, SCode)
                # print(url)
                for _ in range(REQUEST_RETRY):
                    time.sleep(REQUEST_SLEEP)
                    try:
                        res = requests.get(url, timeout=REQUEST_TIMEOUT)
                        # res = requests.get(url, timeout=0.001)

                    except requests.exceptions.RequestException as e:
                        print("第%d次获取失败%s" % (_ + 1, e))
                    else:
                        print('成功获取股票代码%s:%s当天的龙虎榜数据！' % (SCode, date))
                        LHB_Stock_Details(res.content, date)
                        break
                    if _ == 2:
                        print('经过多次尝试：无法获取股票代码%s:%s当天的龙虎榜数据！' % (SCode, date))
    return


def LHB_Daily_Sumary(date):
    print('请求' + date + '龙虎榜信息...')

    # 龙虎榜URL，样例：http://data.eastmoney.com/DataCenter_V3/stock2016/TradeDetail/pagesize=200,page=1,sortRule=-1,sortType=,startDate=2018-07-20,endDate=2018-07-20,gpfw=0,js=vardata_tab_1.html
    LHB_URL = '%sdata.%s/DataCenter_V3/stock2016/TradeDetail/pagesize=200,page=1,sortRule=-1,sortType=,startDate=%s,endDate=%s,gpfw=0,js=vardata_tab_1.html'
    url = LHB_URL % ('http://', 'eastmoney.com', date, date)
    # print(url)

    for _ in range(REQUEST_RETRY):
        time.sleep(REQUEST_SLEEP)
        try:
            # 请求超时5秒，重复请求3次
            # print(str(_+1)+'次尝试请求')
            res = requests.get(url, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            print(e)
        else:
            print('成功获取' + date + '数据！')
            return res.text
    print(REQUEST_ERROR_MSG)
    return None


def DB_Setup():
	DBConnection = MySQLdb.connect(
	    'localhost', 'ryan', 'renyan', 'lhbDB', charset='utf8')
	return

def LHB_Start():
    m_date = date.today()
    history = date(2000,1,1)   

    while history < m_date:        

        if m_date.weekday() > 4:
            m_date = m_date - timedelta(days=1)
            continue

        data = LHB_Daily_Sumary(m_date.__str__())
        #print(data)
        LHB_Stock_Info(data, m_date.__str__())
        m_date = m_date - timedelta(days=1)
        



if __name__ == '__main__':
    
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    print('龙虎榜数据分析程序V1.0')

    

    LHB_Start()

    sys.exit(0)
