<template>
  <div class="page">
    <div class="header">
      <div class="header-inner">
        <div class="header-left">
          <img src="/logo.jpg" class="logo-avatar" alt="logo" @error="onLogoError" />
          <div class="header-title">
            <h1><span class="accent">猪猪基金</span><span class="light"> 房地产走势</span></h1>
            <div style="font-size:11px;color:var(--text-dim);">城市房价历史走势 · 数据仅供参考</div>
          </div>
        </div>
        <div class="header-right">
          <span class="update-time" style="font-size:11px;">
            <span class="update-dot" :style="{ display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%', background: 'var(--green)' }"></span>
            <span>{{ utext }}</span>
          </span>
          <router-link to="/" class="btn" style="font-size:11px;padding:6px 10px;">📊 基金折溢价</router-link>
          <router-link to="/futures" class="btn" style="font-size:11px;padding:6px 10px;">📈 期货基差</router-link>
          <router-link to="/perks" class="btn" style="text-decoration:none;font-size:11px;padding:6px 10px;">🎁 股东薅羊毛</router-link>
        </div>
      </div>
    </div>

    <div class="main">
      <div class="city-selector">
        <label for="citySelect">🌆 选择城市</label>
        <select id="citySelect" v-model="city" @change="loadData">
          <option v-for="(name, key) in CITY_NAMES" :key="key" :value="key">{{ name }}</option>
        </select>
        <button class="btn" @click="loadData">📊 查询</button>
      </div>

      <div v-if="errorMsg" class="error-msg">⚠️ {{ errorMsg }}</div>

      <div class="chart-type-tabs">
        <span
          v-for="t in chartTabs"
          :key="t.type"
          class="tab"
          :class="{ active: currentType === t.type }"
          @click="switchType(t.type as 'price' | 'mom' | 'yoy')"
        >{{ t.label }}</span>
      </div>

      <div class="cards">
        <div class="card">
          <div class="label">最新均价</div>
          <div class="value">{{ latestPriceText }}</div>
          <div v-if="latestChangeText" class="change" :class="latestChangeClass">{{ latestChangeText }}</div>
        </div>
        <div class="card">
          <div class="label">近一月</div>
          <div class="value" :class="monthlyChangeClass" style="font-size:20px;">{{ monthlyChangeText }}</div>
        </div>
        <div class="card">
          <div class="label">近一年</div>
          <div class="value" :class="yearlyChangeClass" style="font-size:20px;">{{ yearlyChangeText }}</div>
        </div>
        <div class="card">
          <div class="label">近五年</div>
          <div class="value" :class="fiveYearChangeClass" style="font-size:20px;">{{ fiveYearChangeText }}</div>
        </div>
        <div class="card">
          <div class="label">历史最高</div>
          <div class="value">{{ highPriceText }}</div>
          <div class="change" style="font-size:11px;color:var(--text-dim);">{{ highDateText }}</div>
        </div>
        <div class="card">
          <div class="label">历史最低</div>
          <div class="value">{{ lowPriceText }}</div>
          <div class="change" style="font-size:11px;color:var(--text-dim);">{{ lowDateText }}</div>
        </div>
      </div>

      <div class="chart-wrap">
        <div class="chart-title">
          <span>{{ chartTitle }}</span>
          <span class="hint">数据来源：中国房价行情网</span>
        </div>
        <canvas ref="chartCanvas"></canvas>
      </div>

      <div class="data-table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>月份</th>
              <th>均价 (元/㎡)</th>
              <th>环比</th>
              <th>同比</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in tableRows" :key="p.month">
              <td>{{ p.month }}</td>
              <td style="font-weight:600;">{{ p.price.toLocaleString() }}</td>
              <td>
                <span v-if="p.mom != null" :class="p.mom >= 0 ? 'up' : 'down'">{{ (p.mom >= 0 ? '+' : '') + p.mom.toFixed(2) }}%</span>
                <span v-else style="color:var(--text-muted)">-</span>
              </td>
              <td>
                <span v-if="p.yoy != null" :class="p.yoy >= 0 ? 'up' : 'down'">{{ (p.yoy >= 0 ? '+' : '') + p.yoy.toFixed(2) }}%</span>
                <span v-else style="color:var(--text-muted)">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, shallowRef } from 'vue';
