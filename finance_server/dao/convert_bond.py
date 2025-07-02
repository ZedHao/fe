from logging import exception

import requests
import json
import pdb
# 请求的 URL
# https://searchadapter.eastmoney.com/api/suggest/get?input=1232&type=14&securitytype=1,2,3,4,8,21,25,27&count=5
# https://searchadapter.eastmoney.com/api/suggest/get?input=1232&type=14&securitytype=1,2,3,4,8,21,25,27&count=3
url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
es_url ='https://searchadapter.eastmoney.com/api/suggest/get'
ReportName = 'RPT_BOND_CB_LIST'
def get_df_cover_bond_data(sort_columns:str,sort_types:int,page_num:int,page_size:int) :
    # 请求参数
    params = {
        'pageSize': page_size,
        'pageNumber': page_num,
        'reportName': ReportName,
        'sortColumns': sort_columns,
        'sortTypes': sort_types,
        'columns': 'ALL',
        'quoteColumns': 'f2~01~CONVERT_STOCK_CODE~CONVERT_STOCK_PRICE,f235~10~SECURITY_CODE~TRANSFER_PRICE,f236~10~SECURITY_CODE~TRANSFER_VALUE,f2~10~SECURITY_CODE~CURRENT_BOND_PRICE,f237~10~SECURITY_CODE~TRANSFER_PREMIUM_RATIO,f239~10~SECURITY_CODE~RESALE_TRIG_PRICE,f240~10~SECURITY_CODE~REDEEM_TRIG_PRICE,f23~01~CONVERT_STOCK_CODE~PBV_RATIO',
    }

    # 发送请求
    response = requests.get(url, params=params)
    response.raise_for_status()  # 检查请求是否成功

    # 处理 JSONP 数据，提取出有效的 JSON 部分
    jsonp_data = response.text
    start_index = jsonp_data.find('{')
    end_index = jsonp_data.rfind('}')
    json_data = jsonp_data[start_index:end_index + 1]

    # 解析 JSON 数据
    data = json.loads(json_data)
    return data


def search_cover_bond_data(cb_name:str,cb_code:int) :
    # 请求参数 ?input=1232&type=14&securitytype=1,2,3,4,8,21,25,27&count=3
    params = {
        'input': cb_name if cb_code == 0 else cb_code,
        'type': 14,
        'count': 3,
        'securitytype':"1,2,3,4,8,21,25,27"
    }
    # 创建请求对象（不发送请求），用于获取构建后的URL
    request = requests.Request('GET', url, params=params)
    prepared_request = request.prepare()

    # 打印完整的请求URL
    print("完整请求URL：", prepared_request.url)
    pdb.set_trace()
    # 若需要发送请求并获取响应，可继续以下操作
    session = requests.Session()
    response = session.send(prepared_request)
    response.raise_for_status()  # 检查请求是否成功
    # 处理 JSONP 数据，提取出有效的 JSON 部分
    jsonp_data = response.text
    start_index = jsonp_data.find('{')
    end_index = jsonp_data.rfind('}')
    json_data = jsonp_data[start_index:end_index + 1]

    # 解析 JSON 数据
    data = json.loads(json_data)
    return data
