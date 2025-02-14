<template>
  <div class="stock-page">
    <Header />
    <div class="search-section">
      <input
        v-model="stockCode"
        type="text"
        placeholder="输入股票名称或代码"
        class="search-input"
      />
      <div>
        <span @click="showStartDatePicker = true">开始时间：{{ startDate }}</span>
        <div v-show="showStartDatePicker" class="date-picker-popup">
          <input
            v-model="startDate"
            type="date"
            class="date-input"
          />
          <button @click="showStartDatePicker = false">确定</button>
          <button @click="cancelDateSelection('start')">取消</button>
        </div>
      </div>
      <div>
        <span @click="showEndDatePicker = true">结束时间：{{ endDate }}</span>
        <div v-show="showEndDatePicker" class="date-picker-popup">
          <input
            v-model="endDate"
            type="date"
            class="date-input"
          />
          <button @click="showEndDatePicker = false">确定</button>
          <button @click="cancelDateSelection('end')">取消</button>
        </div>
      </div>
      <button @click="searchStocks" class="search-button">搜索</button>
    </div>
    <div class="table-section">
      <table v-if="stockData.length > 0" class="stock-table">
        <thead>
        <tr>
          <th>日期</th>
          <th>股票</th>
          <th>股票代码</th>
          <th>开盘价</th>
          <th>最高价</th>
          <th>最低价</th>
          <th>收盘价</th>
          <th>前收盘价</th>
          <th>成交量</th>
          <th>成交额</th>
          <th>涨跌幅</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(item, index) in stockData" :key="index">
          <td>{{ item.date }}</td>
          <td>{{ item.stock_name}}</td>
          <td>{{ item.code }}</td>
          <td>{{ item.open }}</td>
          <td>{{ item.high }}</td>
          <td>{{ item.low }}</td>
          <td>{{ item.close }}</td>
          <td>{{ item.preclose }}</td>
          <td>{{ item.volume }}</td>
          <td>{{ item.amount }}</td>
          <td>{{ item.pctChg }}%</td>
        </tr>
        </tbody>
      </table>
      <p v-else class="no-data">暂无数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Header from '@/components/Header.vue';
import {getStockData} from '../services/stockApi';

// 定义响应式数据
const stockCode = ref('');
const showStartDatePicker = ref(false);
const showEndDatePicker = ref(false);
const startDate = ref(getDefaultStartDate());
const endDate = ref(getDefaultEndDate());
const stockData = ref([]);

// 获取默认开始日期
function getDefaultStartDate() {
  const date = new Date();
  date.setDate(date.getDate() - 7);
  return date.toISOString().split('T')[0];
}

// 获取默认结束日期
function getDefaultEndDate() {
  return new Date().toISOString().split('T')[0];
}

// 取消日期选择
function cancelDateSelection(type: 'start' | 'end') {
  if (type === 'start') {
    startDate.value = getDefaultStartDate();
    showStartDatePicker.value = false;
  } else {
    endDate.value = getDefaultEndDate();
    showEndDatePicker.value = false;
  }
}

// 搜索股票数据的方法
async function searchStocks() {
  try {
    console.log(typeof getStockData); // 检查类型

    const response = await getStockData(stockCode.value,startDate.value,endDate.value)
    stockData.value = response;
  } catch (error) {
    console.error('搜索失败:', error);
  }
}
</script>

<style scoped>
.stock-page {
  padding: 20px;
  background-color: #0d0d0d;
  color: #fff;
  min-height: 100vh;
}

.search-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input,
.date-input {
  padding: 10px;
  border: 1px solid #444;
  border-radius: 5px;
  background-color: #1a1a1a;
  color: #fff;
}

.search-button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #00ffcc;
  color: #000;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: #00ccaa;
}

.table-section {
  overflow-x: auto;
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #1a1a1a;
  color: #fff;
}

.stock-table th,
.stock-table td {
  padding: 12px;
  border: 1px solid #444;
  text-align: center;
}

.stock-table th {
  background-color: #00ffcc;
  color: #000;
}

.stock-table tr:hover {
  background-color: #333;
}

.no-data {
  text-align: center;
  color: #ccc;
}

.date-picker-popup {
  position: absolute;
  background-color: #1a1a1a;
  padding: 10px;
  border: 1px solid #444;
  border-radius: 5px;
  z-index: 1;
}

.date-picker-popup button {
  margin-top: 10px;
  margin-right: 5px;
}
</style>
