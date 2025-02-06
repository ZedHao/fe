<template>
  <div>
    <h2>股票详情 - {{ symbol }}</h2>
    <StockChart v-if="stockData" :stockData="stockData" />
    <p v-else>加载中...</p>
  </div>
</template>

<script>
import StockChart from '@/components/StockChart.vue';
import stockApi from '@/services/stockApi';

export default {
  components: {
    StockChart,
  },
  data() {
    return {
      symbol: this.$route.params.symbol,
      stockData: null,
    };
  },
  async created() {
    this.stockData = await stockApi.getStockData(this.symbol);
  },
};
</script>
