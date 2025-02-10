<template>
  <div>
    <h2>股票列表</h2>
    <ul>
      <li v-for="stock in stocks" :key="stock.symbol" @click="viewStockDetail(stock.symbol)">
        {{ stock.name }} ({{ stock.symbol }})
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      stocks: [
        { symbol: 'AAPL', name: 'Apple Inc.' },
        { symbol: 'GOOGL', name: 'Alphabet Inc.' },
        { symbol: 'MSFT', name: 'Microsoft Corporation' },
      ],
    };
  },
  methods: {
    viewStockDetail(symbol) {
      this.$router.push({ name: 'Detail', params: { symbol } });
    },
  },
};
</script>
