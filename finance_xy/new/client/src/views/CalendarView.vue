<template>
  <div class="page">
    <div class="header">
      <div class="header-inner">
        <div class="header-left">
          <router-link to="/" class="back-btn">‹</router-link>
          <div class="header-title">
            <h1><span class="accent">📅</span> 投资日历</h1>
          </div>
        </div>
        <div class="header-right">{{ updateTime }}</div>
      </div>
    </div>

    <div class="main">
      <div class="summary-bar">
        <div class="summary-item">
          <div class="num">{{ ipo.length }}</div>
          <div class="label">待申购</div>
        </div>
        <div class="summary-item">
          <div class="num">{{ cb.length }}</div>
          <div class="label">转债事件</div>
        </div>
        <div class="summary-item">
          <div class="num">{{ listed.length }}</div>
          <div class="label">即将上市</div>
        </div>
      </div>

      <div class="section-tabs">
        <div
          v-for="tab in tabs"
          :key="tab.key"
          class="section-tab"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >{{ tab.label }}</div>
      </div>

      <div class="refresh-bar">
        <button class="refresh-btn" @click="loadData">⟳ 刷新</button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <div>加载中...</div>
      </div>

      <div v-else-if="error" class="error-state">❌ {{ error }}</div>

      <div v-else>
        <div v-show="showSection('ipo')" class="section" id="section-ipo">
          <div class="section-title">
            <span class="icon ipo">📄</span> 新股申购
          </div>
          <div class="card">
            <div class="card-body">
              <table v-if="ipo.length">
                <thead>
                  <tr>
                    <th>代码</th><th>名称</th><th>发行价(元)</th><th>市盈率</th>
                    <th>申购日期</th><th>顶格申购</th><th>市场</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="i in ipo" :key="i.code + i.apply_date">
                    <td>{{ i.code }}</td>
                    <td>{{ i.name }}</td>
                    <td>{{ i.price || '-' }}</td>
                    <td>{{ i.pe || '-' }}</td>
                    <td><span v-html="dateBadge(i.apply_date)"></span></td>
                    <td>{{ i.apply_upper ? (i.apply_upper / 10000).toFixed(2) + '万元' : '-' }}</td>
                    <td><span v-html="marketTag(i.trade_market)"></span></td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="empty-state">
                <div class="big-icon">📭</div>
                <div>暂无新股申购</div>
              </div>
            </div>
          </div>
        </div>

        <div v-show="showSection('cb')" class="section" id="section-cb">
          <div class="section-title">
            <span class="icon cb">🔖</span> 可转债事件
          </div>
          <div class="card">
            <div class="card-body">
              <table v-if="cb.length">
                <thead>
                  <tr>
                    <th>代码</th><th>名称</th><th>事件类型</th><th>日期</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="c in cb" :key="c.code + c.date">
                    <td>{{ c.code }}</td>
                    <td>{{ c.name }}</td>
                    <td>
                      <span class="tag" :class="c.event_type === '到期' ? 'tag-expire' : 'tag-lastday'">{{ c.event_type }}</span>
                    </td>
                    <td><span v-html="dateBadge(c.date)"></span></td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="empty-state">
                <div class="big-icon">📭</div>
                <div>暂无可转债事件</div>
              </div>
            </div>
          </div>
        </div>

        <div v-show="showSection('listed')" class="section" id="section-listed">
          <div class="section-title">
            <span class="icon ipo">🚀</span> 上市提醒
          </div>
          <div class="card">
            <div class="card-body">
              <table v-if="listed.length">
                <thead>
                  <tr>
                    <th>代码</th><th>名称</th><th>上市日期</th><th>发行价(元)</th><th>市场</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="l in listed" :key="l.code + l.date">
                    <td>{{ l.code }}</td>
                    <td>{{ l.name }}</td>
                    <td><span v-html="dateBadge(l.date)"></span></td>
                    <td>{{ l.price || '-' }}</td>
                    <td><span v-html="marketTag(l.trade_market)"></span></td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="empty-state">
                <div class="big-icon">📭</div>
                <div>暂无上市提醒</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { getCalendar } from '@/services/etfApi';
import '@/styles/calendar.css';

interface IpoItem {
  code: string;
  name: string;
  price?: number | string;
  pe?: number | string;
  apply_date: string;
  apply_upper?: number;
  trade_market?: string;
}

interface CbItem {
  code: string;
  name: string;
  event_type: string;
  date: string;
}

interface ListedItem {
  code: string;
  name: string;
  date: string;
  price?: number | string;
  trade_market?: string;
}

const today = new Date();
const todayStr = today.toISOString().slice(0, 10);

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'ipo', label: '新股申购' },
  { key: 'cb', label: '可转债到期' },
  { key: 'lastday', label: '最后交易日' },
  { key: 'listed', label: '上市提醒' },
];

const activeTab = ref('all');
const loading = ref(true);
const error = ref('');
const updateTime = ref('');
const ipo = ref<IpoItem[]>([]);
const cb = ref<CbItem[]>([]);
const listed = ref<ListedItem[]>([]);

function daysUntil(dateStr: string | undefined) {
  if (!dateStr) return null;
  const d1 = new Date(dateStr);
  return Math.floor((d1.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

function dateBadge(dateStr: string | undefined) {
  if (!dateStr) return '';
  const d = daysUntil(dateStr);
  let cls = 'normal';
  let text = dateStr.slice(5);
  if (dateStr === todayStr) { cls = 'today'; text = '今天'; }
  else if (d === 1) { cls = 'tomorrow'; text = '明天'; }
  else if (d !== null && d >= 0 && d <= 3) { cls = 'soon'; text = d + '天后'; }
  else if (d !== null && d > 3 && d <= 14) { text = d + '天后'; }
  else if (d !== null && d > 14) { text = dateStr.slice(5); }
  return `<span class="date-badge ${cls}">${text}</span>`;
}

function marketTag(market: string | undefined) {
  if (!market) return '<span class="tag tag-none">未知</span>';
  if (market.includes('北京')) return '<span class="tag tag-ipo">北交所</span>';
  if (market.includes('深圳')) return '<span class="tag tag-lastday">深交所</span>';
  if (market.includes('上海')) return '<span class="tag tag-listed">上交所</span>';
  if (market.includes('科创')) return '<span class="tag tag-redemption">科创板</span>';
  if (market.includes('创业')) return '<span class="tag tag-cb">创业板</span>';
  return `<span class="tag tag-none">${market}</span>`;
}

function showSection(section: 'ipo' | 'cb' | 'listed') {
  if (activeTab.value === 'all') return true;
  if (activeTab.value === 'ipo') return section === 'ipo';
  if (activeTab.value === 'listed') return section === 'listed';
  if (activeTab.value === 'cb' || activeTab.value === 'lastday') return section === 'cb';
  return false;
}

async function loadData() {
  loading.value = true;
  error.value = '';
  try {
    const json = await getCalendar();
    if (json.error) throw new Error(json.error);
    ipo.value = json.ipo || [];
    cb.value = json.cb || [];
    listed.value = json.listed || [];
    updateTime.value = '更新于 ' + new Date().toLocaleString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    error.value = e instanceof Error ? e.message : '请求失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}
</style>
