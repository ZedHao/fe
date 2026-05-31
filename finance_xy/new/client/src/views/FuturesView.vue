<template>
  <div class="page">
    <div class="header">
      <div class="header-inner">
        <div class="header-left">
          <img src="/logo.jpg" class="logo-avatar" alt="猪猪" />
          <div class="header-title">
            <h1><span class="accent">猪猪期货</span><span class="sub"> 贴水基差查询</span></h1>
            <div class="sub">国内期货主力合约 · 使用新浪K线数据</div>
          </div>
        </div>
        <div class="header-right">
          <span class="update-time">
            <span class="update-dot" :class="dotClass"></span>
            <span>{{ utext }}</span>
          </span>
          <router-link to="/" class="btn" style="font-size:11px;padding:6px 10px;background:var(--accent);">📊 基金折溢价</router-link>
          <router-link to="/futures" class="btn" style="font-size:11px;padding:6px 10px;background:linear-gradient(135deg,#6366f1,#8b5cf6);">📈 期货基差</router-link>
          <router-link to="/perks" class="btn" style="text-decoration:none;font-size:11px;padding:6px 10px;background:linear-gradient(135deg,#f59e0b,#ef4444);">🎁 股东薅羊毛</router-link>
          <button class="btn" style="font-size:11px;padding:6px 10px;" @click="loadData">🔄 刷新</button>
        </div>
      </div>
    </div>

    <div class="main">
      <div class="toolbar">
        <div class="search-wrap">
          <span class="icon">🔍</span>
          <input v-model="searchInput" type="text" placeholder="搜品种代码/名称..." autocomplete="off" @input="applyFilter" />
        </div>
        <select v-model="ftype" @change="applyFilter">
          <option value="all">全部品种</option>
          <option value="backwardation">🟢 仅贴水品种</option>
          <option value="contango">🔴 仅升水品种</option>
          <option value="cffex">📊 股指期货</option>
          <option value="commodity">📦 商品期货</option>
        </select>
        <select v-model="fexch" @change="applyFilter">
          <option value="all">全部交易所</option>
          <option value="cffex">中金所</option>
          <option value="shfe">上期所</option>
          <option value="dce">大商所</option>
          <option value="zce">郑商所</option>
          <option value="ine">能源中心</option>
        </select>
        <button class="btn btn-secondary" @click="onReset">重置</button>
      </div>

      <div class="stats-bar" v-html="statsHtml"></div>

      <div class="table-wrap">
        <div v-if="loading" class="loading-state">
          <div class="sp"></div>
          <p>正在拉取期货行情数据</p>
          <p style="font-size:11px;color:var(--text-muted);margin-top:4px;">首次查询约需5-15秒 · 来源：新浪财经</p>
        </div>
        <div v-else-if="loadError" class="error-state" style="text-align:center;padding:40px;">
          <p style="font-size:16px;color:var(--red);margin-bottom:6px;">⚠️ 数据获取失败</p>
          <p style="font-size:12px;color:var(--text-dim);">{{ loadError }}</p>
          <button class="btn" style="margin-top:12px;" @click="loadData">重试</button>
        </div>
        <div v-else class="table-scroll">
          <table>
            <thead>
              <tr>
                <th @click="onSort('name')">品种<span class="sa">{{ sortArrow('name') }}</span></th>
                <th>代码</th>
                <th>交易所</th>
                <th @click="onSort('price')">最新价<span class="sa">{{ sortArrow('price') }}</span></th>
                <th @click="onSort('changePct')">涨跌幅<span class="sa">{{ sortArrow('changePct') }}</span></th>
                <th @click="onSort('spreadPct')">跨期价差<span class="sa">{{ sortArrow('spreadPct') }}</span></th>
                <th>升贴水</th>
                <th>主力合约</th>
                <th>次主力</th>
                <th @click="onSort('volume')">成交量<span class="sa">{{ sortArrow('volume') }}</span></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!filteredData.length">
                <td colspan="10" style="text-align:center;padding:40px;color:var(--text-dim);">没有匹配的品种</td>
              </tr>
              <tr
                v-for="e in filteredData"
                :key="e.code"
                :class="{ 'backwardation-row': e.isBackwardation }"
                style="cursor:pointer;"
                :title="'点击查看合约链详情'"
                @click="showDetail(e.code)"
              >
                <td style="max-width:130px;position:relative;">
                  <span style="font-weight:500;">{{ e.name }}</span>
                </td>
                <td class="cc nm"><b>{{ e.code }}</b></td>
                <td><span class="cc">{{ exchangeNames[e.exchange] || e.exchange }}</span></td>
                <td class="nm" style="font-weight:600;" v-html="fmtPrice(e.price)"></td>
                <td class="nm" :class="e.changePct >= 0 ? 'pr' : 'pg'">{{ e.changePct >= 0 ? '+' : '' }}{{ (e.changePct || 0).toFixed(2) }}%</td>
                <td class="nm" :class="e.spreadPct != null ? (e.spreadPct > 0 ? 'pr' : 'pg') : ''">{{ spreadLabel(e) }}</td>
                <td>
                  <span v-if="e.isBackwardation" class="tag tag-bw">📉 贴水</span>
                  <span v-else-if="e.spreadPct != null" class="tag tag-ct">📈 升水</span>
                  <span v-else class="cc" style="font-size:10px;">-</span>
                </td>
                <td style="font-size:11px;color:var(--text-dim);">{{ e.mainContract || '-' }}</td>
                <td style="font-size:11px;color:var(--text-dim);">{{ e.contract2Name || '-' }}</td>
                <td class="nm cc" v-html="fmtNum(e.volume)"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="legend">
        <p>📌 <strong style="color:var(--green);">贴水 (Backwardation)</strong> = 远月合约价格 <strong>低于</strong> 近月合约 · 远月折价</p>
        <p>📌 <strong style="color:var(--red);">升水 (Contango)</strong> = 远月合约价格 <strong>高于</strong> 近月合约 · 远月溢价</p>
        <p>📌 <strong>跨期价差</strong> = (主力价格 - 次主力价格) / 次主力价格 × 100% · 正值 = 贴水(近月高)，负值 = 升水(远月高)</p>
        <p>💡 点击品种行可查看完整合约链详情</p>
        <p class="data-source">{{ srcInfo }}</p>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="detailOpen" class="detail-overlay" @click="onOverlayClick">
      <div class="detail-modal" @click.stop>
        <div class="dt-header">
          <div>
            <h2>{{ detailTitle }}</h2>
            <span v-if="detailMeta" class="cc" style="font-size:11px;">{{ detailMeta }}</span>
          </div>
          <button class="dt-close" @click="closeDetail">✕</button>
        </div>
        <div v-if="detailLoading" class="dt-loading">
          <div class="sp"></div>
          <p>加载合约链数据...</p>
        </div>
        <div v-else-if="detailError" class="dt-content">
          <p style="text-align:center;padding:30px;color:var(--red);">查询失败: {{ detailError }}</p>
        </div>
        <div v-else-if="detailEmpty" class="dt-content">
          <p style="text-align:center;padding:30px;color:var(--text-dim);">暂无此品种的合约数据</p>
        </div>
        <div v-else-if="detailData" class="dt-content">
          <div class="table-wrap" style="margin-top:12px;">
            <table class="dt-table">
              <thead>
                <tr>
                  <th>合约</th><th>最新价</th><th>涨跌幅</th><th>基差</th><th>基差率</th>
                  <th>成交量</th><th>持仓量</th><th>日期</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in detailData.contracts" :key="c.month">
                  <td style="font-weight:500;">{{ c.month }}</td>
                  <td class="nm" style="font-weight:600;">{{ fmtPricePlain(c.price) }}</td>
                  <td class="nm" :class="c.change >= 0 ? 'pr' : 'pg'">{{ c.change >= 0 ? '+' : '' }}{{ c.change.toFixed(2) }}%</td>
                  <td class="nm" :class="c.basis != null ? (c.basis >= 0 ? 'pr' : 'pg') : 'cc'">
                    {{ c.basis != null ? (c.basis >= 0 ? '+' : '') + fmtPricePlain(c.basis) : '-' }}
                  </td>
                  <td class="nm" :class="c.basisPct != null ? (c.basisPct >= 0 ? 'pr' : 'pg') : 'cc'">
                    {{ c.basisPct != null ? (c.basisPct >= 0 ? '+' : '') + c.basisPct.toFixed(2) + '%' : '-' }}
                  </td>
                  <td class="nm cc">{{ fmtVol(c.volume) }}</td>
                  <td class="nm cc">{{ fmtVol(c.openInterest || 0) }}</td>
                  <td class="cc" style="font-size:11px;">{{ c.date || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="dt-basis" style="margin-top:12px;padding:10px 14px;background:var(--card);border:1px solid var(--border);border-radius:8px;" v-html="basisHtml"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { getFuturesBasis, getFuturesDetail } from '@/services/etfApi';
import '@/styles/futures.css';

interface FuturesRow {
  code: string;
  name: string;
  exchange: string;
  price: number | null;
  changePct: number;
  spreadPct: number | null;
  isBackwardation: boolean;
  mainContract?: string;
  contract2Name?: string;
  volume: number;
}

interface ContractDetail {
  month: string;
  price: number | null;
  change: number;
  basis: number | null;
  basisPct: number | null;
  volume: number;
  openInterest?: number;
  date?: string;
}

interface DetailData {
  ok?: boolean;
  name: string;
  code: string;
  exchange: string;
  unit: string;
  contracts: ContractDetail[];
  isContango?: boolean;
  basis?: number;
  basisPct?: number;
}

const exchangeNames: Record<string, string> = {
  cffex: '中金所', shfe: '上期所', dce: '大商所', zce: '郑商所', ine: '能源中心',
};

const rawData = ref<FuturesRow[]>([]);
const filteredData = ref<FuturesRow[]>([]);
const searchInput = ref('');
const ftype = ref('all');
const fexch = ref('all');
const sortKey = ref('spreadPct');
const sortDir = ref<'asc' | 'desc'>('desc');
const loading = ref(true);
const loadError = ref('');
const dotClass = ref('loading');
const utext = ref('加载中...');
const srcInfo = ref('');
const statsHtml = ref('<span style="color:var(--text-dim);font-size:11px;">加载中...</span>');

const detailOpen = ref(false);
const detailLoading = ref(false);
const detailError = ref('');
const detailEmpty = ref(false);
const detailData = ref<DetailData | null>(null);
const detailTitle = ref('');
const detailMeta = ref('');

let refreshTimer: ReturnType<typeof setInterval> | null = null;

function fmtNum(v: number | null | undefined) {
  if (v == null || v === 0) return '<span style="color:var(--text-muted)">-</span>';
  if (v >= 100000) return (v / 10000).toFixed(0) + '万';
  if (v >= 10000) return (v / 10000).toFixed(1) + '万';
  if (v >= 1000) return (v / 1000).toFixed(1) + '千';
  return v.toLocaleString();
}

function fmtPrice(v: number | null | undefined) {
  if (v == null) return '<span style="color:var(--text-muted)">-</span>';
  if (v >= 1000) return String(v.toFixed(v >= 10000 ? 0 : 2));
  if (v >= 10) return v.toFixed(1);
  return v.toFixed(2);
}

function fmtPricePlain(v: number | null | undefined) {
  if (v == null) return '-';
  if (v >= 1000) return v.toFixed(v >= 10000 ? 0 : 2);
  if (v >= 10) return v.toFixed(1);
  return v.toFixed(2);
}

function fmtVol(v: number) {
  return v >= 10000 ? (v / 10000).toFixed(1) + '万' : v.toLocaleString();
}

function spreadLabel(e: FuturesRow) {
  if (e.spreadPct == null) return '-';
  return `${e.spreadPct > 0 ? '+' : ''}${e.spreadPct.toFixed(2)}%`;
}

function sortArrow(key: string) {
  if (sortKey.value !== key) return '';
  return sortDir.value === 'asc' ? '▲' : '▼';
}

function renderStats() {
  if (!rawData.value.length) {
    statsHtml.value = '<span style="color:var(--text-dim);font-size:11px;">暂无数据</span>';
    return;
  }
  const t = rawData.value.length;
  const bw = rawData.value.filter(r => r.isBackwardation).length;
  const ct = rawData.value.filter(r => r.spreadPct != null && !r.isBackwardation).length;
  const na = rawData.value.filter(r => r.spreadPct == null).length;
  statsHtml.value = `
    <span>总数 <b>${t}</b></span>
    <span class="pill backwardation">🟢 贴水 ${bw}</span>
    <span class="pill contango">🔴 升水 ${ct}</span>
    ${na > 0 ? `<span class="cc" style="font-size:10px;">${na} 个无跨期数据</span>` : ''}
    <span style="color:var(--text-dim);font-size:11px;margin-left:auto;">${new Date().toLocaleTimeString()}</span>
  `;
}

function applyFilter() {
  const search = searchInput.value.trim().toLowerCase();
  let result = rawData.value.filter(e => {
    if (search && !e.code.toLowerCase().includes(search) && !e.name.toLowerCase().includes(search)) return false;
    if (ftype.value === 'backwardation' && !e.isBackwardation) return false;
    if (ftype.value === 'contango' && e.isBackwardation) return false;
    if (ftype.value === 'cffex' && e.exchange !== 'cffex') return false;
    if (ftype.value === 'commodity' && e.exchange === 'cffex') return false;
    if (fexch.value !== 'all' && e.exchange !== fexch.value) return false;
    return true;
  });

  const key = sortKey.value;
  const dir = sortDir.value;
  result = result.slice().sort((a, b) => {
    let va: unknown = a[key as keyof FuturesRow];
    let vb: unknown = b[key as keyof FuturesRow];
    if (typeof va === 'string') va = va.toLowerCase();
    if (typeof vb === 'string') vb = vb.toLowerCase();
    if (va == null) return 1;
    if (vb == null) return -1;
    if (va < vb) return dir === 'asc' ? -1 : 1;
    if (va > vb) return dir === 'asc' ? 1 : -1;
    return 0;
  });

  filteredData.value = result;
}

function onSort(key: string) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDir.value = 'desc';
  }
  applyFilter();
}

