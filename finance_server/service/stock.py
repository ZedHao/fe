#!/usr/bin/env python
import pdb
import pandas as pd
from io import StringIO
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from dao  import  stock,convert_bond
from django.http import JsonResponse

def get_stock_data(request):
   stock_code = request.GET.get('stock_code')
   start_date = request.GET.get('start_date')
   end_date = request.GET.get('end_date')
   # 检查参数是否都存在
   if not all([stock_code, start_date, end_date]):
      return JsonResponse({'error': 'Missing required parameters'}, status=400)
   try:
      ret= stock.get_bao_stock_data(stock_code, start_date, end_date)
   except Exception as e :
      return JsonResponse({'error': f'获取股票数据时发生异常: {str(e)}'}, status=500)

   result_json = ret.to_json(orient='records')
   result_json_obj = pd.read_json(StringIO(result_json), orient='records').to_dict(orient='records')
   response_data = {
      "code": 200,  # 状态码，200 表示成功
      "message": "请求成功",  # 状态描述信息
      "data": result_json_obj  # 实际返回的数据
   }
   resp = JsonResponse(response_data, safe=False)
   logging.error(response_data)
   return    resp


def get_cover_bond_data(request):
   sort_columns = request.GET.get('sort_columns')
   sort_types = request.GET.get('sort_types')
   page_num = request.GET.get('page_num')
   page_size = request.GET.get('page_size')
   #sort_columns:int,sort_types:int,page_num:int,page_size:intsort_columns:int,sort_types:int,page_num:int,page_size:int
   result_json_obj = convert_bond.get_df_cover_bond_data(sort_columns,sort_types,page_num,page_size)
   response_data = {
      "code": 200,  # 状态码，200 表示成功
      "message": "请求成功",  # 状态描述信息
      "data": result_json_obj  # 实际返回的数据
   }
   resp = JsonResponse(response_data, safe=False)
   logging.error(response_data)
   return    resp