import Chart from 'chart.js/auto';
import type { Chart as ChartInstance } from 'chart.js';
import { getHousePrices } from '@/services/etfApi';
import '@/styles/house.css';

interface PricePoint {
  month: string;
  price: number;
  mom: number | null;
  yoy: number | null;
}

interface HouseData {
  ok?: boolean;
  city: string;
  prices: PricePoint[];
  fetchTime?: string;
  error?: string;
}

const CITY_NAMES: Record<string, string> = {
  shanghai: '上海', suzhou: '苏州', beijing: '北京', shenzhen: '深圳',
  guangzhou: '广州', hangzhou: '杭州', nanjing: '南京', chengdu: '成都',
  wuhan: '武汉', chongqing: '重庆', tianjin: '天津', xiamen: '厦门',
  ningbo: '宁波', qingdao: '青岛', wuxi: '无锡', changsha: '长沙',
  zhengzhou: '郑州', xian: '西安', hefei: '合肥',
};

const chartTabs = [
  { type: 'price', label: '🏠 均价走势' },
  { type: 'mom', label: '📈 环比涨跌' },
  { type: 'yoy', label: '📊 同比涨跌' },
];

const city = ref('suzhou');
const currentType = ref<'price' | 'mom' | 'yoy'>('price');
const currentData = ref<HouseData | null>(null);
const errorMsg = ref('');
const utext = ref('加载中...');
const chartCanvas = ref<HTMLCanvasElement | null>(null);
const chart = shallowRef<ChartInstance | null>(null);

const latestPriceText = ref('--');
const latestChangeText = ref('');
const latestChangeClass = ref('');
const monthlyChangeText = ref('--');
const monthlyChangeClass = ref('');
const yearlyChangeText = ref('--');
const yearlyChangeClass = ref('');
const fiveYearChangeText = ref('--');
const fiveYearChangeClass = ref('');
const highPriceText = ref('--');
const highDateText = ref('');
const lowPriceText = ref('--');
const lowDateText = ref('');
const chartTitle = ref('苏州二手房均价走势');

const tableRows = computed(() => {
  const prices = currentData.value?.prices;
  if (!prices) return [];
  return [...prices].reverse();
});

function onLogoError(e: Event) {
  (e.target as HTMLImageElement).style.display = 'none';
}

function showLoading() {
  errorMsg.value = '';
  latestPriceText.value = '加载中...';
  latestChangeText.value = '';
  monthlyChangeText.value = '--';
  monthlyChangeClass.value = '';
  yearlyChangeText.value = '--';
  yearlyChangeClass.value = '';
  fiveYearChangeText.value = '--';
  fiveYearChangeClass.value = '';
}

function showError(msg: string) {
  errorMsg.value = msg;
  latestPriceText.value = '--';
}

function renderData(data: HouseData) {
  const cityName = CITY_NAMES[data.city] || data.city;
  const prices = data.prices;
  if (!prices || prices.length === 0) {
    showError('暂无该城市房价数据');
    return;
  }

  const latest = prices[prices.length - 1];
  const prev = prices.length > 1 ? prices[prices.length - 2] : null;

  latestPriceText.value = latest.price.toLocaleString();
  if (prev && prev.price > 0) {
    const chg = ((latest.price - prev.price) / prev.price * 100).toFixed(2) + '%';
    latestChangeText.value = chg;
    latestChangeClass.value = latest.price >= prev.price ? 'up' : 'down';
  } else {
    latestChangeText.value = '';
  }

  const idxM1 = prices.length - 2;
  if (idxM1 >= 0) {
    const chg = ((latest.price - prices[idxM1].price) / prices[idxM1].price * 100).toFixed(2);
    monthlyChangeText.value = (Number(chg) >= 0 ? '+' : '') + chg + '%';
    monthlyChangeClass.value = Number(chg) >= 0 ? 'up' : 'down';
  }

  const idxY1 = prices.length - 13;
  if (idxY1 >= 0) {
    const chg = ((latest.price - prices[idxY1].price) / prices[idxY1].price * 100).toFixed(2);
    yearlyChangeText.value = (Number(chg) >= 0 ? '+' : '') + chg + '%';
    yearlyChangeClass.value = Number(chg) >= 0 ? 'up' : 'down';
  }

  const idxY5 = prices.length - 61;
  if (idxY5 >= 0) {
    const chg = ((latest.price - prices[idxY5].price) / prices[idxY5].price * 100).toFixed(2);
    fiveYearChangeText.value = (Number(chg) >= 0 ? '+' : '') + chg + '%';
    fiveYearChangeClass.value = Number(chg) >= 0 ? 'up' : 'down';
  }

  let maxP = prices[0];
  let minP = prices[0];
  for (const p of prices) {
    if (p.price > maxP.price) maxP = p;
    if (p.price < minP.price) minP = p;
  }
  highPriceText.value = maxP.price.toLocaleString();
  highDateText.value = maxP.month;
  lowPriceText.value = minP.price.toLocaleString();
  lowDateText.value = minP.month;

  updateChart(prices, cityName);
}

