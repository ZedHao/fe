import axios from 'axios';

const API_KEY = 'your_api_key_here'; // 替换为你的 API Key
const BASE_URL = 'https://www.alphavantage.co/query'; // 示例 API
// 模拟的股票数据响应
const mockStockData = {
  "Meta Data": {
    "1. Information": "Daily Time Series with Splits and Dividend Events",
    "2. Symbol": "AAPL",
    "3. Last Refreshed": "2025-02-06",
    "4. Output Size": "Compact",
    "5. Time Zone": "US/Eastern"
  },
  "Time Series (Daily)": {
    "2025-02-06": {
      "1. open": "170.50",
      "2. high": "171.20",
      "3. low": "169.80",
      "4. close": "170.80",
      "5. adjusted close": "170.80",
      "6. volume": "50000000",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    },
    "2025-02-05": {
      "1. open": "171.00",
      "2. high": "172.50",
      "3. low": "170.20",
      "4. close": "171.50",
      "5. adjusted close": "171.50",
      "6. volume": "55000000",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    },
    "2025-02-04": {
      "1. open": "172.00",
      "2. high": "173.00",
      "3. low": "171.50",
      "4. close": "172.20",
      "5. adjusted close": "172.20",
      "6. volume": "60000000",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    },
    "2025-02-03": {
      "1. open": "170.80",
      "2. high": "171.80",
      "3. low": "169.50",
      "4. close": "170.20",
      "5. adjusted close": "170.20",
      "6. volume": "48000000",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    },
    "2025-02-02": {
      "1. open": "171.50",
      "2. high": "172.80",
      "3. low": "170.50",
      "4. close": "172.00",
      "5. adjusted close": "172.00",
      "6. volume": "52000000",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    },
    "2025-01-31": {
      "1. open": "172.20",
      "2. high": "173.50",
      "3. low": "171.80",
      "4. close": "172.80",
      "5. adjusted close": "172.80",
      "6. volume": "58000000",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    },
    "2025-01-30": {
      "1. open": "170.50",
      "2. high": "171.50",
      "3. low": "169.20",
      "4. close": "170.00",
      "5. adjusted close": "170.00",
      "6. volume": "45000000",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    },
    "2025-01-29": {
      "1. open": "171.00",
      "2. high": "172.00",
      "3. low": "170.50",
      "4. close": "171.20",
      "5. adjusted close": "171.20",
      "6. volume": "53000000",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    },
    "2025-01-28": {
      "1. open": "172.50",
      "2. high": "173.80",
      "3. low": "172.00",
      "4. close": "173.00",
      "5. adjusted close": "173.00",
      "6. volume": "62000000",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    },
    "2025-01-27": {
      "1. open": "170.20",
      "2. high": "171.20",
      "3. low": "169.50",
      "4. close": "170.50",
      "5. adjusted close": "170.50",
      "6. volume": "49000000",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    }
  }
};

export default {
  async getStockData(symbol) {
    try {
      return mockStockData
      const response = await axios.get(BASE_URL, {
        params: {
          function: 'TIME_SERIES_DAILY',
          symbol: symbol,
          apikey: API_KEY,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching stock data:', error);
      return null;
    }
  },
};
