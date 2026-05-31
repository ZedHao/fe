<template>
  <div class="page">
    <div class="header">
      <div class="header-inner">
        <div class="header-left">
          <img src="/logo.jpg" class="logo-avatar" alt="猪猪" />
          <div class="header-title">
            <h1><span class="accent">🎁 股东薅羊毛</span></h1>
            <div class="sub">上市公司股东回馈 · 持股就有福利</div>
          </div>
        </div>
        <div class="header-right" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
          <span class="update-time" style="font-size:11px;">
            <span class="update-dot" :class="dotClass"></span>
            <span>{{ utext }}</span>
          </span>
          <router-link to="/" class="btn" style="font-size:11px;padding:6px 10px;">📊 基金折溢价</router-link>
          <router-link to="/futures" class="btn" style="font-size:11px;padding:6px 10px;background:linear-gradient(135deg,#6366f1,#8b5cf6);">📈 期货基差</router-link>
          <router-link to="/perks" class="btn" style="font-size:11px;padding:6px 10px;background:linear-gradient(135deg,#f59e0b,#ef4444);">🎁 股东薅羊毛</router-link>
          <button class="btn" style="font-size:11px;padding:6px 10px;" @click="loadData">🔄 刷新</button>
        </div>
      </div>
    </div>

    <div class="main">
      <div class="toolbar">
        <div class="search-wrap">
          <span class="icon">🔍</span>
          <input v-model="searchInput" type="text" placeholder="搜股票代码/名称/福利..." autocomplete="off" @input="onFilter" />
        </div>
        <select v-model="statusFilter" @change="onFilter">
          <option value="all">全部状态</option>
          <option value="ongoing">🟢 进行中</option>
          <option value="upcoming">🟡 即将开始</option>
          <option value="ended">🔴 已结束</option>
        </select>
        <select v-model="shareFilter" @change="renderCards">
          <option value="all">最低持股：不限</option>
          <option value="100">≤ 100股</option>
          <option value="500">≤ 500股</option>
          <option value="1000">≤ 1000股</option>
        </select>
        <button class="btn btn-secondary" @click="onReset">重置</button>
        <a href="https://www.cninfo.com.cn/new/fulltextSearch?notautosubmit=&keyWord=股东回馈活动" target="_blank" class="btn btn-secondary" style="background:transparent;border:1px solid var(--accent);color:var(--accent);">🔍 巨潮公告</a>
        <select v-model="sourceFilter" @change="onFilter">
          <option value="all">全部来源</option>
          <option value="manual">手动录入</option>
          <option value="cninfo">巨潮公告</option>
        </select>
      </div>

      <div class="stats-bar" v-html="statsHtml"></div>

      <div v-if="loading" class="loading-state">
        <div class="sp"></div>
        <p>正在加载股东回馈数据...</p>
      </div>

      <div v-else-if="loadFailed" class="cards">
        <div class="empty-state">
          <div class="big">⚠️</div>
          <p>数据加载失败</p>
          <button class="btn" style="margin-top:12px;" @click="loadData">重试</button>
        </div>
      </div>

      <div v-else class="cards">
        <div v-if="!displayPerks.length" class="empty-state">
          <div class="big">🎁</div>
          <p>暂无匹配的股东回馈</p>
          <span style="font-size:12px;">试试调整筛选条件或搜索其他关键词</span>
        </div>
        <template v-else>
          <div v-for="(perk, idx) in displayPerks" :key="perkKey(perk, idx)" class="card" :style="perk._fromCninfo ? 'min-height:0;' : ''">
            <!-- 巨潮来源 -->
            <template v-if="perk._fromCninfo">
              <div class="card-header">
                <div>
                  <a :href="perk.sourceUrl" target="_blank" class="card-title" style="color:var(--accent);text-decoration:none;font-size:16px;">{{ perk.name }} ↗</a>
                  <div class="card-subtitle">{{ perk.code }}</div>
                </div>
                <span class="status-badge cninfo">📄 巨潮</span>
              </div>
              <div class="card-body">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                  <span style="color:var(--text-dim);font-size:11px;">📅 {{ perk.startDate }}</span>
                  <span style="font-size:10px;color:var(--accent);">查看PDF原文 →</span>
                </div>
                <div class="stock-info">
                  <span class="code-tag">{{ perk.code }}</span>
                  <template v-if="quoteFor(perk.code)">
                    <span class="price">{{ quoteFor(perk.code)!.price.toFixed(2) }}</span>
                    <span class="change" :class="quoteFor(perk.code)!.changePct >= 0 ? 'up' : 'down'">
                      {{ quoteFor(perk.code)!.changePct >= 0 ? '+' : '' }}{{ (quoteFor(perk.code)!.changePct || 0).toFixed(2) }}%
                    </span>
                  </template>
                </div>
              </div>
            </template>
            <!-- 手动来源 -->
            <template v-else>
              <div class="card-header">
                <div>
                  <div class="card-title" style="font-size:15px;">{{ perk.perkName }}</div>
                  <div class="card-subtitle">{{ perk.name }}（{{ perk.code }}） <span style="font-size:10px;color:var(--text-muted);">📝 人工整理</span></div>
                </div>
                <span class="status-badge" :class="perk.status">{{ statusText(perk) }}</span>
              </div>
              <div class="card-body">
                <div class="card-desc">{{ perk.description }}</div>
                <div class="card-meta">
                  <span class="card-meta-item">📅 {{ perk.startDate || '待定' }} {{ perk.endDate ? `~ ${perk.endDate}` : '' }}</span>
                  <span class="card-meta-item">⏳ <strong>{{ daysLeft(perk) }}</strong></span>
                  <span class="card-meta-item" :style="{ color: (perk.minShares ?? 0) <= 500 ? 'var(--green)' : 'var(--orange)' }">
                    📊 最低 <strong>{{ perk.minShares ?? 0 }}股</strong> {{ (perk.minShares ?? 0) <= 500 ? '✅友好' : '' }}
                  </span>
                  <span v-if="perk.benefit" class="card-meta-item">🎯 {{ perk.benefit }}</span>
                </div>
                <div class="progress-bar">
                  <div class="fill" :class="perk.status" :style="{ width: progressPercent(perk) + '%' }"></div>
                </div>
                <div class="stock-info">
                  <span class="code-tag">{{ perk.code }}</span>
                  <template v-if="quoteFor(perk.code)">
                    <span class="price">{{ quoteFor(perk.code)!.price.toFixed(2) }}</span>
                    <span class="change" :class="quoteFor(perk.code)!.changePct >= 0 ? 'up' : 'down'">
                      {{ quoteFor(perk.code)!.changePct >= 0 ? '+' : '' }}{{ (quoteFor(perk.code)!.changePct || 0).toFixed(2) }}%
                    </span>
                  </template>
                </div>
              </div>
            </template>
          </div>
        </template>
      </div>

      <div v-if="adminVisible" id="admin-tools" style="margin-top:14px;border:1px dashed var(--border);border-radius:8px;padding:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <span style="font-size:13px;font-weight:600;">🛠️ 数据管理</span>
          <span style="font-size:10px;color:var(--text-muted);cursor:pointer;" @click="adminVisible = false">关闭</span>
        </div>
        <div style="margin-bottom:8px;">
          <span style="font-size:11px;color:var(--text-dim);">添加/编辑股东回馈记录（JSON格式编辑后保存）</span>
        </div>
        <textarea v-model="editArea" rows="10" style="width:100%;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:12px;font-family:monospace;padding:8px;outline:none;resize:vertical;"></textarea>
        <div style="margin-top:8px;display:flex;gap:8px;">
          <button class="btn" style="font-size:12px;" @click="savePerksEdit">💾 保存</button>
          <button class="btn btn-secondary" style="font-size:12px;" @click="loadPerksEdit">🔄 加载当前数据</button>
          <span :style="{ fontSize: '11px', color: editMsgColor, alignSelf: 'center' }">{{ editMsg }}</span>
        </div>
      </div>

      <div class="legend">
        <p>📌 数据来源：<a href="https://www.cninfo.com.cn/new/fulltextSearch?notautosubmit=&keyWord=股东回馈活动" target="_blank" style="color:var(--accent);">巨潮资讯网公告搜索「股东回馈活动」</a>（证监会指定披露平台） + 人工整理</p>
        <p>📌 <strong>进行中</strong> — 当前可参与 · <strong>即将开始</strong> — 尚未开始 · <strong>已结束</strong> — 无法参与</p>
        <p>💡 持有足够数量的股票即可按公告要求领取福利，部分公司需在股权登记日持有</p>
        <p style="margin-top:6px;"><span style="color:var(--text-muted);font-size:10px;cursor:pointer;" @click="toggleAdminTools">🔧 管理员入口</span></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { getPerks, updatePerks } from '@/services/etfApi';
