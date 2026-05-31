import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE || '';

const api = axios.create({ baseURL: BASE_URL, timeout: 15000 });

export interface FundRow {
  code: string;
  name: string;
  market: string;
  type: string;
  price: number | null;
  nav: number | null;
  estNav: number | null;
  premium: number | null;
  realPremium: number | null;
  changePct: number;
  amount: number;
  sgzt: string;
  sgLimit: string;
  isCustom?: boolean;
}

export interface PremiumResponse {
  data: FundRow[];
  indexes: { name: string; code: string; price: number; change: number }[];
}

export async function getPremium(): Promise<PremiumResponse> {
  const res = await api.get('/api/premium');
  return res.data.data;
}

export interface FundLimitResponse {
  ok: boolean;
  code?: string;
  status?: string;
  limit?: string;
  limitNum?: number | null;
  limitUnit?: string;
  detailHtml?: string;
  error?: string;
}

export interface FundHistoryResponse {
  ok: boolean;
  code?: string;
  name?: string;
  history?: {
    date: string;
    price: number;
    nav: number;
    premium: number;
    shares?: number;
  }[];
  shares?: {
    current?: number;
    quarterHistory?: { date: string; totalShares: string }[];
  };
  error?: string;
}

export async function getFundHistory(code: string): Promise<FundHistoryResponse> {
  const res = await api.get(`/api/fund-history/${code}`);
  return res.data;
}

export async function getFundLimit(code: string): Promise<FundLimitResponse> {
  const res = await api.get(`/api/fund-limit/${code}`);
  return res.data;
}

export async function addFund(code: string, name?: string) {
  const res = await api.post('/api/add-fund', { code, name });
  return res.data;
}

export async function removeFund(code: string) {
  const res = await api.post('/api/remove-fund', { code });
  return res.data;
}

export async function getBlacklist() {
  const res = await api.get('/api/blacklist');
  return res.data;
}

export async function addBlacklist(code: string, name?: string, reason?: string) {
  const res = await api.post('/api/blacklist/add', { code, name, reason });
  return res.data;
}

export async function removeBlacklist(code: string) {
  const res = await api.post('/api/blacklist/remove', { code });
  return res.data;
}

export async function getStockRisk(code: string) {
  const res = await api.get(`/api/stock-risk/${code}`);
  return res.data;
}

export async function getCalendar() {
  const res = await api.get('/api/calendar');
  return res.data;
}

export async function getFuturesBasis() {
  const res = await api.get('/api/futures-basis');
  return res.data;
}

export async function getFuturesDetail(symbol: string) {
  const res = await api.get(`/api/futures-detail/${symbol}`);
  return res.data;
}

export async function getHousePrices(city = 'suzhou') {
  const res = await api.get('/api/house-prices', { params: { city } });
  return res.data;
}

export async function getPerks(filter = 'all', search = '', source = 'all') {
  const params: Record<string, string> = { filter, search };
  if (source !== 'all') params.filter = source;
  const res = await api.get('/api/perks', { params });
  return res.data;
}

export async function updatePerks(perks: unknown[]) {
  const res = await api.post('/api/perks/update', { perks });
  return res.data;
}
