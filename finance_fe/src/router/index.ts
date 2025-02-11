import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Stock from '@/views/Stock.vue';
import Home from '@/views/Home.vue';

const routes: Array<RouteRecordRaw> = [
  { path: '/', name: 'Home', component: Home },

  { path: '/stock', name: 'Detail', component: Stock, props: true },

];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