function updateChart(prices: PricePoint[], cityName: string) {
  const labels = prices.map(p => p.month);
  const values = prices.map(p => p.price);
  const mom = prices.map(p => (p.mom != null ? p.mom : null));
  const yoy = prices.map(p => (p.yoy != null ? p.yoy : null));

  let datasets;
  let title: string;
  const type = currentType.value;

  if (type === 'price') {
    title = `${cityName}二手房均价走势`;
    datasets = [{
      label: '均价 (元/㎡)',
      data: values,
      borderColor: '#4f7eff',
      backgroundColor: 'rgba(79,126,255,0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 1,
      pointHitRadius: 8,
      borderWidth: 2,
    }];
  } else if (type === 'mom') {
    title = `${cityName}二手房均价 · 环比涨跌`;
    datasets = [{
      label: '环比 (%)',
      data: mom,
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245,158,11,0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 1,
      pointHitRadius: 8,
      borderWidth: 2,
    }];
  } else {
    title = `${cityName}二手房均价 · 同比涨跌`;
    datasets = [{
      label: '同比 (%)',
      data: yoy,
      borderColor: '#22c55e',
      backgroundColor: 'rgba(34,197,94,0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 1,
      pointHitRadius: 8,
      borderWidth: 2,
    }];
  }

  chartTitle.value = title;

  nextTick(() => {
    const canvas = chartCanvas.value;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (chart.value) chart.value.destroy();

    chart.value = new Chart(ctx, {
      type: 'line',
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#1e2538',
            titleColor: '#e2e8f0',
            bodyColor: '#e2e8f0',
            borderColor: '#262e3f',
            borderWidth: 1,
            cornerRadius: 8,
            padding: 10,
            callbacks: {
              label(ctx) {
                const val = ctx.raw as number;
                if (currentType.value === 'price') return `均价: ${val.toLocaleString()} 元/㎡`;
                return `${(val >= 0 ? '+' : '')}${val.toFixed(2)}%`;
              },
            },
          },
        },
        scales: {
          x: {
            ticks: { color: '#4a5568', maxTicksLimit: 20, font: { size: 10 } },
            grid: { color: 'rgba(38,46,63,0.3)' },
          },
          y: {
            ticks: {
              color: '#4a5568',
              font: { size: 11 },
              callback(val) {
                if (currentType.value === 'price') return Number(val).toLocaleString();
                return Number(val).toFixed(1) + '%';
              },
            },
            grid: { color: 'rgba(38,46,63,0.3)' },
          },
        },
        interaction: { mode: 'index', intersect: false },
      },
    });
  });
}

function switchType(type: 'price' | 'mom' | 'yoy') {
  currentType.value = type;
  if (currentData.value?.prices) {
    const cityName = CITY_NAMES[currentData.value.city] || currentData.value.city;
    updateChart(currentData.value.prices, cityName);
  }
}

async function loadData() {
  showLoading();
  try {
    const data = await getHousePrices(city.value);
    if (!data.ok) throw new Error(data.error || '获取数据失败');
    currentData.value = data;
    renderData(data);
    if (data.fetchTime) utext.value = data.fetchTime;
  } catch (e) {
    showError(e instanceof Error ? e.message : '获取数据失败');
  }
}

onMounted(loadData);

onUnmounted(() => {
  if (chart.value) chart.value.destroy();
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}
</style>
