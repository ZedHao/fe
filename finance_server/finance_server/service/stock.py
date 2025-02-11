from finance_server import  dao

def get_stock_data(stock_name:str, start_date:str, end_date:str):
     return dao.get_bao_stock_data(stock_name, start_date, end_date)