import akshare as ak

import requests
import pandas as pd

"""def get_lof_list():
    url = "https://datacenter.eastmoney.com/stock/fundselector/api/data/get?"
    params = {"type": "ETF", "ps": 2000}
    res = requests.get(url, params=params)
    df = pd.DataFrame(res.json()['result']['data'])
    print(df[['SECURITY_CODE', 'SECURITY_NAME', 'PRICE', 'DISCOUNT_RATE']])"""

# 单个 LOF 历史行情（东方财富）
def get_lof_history(symbol):
    df_hist = ak.fund_lof_hist_em(symbol="160222")
    print(df_hist[["日期", "收盘", "成交额"]].tail())

def test(): #使用pip install pandas 
#使用pip install requests
    #行业业绩轮动公众号首发
    import pandas as pd
    import json
    import requests
    def get_all_etf_data():
            '''
            获取全部的etf数据
            '''
            params={
                'type': 'RPTA_APP_FUNDSELECT',
                'sty': 'ETF_TYPE_CODE,SECUCODE,SECURITY_CODE,CHANGE_RATE_1W,CHANGE_RATE_1M,CHANGE_RATE_3M,YTD_CHANGE_RATE,DEC_TOTALSHARE,DEC_NAV,SECURITY_NAME_ABBR,DERIVE_INDEX_CODE,INDEX_CODE,INDEX_NAME,NEW_PRICE,CHANGE_RATE,CHANGE,VOLUME,DEAL_AMOUNT,PREMIUM_DISCOUNT_RATIO,QUANTITY_RELATIVE_RATIO,HIGH_PRICE,LOW_PRICE,STOCK_ID,PRE_CLOSE_PRICE',
                'extraCols':'' ,
                'source': 'FUND_SELECTOR',
                'client': 'APP',
                'sr': '-1,-1,1',
                'st': 'CHANGE_RATE,CHANGE,SECURITY_CODE',
                'filter': '(ETF_TYPE_CODE="ALL")',
                'extraCols': '',
                'p': '1',
                'ps':5,
                'isIndexFilter': '1'
            }
            url='https://datacenter.eastmoney.com/stock/fundselector/api/data/get?'
            res=requests.get(url=url,params=params)
            text=res.json()
    
            df=pd.DataFrame(text['result']['data'])
            print(text['result']['data'][0])
            columns=['_','_','基金代码','周涨跌幅','月涨跌幅','3月涨跌幅','年涨跌幅','市值','现在市值',
            '基金名称','_','_','主题',"价格",'涨跌幅','涨跌额','成交量','成交额','折价率','_',
            "最高价",'最低价','_','前收盘价']
            df.columns=columns
            df['折价率']=df['折价率'].replace('-',0)
            df['折价率']=pd.to_numeric(df['折价率'])
            df['折价率']=df['折价率'].astype(float)
            df['溢价率']=0-df['折价率']
            del df['_']
            '''
            df['实时参考净值']=df['最新价']*(1+df['折价率'])
            df['实时参考涨跌幅']=df['涨跌幅']*(1+df['折价率'])
            df['实时参考净值']=df['实时参考净值'].apply(lambda x:round(x,4))
            df['实时参考涨跌幅']=df['实时参考涨跌幅'].apply(lambda x:round(x,2))
            '''
            return df
    df = get_all_etf_data()
    print(df)


if __name__ == "__main__":
    test()#使用pip install pandas 