import '@/styles/perks.css';

interface Quote {
  price: number;
  changePct: number;
}

interface Perk {
  code: string;
  name: string;
  perkName?: string;
  description?: string;
  startDate?: string;
  endDate?: string;
  status?: string;
  minShares?: number;
  benefit?: string;
  sourceUrl?: string;
  _fromCninfo?: boolean;
}

const allPerks = ref<Perk[]>([]);
const allQuotes = ref<Record<string, Quote>>({});
const displayPerks = ref<Perk[]>([]);
const searchInput = ref('');
const statusFilter = ref('all');
const shareFilter = ref('all');
const sourceFilter = ref('all');
const loading = ref(true);
const loadFailed = ref(false);
const dotClass = ref('loading');
const utext = ref('加载中...');
const statsHtml = ref('<span style="color:var(--text-dim);font-size:11px;">等待数据...</span>');

const adminVisible = ref(false);
const editArea = ref('');
const editMsg = ref('');
const editMsgColor = ref('var(--text-dim)');

let refreshTimer: ReturnType<typeof setInterval> | null = null;
let editMsgTimer: ReturnType<typeof setTimeout> | null = null;

function perkKey(perk: Perk, idx: number) {
  return perk.code + (perk.perkName || '') + idx;
}

function quoteFor(code: string) {
  const q = allQuotes.value[code];
  return q?.price ? q : null;
}

