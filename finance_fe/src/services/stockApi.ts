import axios from 'axios';

const BASE_URL = 'http://localhost:9000/'; // 示例 API

export async function getStockData(stockCode: string, startDate: string, endDate: string) {
  try {
    const queryParams = new URLSearchParams({
      stock_code: stockCode,
      start_date: startDate,
      end_date: endDate
    }).toString();
    const url = `${BASE_URL}get_stock/?${queryParams}`;

    const response = await axios.get(url, { timeout: 5000 }); // 设置超时时间为 5 秒
    return response.data.data;
  } catch (error) {
    throw new Error(`获取股票数据失败: ${error}`);
  }
}

export async function getCoverBondData(sort_columns: string, sort_types: string, page_num: string,page_size:string) {
  // sort_columns = request.GET.get('sort_columns')
  //    sort_types = request.GET.get('sort_types')
  //    page_num = request.GET.get('page_num')
  //    page_size = request.GET.get('page_size')
  try {
    const queryParams = new URLSearchParams({
      sort_columns: sort_columns,
      sort_types: sort_types,
      page_num:page_num,
      page_size:page_size
    }).toString();
    const url = `${BASE_URL}get_covert_bond/?${queryParams}`;

    const response = await axios.get(url, { timeout: 5000 }); // 设置超时时间为 5 秒
    console.info('-------getCoverBondData resp data:', response);
    return response.data;
  } catch (error) {
    console.info('-------getCoverBondData resp error:', error);
    return null;
  }
}
