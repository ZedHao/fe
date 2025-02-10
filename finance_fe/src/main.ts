import { createApp } from 'vue';
import App from './App.vue';
import './registerServiceWorker';
import router from './router';
import store from './store';
import axios, { AxiosResponse } from 'axios';
import { mockStockData } from './mock/mock.';

// 模拟后端 API，使用响应拦截器
axios.interceptors.response.use((response) => {
  if (response.config.url === '/api/stock-data') {
    return new Promise<AxiosResponse<{ data: typeof mockStockData }>>((resolve) => {
      setTimeout(() => {
        const mockResponse: AxiosResponse<{ data: typeof mockStockData }> = {
          data: { data: mockStockData },
          status: 200,
          statusText: 'OK',
          headers: response.headers,
          config: response.config
        };
        resolve(mockResponse);
      }, 500); // 模拟延迟
    });
  }
  return response;
});

const app = createApp(App);
app.use(store);
app.use(router);
app.mount('#app');
