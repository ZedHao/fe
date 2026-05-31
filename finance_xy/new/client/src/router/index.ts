import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import PremiumView from '@/views/PremiumView.vue';
import BlacklistView from '@/views/BlacklistView.vue';
import CalendarView from '@/views/CalendarView.vue';
import FuturesView from '@/views/FuturesView.vue';
import HouseView from '@/views/HouseView.vue';
import PerksView from '@/views/PerksView.vue';

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'Premium', component: PremiumView },
  { path: '/blacklist', name: 'Blacklist', component: BlacklistView },
  { path: '/calendar', name: 'Calendar', component: CalendarView },
  { path: '/futures', name: 'Futures', component: FuturesView },
  { path: '/house', name: 'House', component: HouseView },
  { path: '/perks', name: 'Perks', component: PerksView },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