function progressPercent(perk: Perk) {
  const start = new Date(perk.startDate || '').getTime();
  const end = new Date(perk.endDate || '').getTime();
  const now = Date.now();
  if (now < start) return 0;
  if (now > end) return 100;
  return Math.round((now - start) / (end - start) * 100);
}

function statusText(perk: Perk) {
  switch (perk.status) {
    case 'ongoing': return '🟢 进行中';
    case 'ended': return '🔴 已结束';
    case 'upcoming': return '🟡 即将开始';
    default: return perk.status || '';
  }
}

function daysLeft(perk: Perk) {
  const today = new Date();
  const end = new Date(perk.endDate || '');
  const diff = Math.ceil((end.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  if (diff > 0) return `${diff}天后结束`;
  if (diff === 0) return '今天最后一天';
  return '已结束';
}

function renderStats() {
  if (!allPerks.value.length) {
    statsHtml.value = '<span style="color:var(--text-dim);font-size:11px;">暂无数据</span>';
    return;
  }
  const t = allPerks.value.length;
  const ongoing = allPerks.value.filter(p => p.status === 'ongoing').length;
  const ended = allPerks.value.filter(p => p.status === 'ended').length;
  const upcoming = allPerks.value.filter(p => p.status === 'upcoming').length;
  statsHtml.value = `
    <span>总数 <b>${t}</b></span>
    <span class="pill ongoing">🟢 进行中 ${ongoing}</span>
    <span class="pill upcoming">🟡 即将 ${upcoming}</span>
    <span class="pill ended">🔴 已结束 ${ended}</span>
    <span style="color:var(--text-dim);font-size:11px;margin-left:auto;">${new Date().toLocaleDateString('zh-CN')}</span>
  `;
}

function renderCards() {
  const maxShares = shareFilter.value !== 'all' ? parseInt(shareFilter.value) : null;
  displayPerks.value = maxShares != null
    ? allPerks.value.filter(p => (p.minShares ?? 0) <= maxShares)
    : allPerks.value.slice();
}

async function loadData() {
  loading.value = true;
  loadFailed.value = false;
  dotClass.value = 'loading';
  utext.value = '加载中...';

  try {
    const json = await getPerks(statusFilter.value, searchInput.value, sourceFilter.value);
    allPerks.value = json.perks || [];
    allQuotes.value = json.quotes || {};
    renderStats();
    renderCards();
    dotClass.value = '';
    utext.value = new Date().toLocaleString('zh-CN');
  } catch (e) {
    console.error('加载失败:', e);
    loadFailed.value = true;
    dotClass.value = 'fail';
    utext.value = '失败';
  } finally {
    loading.value = false;
  }
}

function onFilter() {
  loadData();
}

function onReset() {
  searchInput.value = '';
  statusFilter.value = 'all';
  shareFilter.value = 'all';
  sourceFilter.value = 'all';
  loadData();
}

function toggleAdminTools() {
  if (!adminVisible.value) {
    adminVisible.value = true;
    loadPerksEdit();
  } else {
    adminVisible.value = false;
  }
}

function loadPerksEdit() {
  editArea.value = JSON.stringify(allPerks.value, null, 2);
  editMsg.value = '已加载当前数据，可编辑后保存';
  editMsgColor.value = 'var(--text-dim)';
}

function showEditMsg(text: string, isErr = false) {
  editMsg.value = text;
  editMsgColor.value = isErr ? 'var(--red)' : 'var(--green)';
  if (editMsgTimer) clearTimeout(editMsgTimer);
  editMsgTimer = setTimeout(() => { editMsgColor.value = 'var(--text-dim)'; }, 3000);
}

async function savePerksEdit() {
  let newData: Perk[];
  try {
    newData = JSON.parse(editArea.value);
    if (!Array.isArray(newData)) throw new Error('必须是数组格式');
  } catch (e) {
    showEditMsg('JSON格式错误: ' + (e instanceof Error ? e.message : ''), true);
    return;
  }

  try {
    const json = await updatePerks(newData);
    if (json.ok) {
      showEditMsg(`✅ 保存成功！共 ${json.count} 条记录`);
      setTimeout(loadData, 1000);
    } else {
      showEditMsg('保存失败: ' + (json.error || '未知错误'), true);
    }
  } catch (e) {
    showEditMsg('保存失败: ' + (e instanceof Error ? e.message : ''), true);
  }
}

onMounted(() => {
  loadData();
  refreshTimer = setInterval(loadData, 60000);
});

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer);
  if (editMsgTimer) clearTimeout(editMsgTimer);
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}
</style>