function onReset() {
  searchInput.value = '';
  ftype.value = 'all';
  fexch.value = 'all';
  sortKey.value = 'spreadPct';
  sortDir.value = 'desc';
  applyFilter();
}

async function loadData() {
  loading.value = true;
  loadError.value = '';
  dotClass.value = 'loading';
  utext.value = '获取中...';
  srcInfo.value = '';

  try {
    const json = await getFuturesBasis();
    rawData.value = (json.data || []).slice();
    renderStats();
    applyFilter();
    dotClass.value = '';
    utext.value = new Date().toLocaleString('zh-CN');
    const bwCount = rawData.value.filter(r => r.isBackwardation).length;
    srcInfo.value = `数据来源：新浪财经K线 · 共 ${json.total} 个品种 · 贴水 ${bwCount} 个 · ${json.updated}`;
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : '连接失败';
    dotClass.value = 'fail';
    utext.value = '失败';
  } finally {
    loading.value = false;
  }
}

const basisHtml = computed(() => {
  const data = detailData.value;
  if (!data || !data.contracts || data.contracts.length < 2) {
    return '<p style="color:var(--text-dim);">仅获取到一个合约数据，无法计算跨期基差</p>';
  }
  const near = data.contracts[0];
  const far = data.contracts[1];
  const isCt = data.isContango;
  const basisCls = isCt ? 'pr' : 'pg';
  const label = isCt ? '升水 (Contango)' : '贴水 (Backwardation)';
  const labelCls = isCt ? 'tag-ct' : 'tag-bw';
  return `
    <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap;">
      <span><span class="tag ${labelCls}" style="font-size:11px;">${label}</span></span>
      <span>近月 <b>${near.month}</b> = <span class="nm">${fmtPricePlain(near.price)}</span></span>
      <span>远月 <b>${far.month}</b> = <span class="nm">${fmtPricePlain(far.price)}</span></span>
      <span>基差 = <span class="nm ${basisCls}">${(data.basis ?? 0) >= 0 ? '+' : ''}${fmtPricePlain(data.basis)}</span></span>
      <span>基差率 = <span class="nm ${basisCls}">${(data.basisPct ?? 0) >= 0 ? '+' : ''}${(data.basisPct ?? 0).toFixed(2)}%</span></span>
    </div>
    <div style="margin-top:6px;font-size:11px;color:var(--text-dim);">
      ${isCt ? '远月合约价格高于近月，呈升水结构（Contango），远期看多' : '远月合约价格低于近月，呈贴水结构（Backwardation），远期看空'}
    </div>
  `;
});

async function showDetail(code: string) {
  if (detailOpen.value) return;
  detailOpen.value = true;
  detailLoading.value = true;
  detailError.value = '';
  detailEmpty.value = false;
  detailData.value = null;
  detailTitle.value = `${code} · 加载中...`;
  detailMeta.value = '';

  try {
    const data = await getFuturesDetail(code);
    if (!data.ok || !data.contracts || !data.contracts.length) {
      detailTitle.value = `${code} · 无数据`;
      detailEmpty.value = true;
      return;
    }
    detailData.value = data;
    detailTitle.value = `${data.name} (${data.code})`;
    detailMeta.value = `${data.exchange} · ${data.unit}`;
  } catch (e) {
    detailTitle.value = `${code} · 查询失败`;
    detailError.value = e instanceof Error ? e.message : '未知错误';
  } finally {
    detailLoading.value = false;
  }
}

function closeDetail() {
  detailOpen.value = false;
  detailData.value = null;
}

function onOverlayClick(e: MouseEvent) {
  if (e.target === e.currentTarget) closeDetail();
}

onMounted(() => {
  loadData();
  refreshTimer = setInterval(loadData, 120000);
});

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer);
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}
</style>
