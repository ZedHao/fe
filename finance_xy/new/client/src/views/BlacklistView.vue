<template>
  <div class="header">
    <div class="header-inner">
      <div class="header-left">
        <img src="/logo.jpg" class="logo-avatar" alt="猪猪">
        <div class="header-title">
          <h1><span class="accent">猪猪基金</span><span class="light"> 黑名单股票池</span></h1>
          <div style="font-size:11px;color:var(--text-dim);">⚠️ 2026年问题股 · 避雷参考</div>
        </div>
      </div>
      <div class="header-right">
        <router-link to="/" class="btn btn-secondary" style="font-size:11px;padding:6px 10px;text-decoration:none;">📊 返回基金折溢价</router-link>
        <button class="btn" style="font-size:11px;padding:6px 10px;" @click="showAddDialog">➕ 新增股票</button>
        <button class="btn" style="font-size:11px;padding:6px 10px;background:linear-gradient(135deg,#8b5cf6,#6366f1);" @click="showQueryDialog">🔍 风险查询</button>
        <button class="btn" style="font-size:11px;padding:6px 10px;" @click="loadBlacklist">🔄 刷新</button>
      </div>
    </div>
  </div>

  <div class="main">
    <div class="stocks-count" id="countBar">
      <span v-html="countBarHtml"></span>
      <span style="font-size:11px;color:var(--text-muted);">数据来源: 2026问题股.xlsx</span>
    </div>

    <div class="search-bar">
      <input
        v-model="searchInput"
        type="text"
        id="searchInput"
        placeholder="🔍 输入股票代码/名称，回车查风险..."
        autocomplete="off"
        @input="onFilter"
        @keydown="onSearchKeydown"
      >
      <span class="search-hint">↩ 回车=查询风险 / 列表过滤</span>
    </div>

    <div class="table-wrap">
      <div v-if="loading" style="text-align:center;padding:40px 20px;color:var(--text-dim);" id="loadingState">
        <div style="width:30px;height:30px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;margin:0 auto 12px;animation:spin .8s linear infinite;"></div>
        <p>正在加载黑名单数据...</p>
      </div>
      <div v-else class="table-scroll" id="tableWrap">
        <table>
          <thead>
            <tr>
              <th style="width:50px;">#</th>
              <th>股票代码</th>
              <th>股票名称</th>
              <th>风险原因</th>
              <th style="width:180px;text-align:center;">操作</th>
            </tr>
          </thead>
          <tbody id="tableBody">
            <tr v-for="(s, i) in filteredStocks" :key="s.code">
              <td style="color:var(--text-muted);font-size:11px;">{{ i + 1 }}</td>
              <td class="code-col">{{ s.code }}</td>
              <td><strong>{{ s.name || '-' }}</strong></td>
              <td class="reason-col">
                <template v-if="s.reason">{{ s.reason }}</template>
                <span v-else style="color:var(--text-muted);">待补充</span>
              </td>
              <td style="text-align:center;">
                <div class="row-actions" style="justify-content:center;">
                  <button
                    class="btn-sm btn-secondary"
                    style="background:rgba(139,92,246,0.15);color:#a78bfa;border-color:rgba(139,92,246,0.3);"
                    @click="queryRisk(s.code)"
                  >🔍 查风险</button>
                  <button class="btn-sm btn-danger" @click="removeStock(s.code)">🗑 删除</button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredStocks.length === 0">
              <td colspan="5" style="text-align:center;padding:30px;color:var(--text-dim);">
                {{ searchTrimmed ? '未找到匹配的股票' : '黑名单为空' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- 内联风险查询弹窗 -->
  <Teleport to="body">
    <div v-if="inlineQueryVisible" class="overlay" id="inlineQueryDialog">
      <div class="modal" style="min-width:460px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <h3 style="margin:0;font-size:17px;">🔍 股票风险查询</h3>
          <button style="background:none;border:none;color:var(--text-dim);font-size:24px;cursor:pointer;" @click="closeDialog('inlineQueryDialog')">&times;</button>
        </div>
        <div class="field">
          <label>股票代码</label>
          <div style="display:flex;gap:10px;">
            <input
              v-model="inlineQueryCode"
              type="text"
              id="inlineQueryCode"
              style="flex:1;font-size:14px;padding:9px 12px;"
              autocomplete="off"
              @keydown.enter="doInlineQuery"
            >
            <button class="btn" style="font-size:13px;padding:9px 18px;" @click="doInlineQuery">查询</button>
          </div>
        </div>
        <div v-if="inlineQueryResultHtml" id="inlineQueryResult" v-html="inlineQueryResultHtml"></div>
        <div v-if="inlineQueryLoading" id="inlineQueryLoading" style="text-align:center;padding:22px;">
          <div class="spinner" style="margin:0 auto 10px;width:24px;height:24px;"></div>
          <span style="color:var(--text-dim);font-size:14px;">正在查询，请稍候...</span>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- 风险查询弹窗（独立入口） -->
  <Teleport to="body">
    <div v-if="queryDialogVisible" class="overlay" id="queryDialog">
      <div class="modal" style="min-width:460px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <h3 style="margin:0;font-size:17px;">🔍 股票风险查询</h3>
          <button style="background:none;border:none;color:var(--text-dim);font-size:24px;cursor:pointer;" @click="closeDialog('queryDialog')">&times;</button>
        </div>
        <div class="field">
          <label>股票代码 *</label>
          <div style="display:flex;gap:10px;">
            <input
              ref="queryCodeInput"
              v-model="queryCode"
              type="text"
              id="queryCode"
              placeholder="例如 000002"
              style="flex:1;font-size:14px;padding:9px 12px;"
              autocomplete="off"
              @keydown.enter="doQueryRisk"
            >
            <button class="btn" style="font-size:13px;padding:9px 18px;" @click="doQueryRisk">查询</button>
          </div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:5px;">可查询：审计意见 · 证监会立案 · ST风险 · 黑名单状态</div>
        </div>
        <div v-if="queryResultHtml" id="queryResult" v-html="queryResultHtml"></div>
        <div v-if="queryLoading" id="queryLoading" style="text-align:center;padding:22px;">
          <div class="spinner" style="margin:0 auto 10px;width:24px;height:24px;"></div>
          <span style="color:var(--text-dim);font-size:14px;">正在查询，请稍候...</span>
        </div>
        <div class="btns">
          <button class="btn btn-secondary" @click="closeDialog('queryDialog')">关闭</button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- 新增股票弹窗 -->
  <Teleport to="body">
    <div v-if="addDialogVisible" class="overlay" id="addDialog">
      <div class="modal">
        <h3>➕ 新增黑名单股票</h3>
        <div class="error-msg" id="addError">{{ addError }}</div>
        <div class="field">
          <label>股票代码 *</label>
          <input ref="addCodeInput" v-model="addCode" type="text" id="addCode" placeholder="例如 600519" autocomplete="off">
        </div>
        <div class="field">
          <label>股票名称</label>
          <input v-model="addName" type="text" id="addName" placeholder="例如 贵州茅台" autocomplete="off">
        </div>
        <div class="field">
          <label>风险原因</label>
          <textarea v-model="addReason" id="addReason" placeholder="例如：涉嫌违规立案、净资产为负、营收不足..."></textarea>
        </div>
        <div class="btns">
          <button class="btn btn-secondary" @click="closeDialog('addDialog')">取消</button>
          <button class="btn" @click="addStock">确认添加</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue';
import {
  addBlacklist, getBlacklist, getStockRisk, removeBlacklist,
} from '@/services/etfApi';

interface StockItem {
  code: string;
  name: string;
  reason: string;
}

interface RiskData {
  code: string;
  name?: string;
  inBlacklist?: boolean;
  blacklistReason?: string;
  auditOpinion?: string;
  auditOpinionDesc?: string;
  csrcCase?: string;
  csrcCaseDesc?: string;
  stRisk?: string;
  stRiskDesc?: string;
}

const stockList = ref<StockItem[]>([]);
const loading = ref(true);
const searchInput = ref('');

const inlineQueryVisible = ref(false);
const inlineQueryCode = ref('');
const inlineQueryLoading = ref(false);
const inlineQueryResultHtml = ref('');

const queryDialogVisible = ref(false);
const queryCode = ref('');
const queryLoading = ref(false);
const queryResultHtml = ref('');
const queryCodeInput = ref<HTMLInputElement | null>(null);

const addDialogVisible = ref(false);
const addCode = ref('');
const addName = ref('');
const addReason = ref('');
const addError = ref('');
const addCodeInput = ref<HTMLInputElement | null>(null);

const searchTrimmed = computed(() => searchInput.value.toLowerCase().trim());

const filteredStocks = computed(() => {
  const search = searchTrimmed.value;
  if (!search) return stockList.value;
  return stockList.value.filter((s) =>
    s.code.toLowerCase().includes(search)
    || (s.name || '').toLowerCase().includes(search));
});

const countBarHtml = computed(() => {
  const total = stockList.value.length;
  const filtered = filteredStocks.value.length;
  const search = searchTrimmed.value;
  if (search && filtered !== total) {
    return `📋 黑名单股票总数: <span class="num">${total}</span> 只 <span style="color:var(--text-dim);font-size:12px;">（搜索筛出 ${filtered} 只）</span>`;
  }
  return `📋 黑名单股票总数: <span class="num">${total}</span> 只`;
});

async function loadBlacklist() {
  loading.value = true;
  try {
    const json = await getBlacklist();
    if (json.ok && json.list) {
      stockList.value = json.list;
    }
  } catch (e) {
    alert(`加载失败: ${(e as Error).message}`);
  }
  loading.value = false;
}

function onFilter() {
  // renderTable 由 computed 响应式实现
}

function onSearchKeydown(e: KeyboardEvent) {
  if (e.key !== 'Enter') return;
  const val = searchInput.value.trim();
  if (!val) return;
  e.preventDefault();
  if (/^\d{5,8}$/.test(val)) {
    queryRiskInline(val);
  } else {
    const matched = stockList.value.filter((s) =>
      s.code.includes(val)
      || (s.name || '').toLowerCase().includes(val.toLowerCase()));
    if (matched.length === 1) {
      queryRiskInline(matched[0].code);
    } else if (matched.length === 0) {
      queryRiskInline(val);
    }
  }
}

function queryRiskInline(code: string) {
  inlineQueryCode.value = code;
  inlineQueryResultHtml.value = '';
  inlineQueryLoading.value = false;
  inlineQueryVisible.value = true;
  nextTick(() => doInlineQuery());
}

function showQueryDialog() {
  queryCode.value = '';
  queryResultHtml.value = '';
  queryLoading.value = false;
  queryDialogVisible.value = true;
  nextTick(() => queryCodeInput.value?.focus());
}

function queryRisk(code: string) {
  showQueryDialog();
  setTimeout(() => {
    queryCode.value = code;
    doQueryRisk();
  }, 100);
}

async function doInlineQuery() {
  const code = inlineQueryCode.value.trim();
  if (!code) {
    alert('请输入股票代码');
    return;
  }
  inlineQueryResultHtml.value = '';
  inlineQueryLoading.value = true;
  try {
    const json = await getStockRisk(code);
    inlineQueryLoading.value = false;
    if (json.ok && json.data) {
      inlineQueryResultHtml.value = buildRiskResultHTML(json.data, 'inline');
    } else {
      inlineQueryResultHtml.value = `<div style="text-align:center;padding:20px;color:var(--red);font-size:13px;">查询失败: ${json.error || '未知错误'}</div>`;
    }
  } catch (e) {
    inlineQueryLoading.value = false;
    inlineQueryResultHtml.value = `<div style="text-align:center;padding:20px;color:var(--red);font-size:13px;">网络错误: ${(e as Error).message}</div>`;
  }
}

async function doQueryRisk() {
  const code = queryCode.value.trim();
  if (!code) {
    alert('请输入股票代码');
    return;
  }
  queryResultHtml.value = '';
  queryLoading.value = true;
  try {
    const json = await getStockRisk(code);
    queryLoading.value = false;
    if (json.ok && json.data) {
      queryResultHtml.value = buildRiskResultHTML(json.data, 'query');
    } else {
      queryResultHtml.value = `<div style="text-align:center;padding:20px;color:var(--red);font-size:13px;">查询失败: ${json.error || '未知错误'}</div>`;
    }
  } catch (e) {
    queryLoading.value = false;
    queryResultHtml.value = `<div style="text-align:center;padding:20px;color:var(--red);font-size:13px;">网络错误: ${(e as Error).message}</div>`;
  }
}

function riskClass(val: string | undefined) {
  if (!val) return '';
  if (val.includes('非标准') || val.includes('立案') || val.includes('ST') || val.includes('风险') || val.includes('亏损') || val.includes('净资产为负') || val.includes('营收不足')) return 'risk-warn';
  if (val.includes('标准') || val.includes('未发现') || val.includes('暂未')) return 'risk-ok';
  return 'risk-info';
}

function buildRiskResultHTML(d: RiskData, source: 'inline' | 'query') {
  let blHtml = '';
  if (d.inBlacklist) {
    blHtml = `<span class="tag tag-bl">🚫 已在黑名单${d.blacklistReason ? `: ${d.blacklistReason}` : ''}</span>`;
  } else {
    blHtml = '<span class="tag tag-notbl">✅ 不在黑名单中</span>';
  }

  const btnId = `add-bl-${source}-${d.code}`;

  return ''
    + '<div class="risk-result">'
    + `<div style="font-size:16px;font-weight:600;margin-bottom:6px;">${d.name || d.code} <span style="font-size:12px;color:var(--text-dim);font-weight:400;">${d.code}</span></div>`
    + `<div class="bl-status">${blHtml}</div>`
    + '<div class="risk-item">'
    + '<div class="label">📄 财务报告审计意见</div>'
    + `<div class="value ${riskClass(d.auditOpinion)}">${d.auditOpinion || '未知'}</div>`
    + (d.auditOpinionDesc ? `<div class="desc">${d.auditOpinionDesc}</div>` : '')
    + '</div>'
    + '<div class="risk-item">'
    + '<div class="label">⚖️ 证监会立案调查</div>'
    + `<div class="value ${riskClass(d.csrcCase)}">${d.csrcCase || '未知'}</div>`
    + (d.csrcCaseDesc ? `<div class="desc">${d.csrcCaseDesc}</div>` : '')
    + '</div>'
    + '<div class="risk-item">'
    + '<div class="label">⚠️ ST风险（财务指标）</div>'
    + `<div class="value ${riskClass(d.stRisk)}">${d.stRisk || '未知'}</div>`
    + (d.stRiskDesc ? `<div class="desc">${d.stRiskDesc}</div>` : '')
    + '</div>'
    + '<div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--border);font-size:11px;color:var(--text-muted);text-align:center;">'
    + '数据源：东方财富 · 巨潮资讯 · 腾讯行情 · 仅供参考'
    + '</div>'
    + '</div>'
    + '<div style="margin-top:10px;display:flex;gap:10px;">'
    + `<button class="btn-sm btn-secondary" data-add-bl="${btnId}" data-code="${d.code}" data-name="${(d.name || '').replace(/"/g, '&quot;')}" style="flex:1;border:1px solid var(--border);font-size:13px;padding:8px 14px;">➕ 加入黑名单</button>`
    + '</div>';
}

function addSearchedToBlacklist(code: string, name: string) {
  closeDialog('inlineQueryDialog');
  closeDialog('queryDialog');
  showAddDialog();
  addCode.value = code;
  addName.value = name;
}

function showAddDialog() {
  addCode.value = '';
  addName.value = '';
  addReason.value = '';
  addError.value = '';
  addDialogVisible.value = true;
  nextTick(() => addCodeInput.value?.focus());
}

async function addStock() {
  const code = addCode.value.trim();
  const name = addName.value.trim();
  const reason = addReason.value.trim();

  if (!code) {
    addError.value = '请输入股票代码';
    return;
  }

  try {
    const json = await addBlacklist(code, name, reason);
    if (json.ok) {
      closeDialog('addDialog');
      loadBlacklist();
    } else {
      addError.value = json.error || '添加失败';
    }
  } catch (e) {
    addError.value = `网络错误: ${(e as Error).message}`;
  }
}

async function removeStock(code: string) {
  if (!confirm(`确定要从黑名单删除 ${code} 吗？`)) return;

  try {
    const json = await removeBlacklist(code);
    if (json.ok) {
      loadBlacklist();
    } else {
      alert(json.error || '删除失败');
    }
  } catch (e) {
    alert(`网络错误: ${(e as Error).message}`);
  }
}

function closeDialog(id: string) {
  if (id === 'inlineQueryDialog') {
    inlineQueryVisible.value = false;
    inlineQueryResultHtml.value = '';
    inlineQueryLoading.value = false;
  } else if (id === 'queryDialog') {
    queryDialogVisible.value = false;
    queryResultHtml.value = '';
    queryLoading.value = false;
  } else if (id === 'addDialog') {
    addDialogVisible.value = false;
    addError.value = '';
  }
}

function handleRiskResultClick(e: MouseEvent) {
  const target = e.target as HTMLElement;
  const btn = target.closest('[data-add-bl]') as HTMLElement | null;
  if (!btn) return;
  addSearchedToBlacklist(btn.dataset.code || '', btn.dataset.name || '');
}

onMounted(() => {
  loadBlacklist();
  document.addEventListener('click', handleRiskResultClick);
});

onUnmounted(() => {
  document.removeEventListener('click', handleRiskResultClick);
});
</script>

<style>
@import '@/styles/blacklist.css';
</style>
