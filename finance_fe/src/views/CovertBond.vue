<template>
  <div class="bond-table-container">
    <table class="bond-table">
      <thead>
      <tr>
        <th v-for="column in tableColumns" :key="column.key" @click="sortColumn(column.key)">
          {{ column.title }}
          <span v-if="sortColumnKey === column.key">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="item in bondData" :key="item.SECURITY_CODE">
        <td v-for="column in tableColumns" :key="column.key">
          <!-- 使用自定义格式化函数 -->
          <span v-if="column.formatter">{{ column.formatter(item[column.key]) }}</span>
          <!-- 或者直接显示数据 -->
          <span v-else>{{ item[column.key] }}</span>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue';
import { getCoverBondData } from '../services/stockApi';
import Header from "@/components/Header.vue";

// 表格列配置
const tableColumns = [
  { key: 'SECURITY_CODE', title: '债券代码' },
  { key: 'SECURITY_NAME_ABBR', title: '债券简称' },
  { key: 'PUBLIC_START_DATE', title: '申购日期' },
  { key: 'CORRECODE', title: '申购代码' },
  { key: 'TRANSFER_PRICE', title: '转股价' },
  {
    key: 'ONLINE_GENERAL_AAU',
    title: '申购上限(万元)',
    formatter: value => value ? (value / 10000).toFixed(2) : '-'
  },
  { key: 'CONVERT_STOCK_CODE', title: '正股代码' },
  { key: 'SECURITY_SHORT_NAME', title: '正股简称' },
  { key: 'CONVERT_STOCK_PRICE', title: '正股价' },
  { key: 'TRANSFER_VALUE', title: '转股价值' },
  { key: 'CURRENT_BOND_PRICE', title: '债现价' },
  { key: 'TRANSFER_PREMIUM_RATIO', title: '转股溢价率' },
  { key: 'FIRST_PER_PREPLACING', title: '原股东配售' },
  { key: 'ACTUAL_ISSUE_SCALE', title: '发行规模(亿元)' },
  { key: 'LISTING_DATE', title: '上市时间' },
  { key: 'RATING', title: '信用评级' }
];

// 表格状态
const bondData = ref([]);
const loading = ref(false);
const error = ref(null);

// 分页状态
const currentPage = ref(1);
const pageSize = ref(20);
const totalPages = ref(1);

// 排序状态
const sortColumnKey = ref('TRANSFER_PREMIUM_RATIO');
const sortType = ref(1); // 1: 升序, -1: 降序

// 计算属性：生成页码列表
const pageNumbers = computed(() => {
  const displayRange = 5; // 显示的页码范围
  let start = Math.max(1, currentPage.value - Math.floor(displayRange / 2));
  let end = Math.min(start + displayRange - 1, totalPages.value);

  if (end - start < displayRange - 1) {
    start = Math.max(1, end - displayRange + 1);
  }

  return Array.from({ length: end - start + 1 }, (_, i) => start + i);
});

// 获取债券数据
const fetchBondData = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await getCoverBondData(
      sortColumnKey.value,
      sortType.value === 1 ? 'asc' : 'desc', // 假设API需要asc/desc参数
      currentPage.value,
      pageSize.value
    );

    bondData.value = response.data.result.data || [];
    totalPages.value = response.data.result.pages || 1;
  } catch (err) {
    error.value = err.message || '获取数据失败';
    console.error('Error fetching bond data:', err);
  } finally {
    loading.value = false;
  }
};

// 处理列排序
const sortColumn = (column) => {
  if (sortColumnKey.value === column) {
    sortType.value = -sortType.value; // 切换排序方向
  } else {
    sortColumnKey.value = column;
    sortType.value = 1; // 默认升序
  }
  currentPage.value = 1; // 重置页码
  fetchBondData(); // 重新获取数据
};

// 分页控制
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    fetchBondData();
  }
};

const prevPage = () => goToPage(currentPage.value - 1);
const nextPage = () => goToPage(currentPage.value + 1);

// 初始化数据
onMounted(fetchBondData);
</script>


<<style scoped>
.cbond-page {
  padding: 20px;
  background-color: #0d0d0d;
  color: #fff;
  min-height: 100vh;
  font-size: 14px; /* 页面基础字体大小调整 */

}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em; /* 表格整体字体缩小 */

}

th, td {
  border: 1px solid #2c3e50;
  padding: 8px 12px; /* 内边距微调，适配小字体 */
  text-align: left;
  transition: all 0.3s ease;
  color: #333; /* 文字颜色调整为深灰色，提升可读性 */
}

th {
  background-color: #1abc9c; /* 青绿色背景 */
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 添加阴影 */
}

th:hover {
  background-color: #16a085; /* 悬停时更深的青绿色 */
}

td {
  background-color: #ecf0f1; /* 浅灰色背景 */
}

td:hover {
  background-color: #d4e6f1; /* 悬停时更浅的蓝色 */
}

.pagination {
  margin-top: 15px;
  font-size: 13px; /* 分页区域单独调整字体 */
}

.pagination button {
  margin: 0 3px;
  padding: 4px 8px; /* 按钮内边距适配小字体 */
  font-size: inherit; /* 继承父级字体大小 */
}
</style>
