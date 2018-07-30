#!/usr/bin/env python
# -*- encoding:utf-8 -*-


# 龙虎榜数据分析系统
# lhb.py @ v0.1
# Ryan @ 2018/07/26


import requests
import sys,os
import time
import json
import lxml.html
from pandas.compat import StringIO
import MySQLdb
from datetime import date, timedelta


REQUEST_TIMEOUT = 2
REQUEST_RETRY = 30
REQUEST_SLEEP = 0.1

REQUEST_ERROR_MSG = '重复请求已达最大次数，无法获取数据！'


def LHB_Stock_Details(content, date, SCode, DBConnection):
    if content == None:
        return
    insert_value = ''
    content = content.decode('GBK')
    # print(content)
    html = lxml.html.parse(StringIO(content))
    div_list = html.xpath(u"//div[@class=\"content-sepe\"]")
    # for item in div_list:
    # 	print(etree.tostring(item).decode('utf-8'))
    if(len(div_list) < 1):
        print("Not find LHB Table")
        return

    for item_div in div_list:
        table_list = item_div.xpath(u"./table/tbody")
        if (len(table_list) < 1):
            print("Not find LHB table")
            continue

        # print("table count %d"%(len(table_list)))
        for item_t in table_list:
            # print('-------print table content-------')
            # print(etree.tostring(item_t).decode('utf-8'))

            row_list = item_t.xpath(u"./tr")
            if (len(row_list) < 1):
                print("Not find LHB YYB Item")
                continue

            # print('row count %d'%(len(row_list)))
            for item_row in row_list:
                colume_list = item_row.xpath('./td')

                # print(len(colume_list))
                if len(colume_list) == 7:

                    # print(colume_list[0].text)
                    # 营业部名称
                    YYB = (colume_list[1].xpath(
                        "./div[@class=\"sc-name\"]/a"))[1].text
                    # print((colume_list[1].xpath("./div[@class=\"sc-name\"]/a"))[1].text)

                    # 营业部代码
                    YYBID = colume_list[1].xpath(
                        "./div/input")[0].attrib['value']
                    # print(colume_list[1].xpath("./div/input")[0].attrib['value'])
                    if colume_list[1].xpath("./div/input")[0].attrib['value'] == '':
                        YYBID = '10000000'
                        # print("机构席位10000")

                    # 买入金额（万）
                    BUY = colume_list[2].text
                    # print(colume_list[2].text)
                    if colume_list[2].text == None or colume_list[2].text == '-':
                        BUY = '0'

                    # 买入占比
                    BRATE = colume_list[3].text[:-1]
                    # print(colume_list[3].text)
                    if colume_list[3].text == None or colume_list[3].text == '-':
                        BRATE = '0'

                    # 卖出金额（万）
                    SELL = colume_list[4].text
                    # print(colume_list[4].text)
                    if colume_list[4].text == None or colume_list[4].text == '-':
                        SELL = '0'

                    # 卖出占比
                    SRATE = colume_list[5].text[:-1]
                    # print(colume_list[5].text)
                    if colume_list[5].text == None or colume_list[5].text == '-':
                        SRATE = '0'

                    insert_value = insert_value + '(\'%s\',\'%s\',%s,\'%s\',%s,%s,%s,%s),' % (
                        date, SCode, YYBID, YYB, BUY, BRATE, SELL, SRATE)
    try:
        insert_value = insert_value[:-1]
        # print insert_value
        # Insert record
        cursor = DBConnection.cursor()
        insert = 'INSERT INTO LHB(LHBDATE, SCode, YYBID, YYB, BUY, BRATE, SELL, SRATE) VALUES' + insert_value
        # print(insert)
        cursor.execute(insert)
    except Exception:
        #print("%s, %s, %s, %s"%(colume_list[2].text, colume_list[3].text, colume_list[4].text, colume_list[5].text))
        #print("%s, %s, %s, %s"%(BUY, BRATE, SELL, SRATE))
        # print(insert)
        # DBConnection.roolback()
        pass
    else:
        cursor.close()
        DBConnection.commit()
    return


def LHB_Stock_Info(content, date, DBConnection):
    if content == None:
        print('Content load is empty, quit!')
        return
    else:
        content = content.decode('GBK')
        json_raw = content[content.find('_1=') + 3:]
        if json_raw == '':
            print("LHB json content error")
            return
        try:
            json_Dict = json.loads(json_raw, encoding='utf-8')
        except Exception as e:
            print(e)
            print(json_raw)
            return

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
                        #print("第%d次获取失败%s" % (_ + 1, e))
                        pass
                    else:
                        print('成功获取股票代码%s:%s当天的龙虎榜数据！' % (SCode, date))
                        LHB_Stock_Details(res.content, date,
                                          SCode, DBConnection)
                        break
                if _ == REQUEST_RETRY:
                    #print('经过多次尝试：无法获取股票代码%s:%s当天的龙虎榜数据！' % (SCode, date))
                    pass
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
            # print(e)
            pass
        else:
            print('成功获取' + date + '数据！')
            return res.content
    # print(REQUEST_ERROR_MSG)
    return None


def DB_Setup():
    # setup DB connection
    DBConnection = MySQLdb.connect(
        'localhost', 'ryan', 'renyan', 'LHB_DB', charset='utf8')

    # Create Cursor
    cursor = DBConnection.cursor()
    # Create main LHB table
    LHBColume = '(LHBDATE DATE NOT NULL, SCode VARCHAR(6) NOT NULL, 	YYBID INT NOT NULL, YYB VARCHAR(48) NOT NULL, BUY FLOAT, BRATE FLOAT, SELL FLOAT, SRATE FLOAT)'
    CreateLHBTable = 'CREATE TABLE IF NOT EXISTS LHB' + LHBColume
    cursor.execute(CreateLHBTable)
    DBConnection.commit()

    cursor.close
    return DBConnection


def LHB_Start(DBConnection):
    m_date = date.today()
    history = date(2000, 1, 1)

    while history < m_date:

        if m_date.weekday() > 4:
            m_date = m_date - timedelta(days=1)
            continue

        data = LHB_Daily_Sumary(m_date.__str__())
        # print(data)
        LHB_Stock_Info(data, m_date.__str__(), DBConnection)
        m_date = m_date - timedelta(days=1)
    return

def LHBDemo(logger):
    for _ in range(300):
        time.sleep(1)
        logger.info('daeomn process %d'%(os.getpid()))

# if __name__ == '__main__':

#     if sys.version_info[0] < 3:
#         reload(sys)
#         sys.setdefaultencoding('utf-8')

#     print('龙虎榜数据分析程序V1.0')

#     hDB = DB_Setup()
#     LHB_Start(hDB)

#     sys.exit(0)
