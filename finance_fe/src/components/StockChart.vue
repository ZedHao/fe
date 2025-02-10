<template>
  <div>
    <canvas ref="stockChart"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  props: {
    stockData: {
      type: Object,
      required: true,
    },
  },
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.stockChart.getContext('2d');
      const labels = Object.keys(this.stockData['Time Series (Daily)']).reverse();
      const data = labels.map((date) => this.stockData['Time Series (Daily)'][date]['4. close']);

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: '收盘价',
              data: data,
              borderColor: 'rgba(75, 192, 192, 1)',
              fill: false,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            x: {
              display: true,
              title: {
                display: true,
                text: '日期',
              },
            },
            y: {
              display: true,
              title: {
                display: true,
                text: '价格',
              },
            },
          },
        },
      });
    },
  },
};
</script>
