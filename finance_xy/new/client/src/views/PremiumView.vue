<template>
  <div>
    <div class="header">
      <div class="header-inner">
        <div class="header-left">
          <img src="/logo.jpg" class="logo-avatar" alt="猪猪">
          <div class="header-title">
            <h1><span class="accent">猪猪基金</span><span class="light"> 折溢价查询</span></h1>
            <div style="font-size:11px;color:var(--text-dim);">实时估算 · 仅供参考</div>
          </div>
        </div>
        <div class="header-right" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
          <span class="update-time" style="font-size:11px;">
            <span class="update-dot" :class="updateDotClass"></span>
            <span>{{ updateText }}</span>
          </span>
          <router-link to="/" class="btn" style="font-size:11px;padding:6px 10px;text-decoration:none;">📊 基金折溢价</router-link>
          <router-link to="/calendar" class="btn" style="font-size:11px;padding:6px 10px;background:linear-gradient(135deg,#22c55e,#16a34a);text-decoration:none;">📅 投资日历</router-link>
          <router-link to="/futures" class="btn" style="font-size:11px;padding:6px 10px;background:linear-gradient(135deg,#6366f1,#8b5cf6);text-decoration:none;">📈 期货基差</router-link>
          <router-link to="/perks" class="btn" style="text-decoration:none;font-size:11px;padding:6px 10px;background:linear-gradient(135deg,#f59e0b,#ef4444);">🎁 股东薅羊毛</router-link>
          <router-link to="/blacklist" class="btn" style="text-decoration:none;font-size:11px;padding:6px 10px;background:linear-gradient(135deg,#dc2626,#ef4444);">🚫 黑名单股票池</router-link>
          <router-link to="/house" class="btn" style="font-size:11px;padding:6px 10px;background:linear-gradient(135deg,#06b6d4,#0891b2);text-decoration:none;">🏠 房地产走势</router-link>
          <button class="btn" style="font-size:11px;padding:6px 10px;" @click="loadData">🔄 刷新</button>
        </div>
      </div>
    </div>

    <div class="index-bar-wrap">
      <div class="index-bar">
        <span v-if="!indexes.length" style="color:var(--text-dim);font-size:12px;padding:4px 0;">{{ indexBarText }}</span>
        <div v-for="idx in indexes" :key="idx.code" class="index-item">
          <div class="i-name">{{ idx.name || '' }}</div>
          <div class="i-row">
            <span class="i-price">{{ (idx.price || 0).toFixed(2) }}</span>
            <span class="i-change" :class="idx.change >= 0 ? 'up' : 'down'">{{ idx.change >= 0 ? '+' : '' }}{{ (idx.change || 0).toFixed(2) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="main">
      <div class="toolbar">
        <div class="search-wrap">
          <span class="icon">🔍</span>
          <input v-model="search" type="text" placeholder="搜代码或名称..." autocomplete="off" @input="onFilter">
        </div>
        <select v-model="typeFilter" @change="onFilter">
          <option value="all">全部类型</option>
          <option value="ETF">仅ETF</option>
          <option value="LOF">仅LOF</option>
        </select>
        <select v-model="premFilter" @change="onFilter">
          <option value="all">全部溢价</option>
          <option value="hp">溢价 &gt; 3%</option>
          <option value="po">溢价 &gt; 0</option>
          <option value="do">折价 &lt; 0</option>
          <option value="dd">折价 &lt; -3%</option>
        </select>
        <button class="btn btn-secondary" @click="onReset">重置</button>
        <button class="btn btn-secondary" style="position:relative;" @click="showAddDialog">➕ 添加</button>
      </div>

      <div class="stats-bar">
        <template v-if="rawData.length">
          <span>总数 <b>{{ stats.total }}</b></span><span class="divider"></span>
          <span style="color:var(--red)">溢价 <b>{{ stats.premiumCount }}</b></span>
          <span style="color:var(--green)">折价 <b>{{ stats.discountCount }}</b></span>
          <span style="color:var(--orange)">&gt;3% <b>{{ stats.highPremium }}</b></span>
          <span style="color:var(--warning)">&lt;-3% <b>{{ stats.highDiscount }}</b></span>
          <span class="divider"></span>
          <span>均值 <b>{{ stats.avgText }}</b></span>
          <span class="count-info">{{ countInfo }}</span>
        </template>
        <span v-else style="color:var(--text-dim);font-size:11px;">等待数据...</span>
      </div>

      <div class="table-wrap">
        <div v-if="showLoading" class="loading-state">
          <div class="sp"></div>
          <p>正在拉取 ETF 数据</p>
          <p style="font-size:11px;color:var(--text-muted);margin-top:4px;">首次查询大约需要 5-10 秒</p>
        </div>
        <div v-else-if="showError" class="error-state">
          <p style="font-size:16px;color:var(--red);margin-bottom:6px;">⚠️ 数据获取失败</p>
          <p style="font-size:12px;color:var(--text-dim);">{{ errorMsg }}</p>
          <button class="btn" style="margin-top:12px;" @click="loadData">重试</button>
        </div>
        <div v-else class="table-scroll">
          <table>
            <thead>
              <tr>
                <th @click="onSort('name')">名称<span class="sa">{{ sortArrow('name') }}</span></th>
                <th>代码</th>
                <th @click="onSort('type')">类型<span class="sa">{{ sortArrow('type') }}</span></th>
                <th @click="onSort('price')">现价<span class="sa">{{ sortArrow('price') }}</span></th>
                <th @click="onSort('nav')">净值<span class="sa">{{ sortArrow('nav') }}</span></th>
                <th @click="onSort('estNav')">估净<span class="sa">{{ sortArrow('estNav') }}</span></th>
                <th @click="onSort('premium')" style="min-width:44px">溢价率<span class="sa">{{ sortArrow('premium') }}</span></th>
                <th @click="onSort('realPremium')" style="min-width:44px">实时<span class="sa">{{ sortArrow('realPremium') }}</span></th>
                <th>申购</th>
                <th>限额</th>
                <th @click="onSort('amount')">成交<span class="sa">{{ sortArrow('amount') }}</span></th>
                <th @click="onSort('changePct')">涨跌<span class="sa">{{ sortArrow('changePct') }}</span></th>
                <th style="width:50px;text-align:center;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!filteredData.length">
                <td colspan="12" style="text-align:center;padding:40px;color:var(--text-dim);">没有匹配的数据</td>
              </tr>
              <tr v-for="e in filteredData" :key="e.code">
                <td class="nc">
                  <span class="nt" :title="e.name" style="cursor:pointer;color:var(--accent);" @click="showFundHistory(e.code)">{{ e.name || '-' }}</span>
                </td>
                <td class="cc" style="cursor:pointer;color:var(--accent);" @click="showFundHistory(e.code)">{{ e.code }}</td>
                <td>
                  <span v-if="e.type === 'LOF'" class="tag tag-lof">LOF</span>
                  <span v-else class="tag tag-etf">ETF</span>
                </td>
                <td class="nm"><span v-if="fmt(e.price, 3)">{{ fmt(e.price, 3) }}</span><span v-else style="color:var(--text-muted)">-</span></td>
                <td class="nm"><span v-if="e.nav && e.nav > 0">{{ fmt(e.nav, 4) }}</span><span v-else style="color:var(--text-muted)">-</span></td>
                <td class="nm"><span v-if="e.estNav && e.estNav > 0">{{ fmt(e.estNav, 4) }}</span><span v-else style="color:var(--text-muted)">-</span></td>
                <td>
                  <div class="pbw">
                    <span class="pm" :class="premiumCls(e.premium)">
                      <template v-if="e.premium != null && isFinite(e.premium)">{{ e.premium > 0 ? '+' : '' }}{{ fmt(e.premium, 2) }}%</template>
                      <span v-else style="color:var(--text-muted)">-</span>
                    </span>
                    <div class="pb"><div class="fl" :class="barCls(e.premium)" :style="{ width: barWidth(e.premium) + '%' }"></div></div>
                  </div>
                </td>
                <td class="pm" :class="premiumCls(e.realPremium)">
                  <template v-if="e.realPremium != null && isFinite(e.realPremium)">{{ e.realPremium > 0 ? '+' : '' }}{{ fmt(e.realPremium, 2) }}%</template>
                  <span v-else style="color:var(--text-muted)">-</span>
                </td>
                <td style="font-size:11px;" :style="{ color: sgztColor(e.sgzt) }">{{ e.sgzt || '-' }}</td>
                <td style="font-size:11px;">
                  <span
                    v-if="isSgLimitClickable(e.sgLimit)"
                    class="sg-limit-click"
                    :style="{ color: sgLimitColor(e.sgLimit) }"
                    @click="showFundLimit(e.code)"
                  >{{ e.sgLimit }}</span>
                  <span v-else-if="e.sgLimit && e.sgLimit !== '-' && e.sgLimit !== dashSpan" :style="{ color: sgLimitColor(e.sgLimit), fontSize: '11px' }">{{ e.sgLimit }}</span>
                  <span v-else style="color:var(--text-muted)">-</span>
                </td>
                <td class="nm"><span v-if="fmt(e.amount, 2)">{{ fmt(e.amount, 2) }}</span><span v-else style="color:var(--text-muted)">-</span></td>
                <td class="nm" :class="e.changePct >= 0 ? 'up' : 'down'">{{ e.changePct >= 0 ? '+' : '' }}{{ fmt(e.changePct, 2) || '0.00' }}%</td>
                <td style="text-align:center;font-size:10px;">
                  <button class="btn-del" @click="removeFundHandler(e.code)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="legend">
        <p>📌 <strong>净值</strong>=上交易日净值 · <strong>估净</strong>=净值×(1+涨跌幅×0.9) 实时估算</p>
        <p>📌 溢价率=(现价−净值)÷净值 · 实时溢价=(现价−估净)÷估净</p>
        <p>⚠️ 溢价&gt;0表示现价高于净值（买贵了），折价&lt;0可能有捡便宜机会</p>
      </div>
    </div>

    <!-- 限额弹窗 -->
    <div v-if="limitPopupVisible" class="limit-overlay" @click.self="closeLimitPopup">
      <div class="limit-popup">
        <template v-if="limitPopupLoading">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <h3 style="font-size:15px;">🔍 {{ limitPopupCode }} <span style="font-size:12px;color:var(--text-dim);font-weight:400;">申购限额查询</span></h3>
            <span style="cursor:pointer;color:var(--text-dim);font-size:18px;" @click="closeLimitPopup">&times;</span>
          </div>
          <div style="text-align:center;padding:16px 0;color:var(--text-dim);">
            <div class="limit-spin"></div>
            <span>正在查询...</span>
          </div>
        </template>
        <template v-else-if="limitPopupData?.ok && limitPopupData.limit !== undefined">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <h3 style="font-size:15px;">🔍 {{ limitPopupData.code }} 申购限额</h3>
            <span style="cursor:pointer;color:var(--text-dim);font-size:18px;" @click="closeLimitPopup">&times;</span>
          </div>
          <div style="background:var(--bg);border-radius:8px;padding:16px;">
            <div style="margin-bottom:10px;">
              <span style="color:var(--text-dim);font-size:12px;">交易状态</span>
              <div style="font-size:15px;font-weight:600;margin-top:3px;">{{ limitPopupData.status || '未知' }}</div>
            </div>
            <div style="margin-top:14px;padding-top:14px;border-top:1px solid var(--border);">
              <span style="color:var(--text-dim);font-size:12px;">📋 每日申购限额</span>
              <div
                style="font-size:24px;font-weight:700;margin-top:4px;"
                :style="{ color: limitPopupData.limitNum !== null && limitPopupData.limitNum !== undefined ? 'var(--orange)' : 'var(--text-dim)' }"
              >
                <template v-if="limitPopupData.limitNum !== null && limitPopupData.limitNum !== undefined">{{ limitPopupData.limitNum }}{{ limitPopupData.limitUnit }}</template>
                <template v-else>{{ limitPopupData.limit || '未获取到' }}</template>
              </div>
              <div v-if="limitPopupData.detailHtml" style="font-size:11px;color:var(--text-dim);margin-top:2px;">{{ stripHtml(limitPopupData.detailHtml) }}</div>
            </div>
          </div>
          <div style="margin-top:12px;display:flex;gap:8px;justify-content:space-between;align-items:center;">
            <span style="font-size:10px;color:var(--text-muted);">数据来源：天天基金</span>
            <button class="btn btn-secondary" style="font-size:12px;padding:6px 14px;" @click="closeLimitPopup">关闭</button>
          </div>
        </template>
        <template v-else-if="limitPopupData">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <h3 style="font-size:15px;">🔍 {{ limitPopupCode }} 申购限额</h3>
            <span style="cursor:pointer;color:var(--text-dim);font-size:18px;" @click="closeLimitPopup">&times;</span>
          </div>
          <div style="background:var(--bg);border-radius:8px;padding:16px;text-align:center;">
            <div style="font-size:16px;margin-bottom:6px;">{{ limitPopupData.status || '' }}</div>
            <span style="color:var(--text-dim);font-size:13px;">{{ limitPopupData.limit ? '限额：' + limitPopupData.limit : '未获取到具体限额信息' }}</span>
          </div>
          <div style="margin-top:12px;text-align:right;">
            <button class="btn btn-secondary" style="font-size:12px;padding:6px 14px;" @click="closeLimitPopup">关闭</button>
          </div>
        </template>
        <template v-else-if="limitPopupError">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <h3 style="font-size:15px;">🔍 {{ limitPopupCode }} 申购限额</h3>
            <span style="cursor:pointer;color:var(--text-dim);font-size:18px;" @click="closeLimitPopup">&times;</span>
          </div>
          <div style="background:var(--bg);border-radius:8px;padding:16px;text-align:center;">
            <span style="color:var(--red);font-size:13px;">查询失败: {{ limitPopupError }}</span>
          </div>
          <div style="margin-top:12px;text-align:right;">
            <button class="btn btn-secondary" style="font-size:12px;padding:6px 14px;" @click="closeLimitPopup">关闭</button>
          </div>
        </template>
      </div>
    </div>

    <!-- 添加基金对话框 -->
    <div v-if="addDialogVisible" class="add-overlay" @click.self="closeAddDialog">
      <div class="add-dialog">
        <h3 style="font-size:16px;margin-bottom:16px;">🔖 添加基金</h3>
        <div style="margin-bottom:12px;">
          <label style="font-size:12px;color:var(--text-dim);display:block;margin-bottom:4px;">基金代码 <span style="color:var(--red);">*</span></label>
          <input
            ref="addCodeInput"
            v-model="addCode"
            type="text"
            placeholder="如 159915"
            class="add-input"
            autocomplete="off"
            @keydown.enter="submitAddFund"
          >
        </div>
        <div style="margin-bottom:16px;">
          <label style="font-size:12px;color:var(--text-dim);display:block;margin-bottom:4px;">自定义名称（可选）</label>
          <input
            v-model="addName"
            type="text"
            placeholder="不填则自动识别"
            class="add-input-name"
            autocomplete="off"
            @keydown.enter="submitAddFund"
          >
        </div>
        <div style="display:flex;gap:8px;justify-content:flex-end;">
          <button class="btn btn-secondary" @click="closeAddDialog">取消</button>
          <button class="btn" :disabled="addBtnDisabled" @click="submitAddFund">{{ addBtnText }}</button>
        </div>
        <div style="margin-top:10px;font-size:12px;min-height:18px;" v-html="addMsg"></div>
      </div>
    </div>

    <!-- 基金历史详情弹窗 -->
    <div v-if="histVisible" class="hist-overlay" @click.self="closeHist">
      <div class="hist-popup">
        <div class="hist-header">
          <h2>📊 {{ histFundName }} <span class="sub">{{ histCode }} · 近20天溢价率 &amp; 场内份额</span></h2>
          <button class="hist-close" @click="closeHist">&times;</button>
        </div>
        <div class="hist-body">
          <div v-if="histLoading" class="hist-loading">
            <div class="sp"></div>
            <span>查询历史数据...</span>
          </div>
          <div v-else-if="histError" style="text-align:center;padding:40px 0;">
            <span style="color:var(--red);font-size:13px;">❌ {{ histError }}</span>
          </div>
          <div v-else-if="histContent">
            <div class="hist-stats">
              <div><div class="label">统计天数</div><div class="val">{{ histContent.history?.length ?? 0 }}天</div></div>
              <span class="divider"></span>
              <div><div class="label">平均溢价率</div><div class="val" :style="{ color: histStats.avgPremium > 0 ? 'var(--red)' : 'var(--green)' }">{{ histStats.avgPremium > 0 ? '+' : '' }}{{ histStats.avgPremium.toFixed(2) }}%</div></div>
              <span class="divider"></span>
              <div><div class="label">最高溢价</div><div class="val" style="color:var(--red)">+{{ histStats.maxPremium.toFixed(2) }}%</div></div>
              <span class="divider"></span>
              <div><div class="label">最低溢价</div><div class="val" style="color:var(--green)">{{ histStats.minPremium.toFixed(2) }}%</div></div>
              <span class="divider"></span>
              <div><div class="label">溢价≥0</div><div class="val" style="color:var(--red)">{{ histStats.posDays }}天</div></div>
              <span class="divider"></span>
              <div><div class="label">溢价&lt;0</div><div class="val" style="color:var(--green)">{{ histStats.negDays }}天</div></div>
              <template v-if="histShares.current">
                <span class="divider"></span>
                <div><div class="label">📊 当前实时总份额</div><div class="val" style="color:var(--accent);font-size:16px;">{{ fmtThousands((histShares.current / 10000).toFixed(2)) }}万份</div></div>
              </template>
              <template v-if="histLatestQuarter">
                <span class="divider"></span>
                <div><div class="label">最新季报份额</div><div class="val">{{ histLatestQuarter.totalShares }}亿份</div></div>
                <span class="divider"></span>
                <div><div class="label">报告期</div><div class="val" style="font-size:12px;color:var(--text-dim);">{{ histLatestQuarter.date }}</div></div>
                <template v-if="histShareDiff !== null">
                  <span class="divider"></span>
                  <div><div class="label">较季末变化</div><div class="val" :style="{ color: histShareDiffColor }">{{ histShareDiff > 0 ? '+' : '' }}{{ histShareDiff }}%</div></div>
                </template>
              </template>
            </div>
            <div v-if="histQuarterShares.length > 1" style="margin-bottom:8px;font-size:11px;color:var(--text-dim);display:flex;gap:8px;flex-wrap:wrap;">
              <span>📋 份额近期变化：</span>
              <span
                v-for="q in histQuarterShares.slice(0, 4)"
                :key="q.date"
                style="background:var(--bg);padding:2px 8px;border-radius:4px;border:1px solid var(--border);"
              >
                {{ q.date }} <b>{{ q.totalShares }}亿份</b>
              </span>
            </div>
            <div class="hist-legend">
              <span><span class="dot" style="background:var(--red)"></span>溢价率</span>
              <span><span class="dot" style="background:var(--accent)"></span>价格</span>
              <span><span class="dot" style="background:var(--orange)"></span>净值</span>
              <span style="margin-left:auto;font-size:10px;color:var(--text-dim);">📌 份额数据来源：基金季度报告+实时行情</span>
            </div>
            <div class="hist-chart-wrap">
              <canvas ref="histChartCanvas"></canvas>
            </div>
            <div class="hist-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>日期</th>
                    <th>现价</th>
                    <th>净值</th>
                    <th>溢价率</th>
                    <th>场内份额(万份)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in histContent.history" :key="row.date">
                    <td>{{ row.date }}</td>
                    <td class="nm">{{ row.price.toFixed(3) }}</td>
                    <td class="nm">{{ row.nav.toFixed(4) }}</td>
                    <td class="nm" :class="row.premium > 0 ? 'pr' : (row.premium < 0 ? 'pg' : '')">{{ row.premium > 0 ? '+' : '' }}{{ row.premium.toFixed(2) }}%</td>
                    <td class="nm">{{ row.shares ? fmtThousands((row.shares / 10000).toFixed(2)) : '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  computed, nextTick, onMounted, onUnmounted, ref, watch,
} from 'vue';
import {
  addFund, getFundHistory, getFundLimit, getPremium, removeFund,
  type FundLimitResponse, type FundRow,
} from '@/services/etfApi';
import { calcStats, drawHistoryChart, fmtThousands } from '@/utils/historyChart';

type SortKey = 'name' | 'type' | 'price' | 'nav' | 'estNav' | 'premium' | 'realPremium' | 'amount' | 'changePct';

const rawData = ref<FundRow[]>([]);
const filteredData = ref<FundRow[]>([]);
const indexes = ref<{ name: string; code: string; price: number; change: number }[]>([]);
const sortKey = ref<SortKey>('premium');
const sortDir = ref<'asc' | 'desc'>('desc');
const search = ref('');
const typeFilter = ref('all');
const premFilter = ref('all');
const showLoading = ref(true);
const showError = ref(false);
const errorMsg = ref('');
const updateDotClass = ref('');
const updateText = ref('加载中...');
const countInfo = ref('');
const indexBarText = ref('加载指数行情...');
const dashSpan = '<span style="color:var(--text-muted)">-</span>';

let refreshTimer: ReturnType<typeof setInterval> | null = null;

// 限额弹窗
const limitPopupVisible = ref(false);
const limitPopupLoading = ref(false);
const limitPopupCode = ref('');
const limitPopupData = ref<FundLimitResponse | null>(null);
const limitPopupError = ref('');

// 添加对话框
const addDialogVisible = ref(false);
const addCode = ref('');
const addName = ref('');
const addMsg = ref('');
const addBtnDisabled = ref(false);
const addBtnText = ref('确认添加');
const addCodeInput = ref<HTMLInputElement | null>(null);

// 历史弹窗
const histVisible = ref(false);
const histLoading = ref(false);
const histError = ref('');
const histFundName = ref('');
const histCode = ref('');
const histContent = ref<Awaited<ReturnType<typeof getFundHistory>> | null>(null);
const histChartCanvas = ref<HTMLCanvasElement | null>(null);

const stats = computed(() => {
  const t = rawData.value.length;
  if (!t) {
    return {
      total: 0, premiumCount: 0, discountCount: 0, highPremium: 0, highDiscount: 0, avgText: '-',
    };
  }
  const pCnt = rawData.value.filter((e) => e.premium != null && e.premium > 0).length;
  const dCnt = t - pCnt;
  const hp = rawData.value.filter((e) => e.premium != null && e.premium > 3).length;
  const hd = rawData.value.filter((e) => e.premium != null && e.premium < -3).length;
  const avg = rawData.value.reduce((s, e) => s + (e.premium ?? 0), 0) / t;
  const avgText = avg != null && isFinite(avg) ? `${avg > 0 ? '+' : ''}${avg.toFixed(2)}%` : '-';
  return {
    total: t, premiumCount: pCnt, discountCount: dCnt, highPremium: hp, highDiscount: hd, avgText,
  };
});

const histStats = computed(() => {
  if (!histContent.value?.history?.length) {
    return { avgPremium: 0, maxPremium: 0, minPremium: 0, posDays: 0, negDays: 0 };
  }
  return calcStats(histContent.value.history);
});

const histShares = computed(() => histContent.value?.shares || {});
const histQuarterShares = computed(() => histShares.value.quarterHistory || []);
const histLatestQuarter = computed(() => (histQuarterShares.value.length > 0 ? histQuarterShares.value[0] : null));

const histShareDiff = computed(() => {
  const current = histShares.value.current;
  const latest = histLatestQuarter.value;
  if (!current || !latest) return null;
  const latestQs = parseFloat(latest.totalShares.replace(/[^0-9.]/g, ''));
  if (isNaN(latestQs) || latestQs <= 0) return null;
  return Math.round(((current / 10000) - latestQs * 10000) / (latestQs * 10000) * 10000) / 100;
});

const histShareDiffColor = computed(() => {
  const diff = histShareDiff.value;
  if (diff == null) return 'var(--text-dim)';
  if (diff > 0) return 'var(--red)';
  if (diff < 0) return 'var(--green)';
  return 'var(--text-dim)';
});

function fmt(v: number | null | undefined, digits: number) {
  return v != null && isFinite(v) ? v.toFixed(digits) : null;
}

function premiumCls(v: number | null | undefined) {
  if (v == null || !isFinite(v)) return '';
  if (v > 0) return 'pr';
  if (v < 0) return 'pg';
  return '';
}

function barWidth(premium: number | null | undefined) {
  if (premium == null || !isFinite(premium)) return 0;
  return Math.min(Math.abs(premium) / 5 * 100, 100);
}

function barCls(premium: number | null | undefined) {
  if (premium == null || !isFinite(premium)) return '';
  if (premium > 3) return 'pr';
  if (premium > 0) return 'po';
  if (premium < 0) return 'pg';
  return '';
}

function sgztColor(v: string | undefined) {
  if (!v) return 'var(--text-muted)';
  if (v.includes('暂停') || v.includes('🛑')) return 'var(--red)';
  if (v.includes('✅')) return 'var(--green)';
  if (v.includes('限制')) return 'var(--orange)';
  if (v.includes('场内')) return 'var(--accent)';
  return 'var(--green)';
}

function sgLimitColor(v: string | undefined) {
  if (!v) return 'var(--text-muted)';
  if (v.includes('暂停') || v.includes('限大额')) return 'var(--orange)';
  if (v.includes('不限')) return 'var(--green)';
  if (v.includes('场内')) return 'var(--accent)';
  return 'var(--text-dim)';
}

function isSgLimitClickable(sgLimit: string | undefined) {
  if (!sgLimit || sgLimit === '-' || sgLimit === dashSpan) return false;
  return sgLimit === '⚠️限大额' || sgLimit === '🛑暂停';
}

function stripHtml(html: string) {
  return html.replace(/<[^>]+>/g, '');
}

function sortArrow(key: SortKey) {
  return sortKey.value === key ? (sortDir.value === 'asc' ? '▲' : '▼') : '';
}

function applyFilter() {
  const q = search.value.trim().toLowerCase();
  const tf = typeFilter.value;
  const pf = premFilter.value;

  let result = rawData.value.filter((e) => {
    if (q && !e.code.includes(q) && !(e.name || '').toLowerCase().includes(q)) return false;
    if (tf !== 'all' && e.type !== tf) return false;
    if (pf === 'hp' && (e.premium == null || e.premium <= 3)) return false;
    if (pf === 'po' && (e.premium == null || e.premium <= 0)) return false;
    if (pf === 'do' && (e.premium == null || e.premium >= 0)) return false;
    if (pf === 'dd' && (e.premium == null || e.premium >= -3)) return false;
    return true;
  });

  result = [...result].sort((a, b) => {
    let va: string | number | null = a[sortKey.value] as string | number | null;
    let vb: string | number | null = b[sortKey.value] as string | number | null;
    if (typeof va === 'string') va = va.toLowerCase();
    if (typeof vb === 'string') vb = vb.toLowerCase();
    if (va == null) return 1;
    if (vb == null) return -1;
    if (va < vb) return sortDir.value === 'asc' ? -1 : 1;
    if (va > vb) return sortDir.value === 'asc' ? 1 : -1;
    return 0;
  });

  filteredData.value = result;
  countInfo.value = result.length ? `显示 ${result.length}/${rawData.value.length}` : '0 条';
}

function onFilter() {
  applyFilter();
}

function onSort(key: SortKey) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDir.value = (key === 'name' || key === 'type') ? 'asc' : 'desc';
  }
  applyFilter();
}

function onReset() {
  search.value = '';
  typeFilter.value = 'all';
  premFilter.value = 'all';
  sortKey.value = 'premium';
  sortDir.value = 'desc';
  applyFilter();
}

async function loadData() {
  showError.value = false;
  showLoading.value = true;
  updateDotClass.value = 'loading';
  updateText.value = '获取中...';

  try {
    const json = await getPremium();
    rawData.value = (json.data || []).slice();
    indexes.value = json.indexes || [];
    indexBarText.value = indexes.value.length ? '' : '暂无指数数据';
    applyFilter();
    showLoading.value = false;
    updateDotClass.value = '';
    updateText.value = new Date().toLocaleString('zh-CN');
  } catch (e) {
    console.error('加载失败:', e);
    showLoading.value = false;
    showError.value = true;
    errorMsg.value = e instanceof Error ? e.message : '连接失败，请确认 node server.js 已启动';
    updateDotClass.value = 'fail';
    updateText.value = '失败';
  }
}

async function showFundLimit(code: string) {
  limitPopupVisible.value = true;
  limitPopupLoading.value = true;
  limitPopupCode.value = code;
  limitPopupData.value = null;
  limitPopupError.value = '';

  try {
    const json = await getFundLimit(code);
    limitPopupData.value = json;
  } catch (e) {
    limitPopupError.value = e instanceof Error ? e.message : '未知错误';
  } finally {
    limitPopupLoading.value = false;
  }
}

function closeLimitPopup() {
  limitPopupVisible.value = false;
}

function showAddDialog() {
  addDialogVisible.value = true;
  addCode.value = '';
  addName.value = '';
  addMsg.value = '';
  addBtnDisabled.value = false;
  addBtnText.value = '确认添加';
  nextTick(() => addCodeInput.value?.focus());
}

function closeAddDialog() {
  addDialogVisible.value = false;
}

async function submitAddFund() {
  const code = addCode.value.trim();
  const name = addName.value.trim();

  if (!code) {
    addMsg.value = '<span style="color:var(--red);">请输入基金代码</span>';
    return;
  }

  addBtnDisabled.value = true;
  addBtnText.value = '添加中...';
  addMsg.value = '<span style="color:var(--text-dim);">查询行情中...</span>';

  try {
    const json = await addFund(code, name || undefined);
    if (json.ok) {
      addMsg.value = `<span style="color:var(--green);">✅ 添加成功：${json.code}（${json.name}）</span>`;
      addBtnText.value = '✅ 已添加';
      setTimeout(() => {
        closeAddDialog();
        loadData();
      }, 2000);
    } else {
      addMsg.value = `<span style="color:var(--red);">❌ ${json.error || '添加失败'}</span>`;
      addBtnDisabled.value = false;
      addBtnText.value = '确认添加';
    }
  } catch (e) {
    addMsg.value = `<span style="color:var(--red);">❌ 请求失败: ${e instanceof Error ? e.message : '未知错误'}</span>`;
    addBtnDisabled.value = false;
    addBtnText.value = '确认添加';
  }
}

async function removeFundHandler(code: string) {
  if (!confirm(`确定删除 ${code} 吗？`)) return;
  try {
    const json = await removeFund(code);
    if (json.ok) {
      loadData();
    } else {
      alert(`删除失败: ${json.error || '未知错误'}`);
    }
  } catch (e) {
    alert(`删除失败: ${e instanceof Error ? e.message : '未知错误'}`);
  }
}

function closeHist() {
  histVisible.value = false;
  histContent.value = null;
}

async function showFundHistory(code: string) {
  const fund = rawData.value.find((e) => e.code === code);
  histFundName.value = fund ? fund.name : code;
  histCode.value = code;
  histVisible.value = true;
  histLoading.value = true;
  histError.value = '';
  histContent.value = null;

  try {
    const json = await getFundHistory(code);
    if (!json.ok) {
      histError.value = json.error || '暂无数据';
      return;
    }
    if (!json.history || !json.history.length) {
      histError.value = '近20天暂无溢价率数据（可能净值或价格缺失）';
      return;
    }
    histContent.value = json;
  } catch (e) {
    histError.value = `查询失败: ${e instanceof Error ? e.message : '未知错误'}`;
  } finally {
    histLoading.value = false;
  }
}

watch(histContent, async (val) => {
  if (val?.history?.length) {
    await nextTick();
    drawHistoryChart(val.history, histChartCanvas.value);
  }
});

onMounted(() => {
  loadData();
  refreshTimer = setInterval(loadData, 60000);
});

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer);
});
</script>

<style>
@import '@/styles/index.css';

.limit-overlay,
.add-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-overlay {
  background: rgba(0, 0, 0, 0.6);
}

.limit-popup,
.add-dialog {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  min-width: 320px;
  max-width: 380px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.add-dialog {
  padding: 24px;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.add-input,
.add-input-name {
  width: 100%;
  padding: 8px 10px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  outline: none;
}

.add-input {
  font-size: 14px;
  font-family: monospace;
}

.add-input-name {
  font-size: 13px;
}

.limit-spin {
  width: 24px;
  height: 24px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  margin: 0 auto 10px;
  animation: spin 0.8s linear infinite;
}

.error-state {
  text-align: center;
  padding: 60px 20px;
}
</style>
