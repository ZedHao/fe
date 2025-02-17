<template>
  <div class="cbond-page">
    <Header />
    <table>
      <thead>
      <tr>
        <th @click="sortColumn('SECURITY_CODE')">债券代码
          <span v-if="sortColumnKey === 'SECURITY_CODE'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('SECURITY_NAME_ABBR')">债券简称
          <span v-if="sortColumnKey === 'SECURITY_NAME_ABBR'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th>相关</th>
        <th @click="sortColumn('PUBLIC_START_DATE')">申购日期
          <span v-if="sortColumnKey === 'PUBLIC_START_DATE'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('CORRECODE')">申购代码
          <span v-if="sortColumnKey === 'CORRECODE'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('ONLINE_GENERAL_AAU')">申购上限(万元)
          <span v-if="sortColumnKey === 'ONLINE_GENERAL_AAU'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('CONVERT_STOCK_CODE')">正股代码
          <span v-if="sortColumnKey === 'CONVERT_STOCK_CODE'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('SECURITY_SHORT_NAME')">正股简称
          <span v-if="sortColumnKey === 'SECURITY_SHORT_NAME'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('CONVERT_STOCK_PRICE')">正股价
          <span v-if="sortColumnKey === 'CONVERT_STOCK_PRICE'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('TRANSFER_PRICE')">转股价
          <span v-if="sortColumnKey === 'TRANSFER_PRICE'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('TRANSFER_VALUE')">转股价值
          <span v-if="sortColumnKey === 'TRANSFER_VALUE'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('CURRENT_BOND_PRICE')">债现价
          <span v-if="sortColumnKey === 'CURRENT_BOND_PRICE'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('TRANSFER_PREMIUM_RATIO')">转股溢价率
          <span v-if="sortColumnKey === 'TRANSFER_PREMIUM_RATIO'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('FIRST_PER_PREPLACING')">原股东配售
          <span v-if="sortColumnKey === 'FIRST_PER_PREPLACING'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('ACTUAL_ISSUE_SCALE')">发行规模(亿元)
          <span v-if="sortColumnKey === 'ACTUAL_ISSUE_SCALE'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th>中签号发布日</th>
        <th @click="sortColumn('ONLINE_GENERAL_LWR')">中签率
          <span v-if="sortColumnKey === 'ONLINE_GENERAL_LWR'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('FIRST_PROFIT')">每中一签获利(元)
          <span v-if="sortColumnKey === 'FIRST_PROFIT'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('LISTING_DATE')">上市时间
          <span v-if="sortColumnKey === 'LISTING_DATE'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
        <th @click="sortColumn('RATING')">信用评级
          <span v-if="sortColumnKey === 'RATING'">{{ sortType === 1 ? '↑' : '↓' }}</span>
        </th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="item in bondData" :key="item.SECURITY_CODE">
        <td>{{ item.SECURITY_CODE }}</td>
        <td>{{ item.SECURITY_NAME_ABBR }}</td>
        <td></td> <!-- 这里根据实际情况填充数据 -->
        <td>{{ item.PUBLIC_START_DATE }}</td>
        <td>{{ item.CORRECODE }}</td>
        <td>{{ item.ONLINE_GENERAL_AAU / 10000 }}</td>
        <td>{{ item.CONVERT_STOCK_CODE }}</td>
        <td>{{ item.SECURITY_SHORT_NAME }}</td>
        <td>{{ item.CONVERT_STOCK_PRICE }}</td>
        <td>{{ item.TRANSFER_PRICE }}</td>
        <td>{{ item.TRANSFER_VALUE }}</td>
        <td>{{ item.CURRENT_BOND_PRICE }}</td>
        <td>{{ item.TRANSFER_PREMIUM_RATIO }}</td>
        <td>{{ item.FIRST_PER_PREPLACING }}</td>
        <td>{{ item.ACTUAL_ISSUE_SCALE }}</td>
        <td></td> <!-- 这里根据实际情况填充数据 -->
        <td>{{ item.ONLINE_GENERAL_LWR }}</td>
        <td>{{ item.FIRST_PROFIT }}</td>
        <td>{{ item.LISTING_DATE }}</td>
        <td>{{ item.RATING }}</td>
      </tr>
      </tbody>
    </table>
    <div class="pagination">
      <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {getCoverBondData} from '../services/stockApi';
import Header from "@/components/Header.vue";

// 存储表格数据
const bondData = ref([]);
// 当前排序的列
const sortColumnKey = ref('TRANSFER_PREMIUM_RATIO');
// 排序类型，1 为升序，-1 为降序
const sortType = ref(1);
// 当前页码
const currentPage = ref(1);
// 每页显示的数量
const pageSize = ref(20);
// 总页数
const totalPages = ref(1);

// 获取债券数据
const fetchBondData = async () => {
  try {

    const response = await getCoverBondData(sortColumnKey.value,sortType.value,  currentPage.value,
       pageSize.value)

    bondData.value = response.data.result.data;
    totalPages.value = response.data.result.pages;
  } catch (error) {
    console.error('Error fetching bond data:', error);
  }
};

// 处理列排序
const sortColumn = (column) => {
  if (sortColumnKey.value === column) {
    sortType.value = -sortType.value; // 切换排序类型
  } else {
    sortColumnKey.value = column;
    sortType.value = 1; // 默认升序
  }
  currentPage.value = 1; // 切换排序时回到第一页
  fetchBondData(); // 重新获取排序后的数据
};

// 上一页
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchBondData();
  }
};

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchBondData();
  }
};

onMounted(() => {
  fetchBondData();
});
</script>

<<style scoped>
.cbond-page {
  padding: 20px;
  background-color: #0d0d0d;
  color: #fff;
  min-height: 100vh;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #2c3e50; /* 深灰色边框 */
  padding: 12px; /* 增加内边距 */
  text-align: left;
  transition: all 0.3s ease; /* 添加过渡效果 */
  color: black; /* 设置文字颜色为黑色 */
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
  margin-top: 20px;
}

.pagination button {
  margin: 0 5px;
}
</style>
