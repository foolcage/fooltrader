import pandas as pd
from functools import reduce
from fooltrader.contract.files_contract import *
import re
import json

class agg_future_dayk(object):
    funcs={}

    def __init__(self):
        self.funcs['shfeh']=self.getShfeHisData
        self.funcs['shfec']=self.getShfeCurrentYearData
        self.funcs['dceh']=self.getDceHisData
        self.funcs['dcec']=self.getDceCurrentYearData
        self.funcs['czceh']=self.getCzceHisData
        self.funcs['czcec']=self.getCzceCurrentYearData
        self.funcs['cffexh']=self.getCffexHisData
        self.funcs['cffexc']=self.getCffexCurrentYearData

    def getAllData(self,exchange):
        finalpd= pd.concat([self.getHisData(exchange),self.getCurrentYearData(exchange)])
        finalpd.set_index(['date','fproduct','symbol'],inplace=True)
        finalpd.sort_index(inplace=True)
        return finalpd

    def getHisData(self,exchange):
        return self.funcs[exchange+'h']()

    def getCurrentYearData(self,exchange):
        return self.funcs[exchange+'c']()

    def getShfeHisData(self):
        pattern = re.compile(r'(\D{1,3})(\d{3,4})')
        dfs=[]
        for i in range(2009,2017):
            dir = get_exchange_cache_dir(security_type='future',exchange='shfe')+"/"
            a=pd.read_excel(dir+str(i)+'_shfe_history_data.xls',header=2,skipfooter=5,usecols=list(range(0,14))).fillna(method='ffill')
            dfs.append(a)
        totaldf = reduce(lambda x,y:x.append(y),dfs)
        totaldf['日期']=pd.to_datetime(totaldf['日期'],format='%Y%m%d')
        totaldf['fproduct'] = totaldf['合约'].apply(lambda x:pattern.match(x).groups()[0])
        totaldf['settleDate'] = totaldf['合约'].apply(lambda x:pd.to_datetime('20'+pattern.match(x).groups()[1],format='%Y%m'))
        renameMap={
            '合约':'symbol',
            '日期':'date',
            '前收盘':'preClose',
            '前结算':'preSettle',
            '开盘价':'open',
            '最高价':'high',
            '最低价':'low',
            '收盘价':'close',
            '结算价':'settle',
            '涨跌1':'range',
            '涨跌2':'range2',
            '成交量':'volume',
            '成交金额':'amount',
            '持仓量':'inventory'
        }
        totaldf.rename(index=str,columns=renameMap,inplace=True)
        totaldf=totaldf[['symbol','date','open','high','low','close','settle','range','range2','volume','inventory','fproduct','settleDate']]
        print("done")
        # totaldf.to_pickle('testdf.pickle')
        return totaldf

    def getShfeCurrentYearData(self):
        dir = os.path.join(get_exchange_cache_dir(security_type='future',exchange='shfe'),"2018_day_kdata")
        file_list=os.listdir(dir)
        tempdfs=[]
        for file in file_list:
            with open(os.path.join(dir,file)) as f:
                load_dict = json.load(f)
                temp_df = pd.DataFrame(data=load_dict['o_curinstrument'])
                temp_df['date'] = file
                temp_df['date'] = pd.to_datetime(temp_df['date'],format="%Y%m%d")
                tempdfs.append(temp_df)
        aggdf=pd.concat(tempdfs)
        aggdf= aggdf[aggdf['DELIVERYMONTH']!='小计' ]
        aggdf= aggdf[aggdf['DELIVERYMONTH']!=""]
        aggdf= aggdf[aggdf['DELIVERYMONTH']!="efp"]
        aggdf['symbol']=aggdf['PRODUCTID'].apply(lambda x:x.strip().replace("_f",""))+aggdf['DELIVERYMONTH']
        aggdf['fproduct']=aggdf['PRODUCTID'].apply(lambda x:x.strip().replace("_f",""))
        aggdf['settleDate']=aggdf['DELIVERYMONTH'].apply(lambda x:pd.to_datetime('20'+x,format='%Y%m'))

        renameMap={
            'OPENPRICE':'open',
            'HIGHESTPRICE':'high',
            'LOWESTPRICE':'low',
            'CLOSEPRICE':'close',
            'SETTLEMENTPRICE':'settle',
            'ZD1_CHG':'range',
            'ZD2_CHG':'range2',
            'VOLUME':'volume',
            'OPENINTEREST':'inventory'
        }
        aggdf.rename(index=str,columns=renameMap,inplace=True)
        aggdf=aggdf[['symbol','date','open','high','low','close','settle','range','range2','volume','inventory','fproduct','settleDate']]
        return aggdf


    def getDceHisData(self):
        pattern = re.compile(r'(\D{1,3})(\d{3,4})')
        dir = os.path.join(get_exchange_cache_dir(security_type='future',exchange='dce'),"his")
        file_list=os.listdir(dir)
        tempdfs=[]
        for file in file_list:
            if file.endswith('csv') and not file.startswith('2018'):
                temp_df = pd.read_csv(os.path.join(dir,file),encoding='gbk')
                tempdfs.append(temp_df)
            if file.startswith('2018'):
                temp_df = pd.read_excel(os.path.join(dir,file))
                tempdfs.append(temp_df)
        totaldf=pd.concat(tempdfs,sort=True)
        totaldf['日期']=pd.to_datetime(totaldf['日期'],format='%Y%m%d')
        totaldf['fproduct'] = totaldf['合约'].apply(lambda x:pattern.match(x).groups()[0])
        totaldf['settleDate'] = totaldf['合约'].apply(lambda x:pd.to_datetime('20'+pattern.match(x).groups()[1],format='%Y%m'))
        renameMap={
            '合约':'symbol',
            '日期':'date',
            '前收盘价':'preClose',
            '前结算价':'preSettle',
            '开盘价':'open',
            '最高价':'high',
            '最低价':'low',
            '收盘价':'close',
            '结算价':'settle',
            '涨跌1':'range',
            '涨跌2':'range2',
            '成交量':'volume',
            '成交金额':'amount',
            '持仓量':'inventory'
        }
        totaldf.rename(index=str,columns=renameMap,inplace=True)
        totaldf=totaldf[['symbol','date','open','high','low','close','settle','range','range2','volume','inventory','fproduct','settleDate']]
        # totaldf.to_pickle('testdf.pickle')
        return totaldf

    def getDceCurrentYearData(self):
        dir = os.path.join(get_exchange_cache_dir(security_type='future',exchange='dce'),"2018_day_kdata")
        file_list=os.listdir(dir)
        tempdfs=[]
        symbolMap={
            '豆一':'a',
            '豆二':'b',
            '胶合板':'bb',
            '玉米':'c',
            '玉米淀粉':'cs',
            '纤维板':'fb',
            '铁矿石':'i',
            '焦炭':'j',
            '鸡蛋':'jd',
            '焦煤':'jm',
            '聚乙烯':'l',
            '豆粕':'m',
            '棕榈油':'p',
            '聚丙烯':'pp',
            '聚氯乙烯':'v',
            '豆油':'y'
        }
        for file in file_list:
            temp_df = pd.read_csv(os.path.join(dir,file),delim_whitespace=True)
            temp_df['date']=pd.to_datetime(file.split(".")[0],format='%Y%m%d')
            tempdfs.append(temp_df)
        aggdf=pd.concat(tempdfs)
        aggdf=aggdf[lambda x: x['商品名称'].apply(lambda y: not y.endswith('计'))]
        # aggdf['symbol']=aggdf['PRODUCTID'].apply(lambda x:x.strip().replace("_f",""))+aggdf['DELIVERYMONTH']
        # aggdf['fproduct']=aggdf['商品名称'].replace(to_replace=symbolMap,value=None)
        aggdf=aggdf.replace(to_replace={'商品名称':symbolMap},value=None)
        aggdf['settleDate']=aggdf['交割月份'].apply(lambda x:pd.to_datetime('20'+x,format='%Y%m'))
        aggdf['symbol']=aggdf['商品名称']+aggdf['交割月份']
        renameMap={
            '开盘价':'open',
            '商品名称':'fproduct',
            '最高价':'high',
            '最低价':'low',
            '收盘价':'close',
            '结算价':'settle',
            '涨跌':'range',
            '涨跌1':'range2',
            '成交量':'volume',
            '持仓量':'inventory'
        }
        aggdf.rename(index=str,columns=renameMap,inplace=True)
        aggdf=aggdf[['symbol','date','open','high','low','close','settle','range','range2','volume','inventory','fproduct','settleDate']]
        return aggdf

    def getCzceHisData(self):
        pattern = re.compile(r'(\D{1,3})(\d{3,4})')
        dir = os.path.join(get_exchange_cache_dir(security_type='future',exchange='czce'),"his")
        file_list=os.listdir(dir)
        tempdfs=[]
        for file in file_list:
            temp_df=pd.read_table(os.path.join(dir,file), header=1, encoding='gbk', sep='\s*\|')
            temp_df.rename(index=str,columns={'品种月份':'品种代码'},inplace=True)
            tempdfs.append(temp_df)
        totaldf=pd.concat(tempdfs,sort=True)
        totaldf['date']=pd.to_datetime(totaldf['交易日期'],format='%Y-%m-%d')
        totaldf['fproduct'] = totaldf['品种代码'].apply(lambda x:pattern.match(x).groups()[0])
        totaldf['settleDate'] = totaldf['品种代码'].apply(lambda x:pd.to_datetime('201'+pattern.match(x).groups()[1],format='%Y%m'))
        renameMap={
            '品种代码':'symbol',
            '今开盘':'open',
            '最高价':'high',
            '最低价':'low',
            '今收盘':'close',
            '今结算':'settle',
            '涨跌1':'range',
            '涨跌2':'range2',
            '成交量(手)':'volume',
            '空盘量':'inventory'
        }
        totaldf.rename(index=str,columns=renameMap,inplace=True)
        totaldf=totaldf[['symbol','date','open','high','low','close','settle','range','range2','volume','inventory','fproduct','settleDate']]
        # totaldf.to_pickle('testdf.pickle')
        return totaldf


    def getCzceCurrentYearData(self):
        pattern = re.compile(r'(\D{1,3})(\d{3,4})')
        dir = os.path.join(get_exchange_cache_dir(security_type='future',exchange='czce'),"2018_day_kdata")
        file_list=os.listdir(dir)
        tempdfs=[]
        for file in file_list:
            temp_df = pd.read_excel(os.path.join(dir,file),header=1)
            temp_df['date']=pd.to_datetime(file.split(".")[0],format='%Y%m%d')
            temp_df.rename(index=str,columns={'品种月份':'品种代码'},inplace=True)
            tempdfs.append(temp_df)
        aggdf=pd.concat(tempdfs)
        aggdf=aggdf[lambda x: x['品种代码'].apply(lambda y: not y.endswith('计'))]
        aggdf['fproduct'] = aggdf['品种代码'].apply(lambda x:pattern.match(x).groups()[0])
        aggdf['settleDate'] = aggdf['品种代码'].apply(lambda x:pd.to_datetime('201'+pattern.match(x).groups()[1],format='%Y%m'))
        renameMap={
            '品种代码':'symbol',
            '今开盘':'open',
            '最高价':'high',
            '最低价':'low',
            '今收盘':'close',
            '今结算':'settle',
            '涨跌1':'range',
            '涨跌2':'range2',
            '成交量(手)':'volume',
            '空盘量':'inventory'
        }
        aggdf.rename(index=str,columns=renameMap,inplace=True)
        aggdf=aggdf[['symbol','date','open','high','low','close','settle','range','range2','volume','inventory','fproduct','settleDate']]
        return aggdf

    def getCffexYearData(self,year):
        pattern = re.compile(r'(\D{1,3})(\d{3,4})')
        dir = os.path.join(get_exchange_cache_dir(security_type='future',exchange='cffex'),str(year)+"_day_kdata")
        file_list=os.listdir(dir)
        tempdfs=[]
        for file in file_list:
            temp_df = pd.read_csv(os.path.join(dir,file),encoding='gbk',sep='\s*\,')
            temp_df['date']=pd.to_datetime(file.split(".")[0],format='%Y%m%d')
            temp_df.rename(index=str,columns={'合约代码':'品种代码'},inplace=True)
            tempdfs.append(temp_df)
        aggdf=pd.concat(tempdfs)
        aggdf=aggdf[lambda x: x['品种代码'].apply(lambda y: not y.endswith('计'))]
        aggdf['fproduct'] = aggdf['品种代码'].apply(lambda x:pattern.match(x).groups()[0])
        aggdf['settleDate'] = aggdf['品种代码'].apply(lambda x:pd.to_datetime('20'+pattern.match(x).groups()[1],format='%Y%m'))
        renameMap={
            '品种代码':'symbol',
            '今开盘':'open',
            '最高价':'high',
            '最低价':'low',
            '今收盘':'close',
            '今结算':'settle',
            '涨跌1':'range',
            '涨跌2':'range2',
            '成交量':'volume',
            '持仓量':'inventory'
        }
        aggdf.rename(index=str,columns=renameMap,inplace=True)
        aggdf=aggdf[['symbol','date','open','high','low','close','settle','range','range2','volume','inventory','fproduct','settleDate']]
        return aggdf

    def getCffexCurrentYearData(self):
        return self.getCffexYearData(pd.Timestamp.today().year)

    def getCffexHisData(self):
        tempdfs=[]
        for year in range(2010,pd.Timestamp.today().year):
            tempdfs.append(self.getCffexYearData(year))
        return pd.concat(tempdfs)
