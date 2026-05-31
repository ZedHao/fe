export interface HistoryRow {
  date: string;
  price: number;
  nav: number;
  premium: number;
  shares?: number;
}

export function calcStats(data: HistoryRow[]) {
  let sum = 0;
  let max = -Infinity;
  let min = Infinity;
  let pos = 0;
  let neg = 0;
  for (const row of data) {
    const p = row.premium;
    sum += p;
    if (p > max) max = p;
    if (p < min) min = p;
    if (p >= 0) pos += 1;
    else neg += 1;
  }
  return {
    avgPremium: data.length > 0 ? sum / data.length : 0,
    maxPremium: max,
    minPremium: min,
    posDays: pos,
    negDays: neg,
  };
}

export function fmtThousands(s: string) {
  const parts = s.split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return parts.join('.');
}

export function drawHistoryChart(data: HistoryRow[], canvas: HTMLCanvasElement | null) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const rect = canvas.parentElement?.getBoundingClientRect();
  if (!rect) return;
  const W = rect.width - 28;
  const H = 200;
  canvas.width = W * 2;
  canvas.height = H * 2;
  canvas.style.width = `${W}px`;
  canvas.style.height = `${H}px`;
  ctx.scale(2, 2);

  const pad = { top: 20, bottom: 28, left: 44, right: 16 };
  const cw = W - pad.left - pad.right;
  const ch = H - pad.top - pad.bottom;

  const dates = data.map((d) => d.date.slice(5));
  const premiums = data.map((d) => d.premium);
  const prices = data.map((d) => d.price);
  const navs = data.map((d) => d.nav);

  const pMin = Math.min(...premiums);
  const pMax = Math.max(...premiums);
  const pRange = Math.max(pMax - pMin, 1);
  const pZero = pad.top + ch - ((0 - pMin) / pRange) * ch;

  const vMin = Math.min(...prices, ...navs);
  const vMax = Math.max(...prices, ...navs);
  const vRange = Math.max(vMax - vMin, 0.01);

  const stepX = cw / (data.length - 1 || 1);

  ctx.clearRect(0, 0, W, H);

  ctx.strokeStyle = 'rgba(38,46,63,0.4)';
  ctx.lineWidth = 0.5;
  ctx.font = '10px -apple-system, sans-serif';
  ctx.fillStyle = '#4a5568';
  ctx.textAlign = 'right';

  for (let i = 0; i <= 4; i += 1) {
    const y = pad.top + (ch * i) / 4;
    ctx.beginPath();
    ctx.moveTo(pad.left, y);
    ctx.lineTo(W - pad.right, y);
    ctx.stroke();
    ctx.fillText(`${(pMin + pRange * (1 - i / 4)).toFixed(1)}%`, pad.left - 4, y + 3);
  }

  ctx.strokeStyle = 'rgba(79,126,255,0.2)';
  ctx.lineWidth = 1;
  ctx.setLineDash([3, 3]);
  ctx.beginPath();
  ctx.moveTo(pad.left, pZero);
  ctx.lineTo(W - pad.right, pZero);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = '#4a5568';
  ctx.textAlign = 'center';
  const labelStep = Math.max(1, Math.floor(data.length / 8));
  for (let i = 0; i < data.length; i += labelStep) {
    const x = pad.left + i * stepX;
    ctx.fillText(dates[i], x, H - 4);
  }

  const toPriceY = (val: number) => pad.top + ch * (1 - (val - vMin) / vRange);
  const toPremY = (val: number) => pad.top + ch * (1 - (val - pMin) / pRange);

  const barW = Math.max(2, Math.min(stepX * 0.6, 8));
  for (let i = 0; i < data.length; i += 1) {
    const x = pad.left + i * stepX - barW / 2;
    const y = toPremY(premiums[i]);
    const h = pZero - y;
    ctx.fillStyle = premiums[i] >= 0 ? 'rgba(239,68,68,0.7)' : 'rgba(34,197,94,0.7)';
    ctx.fillRect(x, y, barW, Math.abs(h));
  }

  ctx.beginPath();
  ctx.strokeStyle = '#4f7eff';
  ctx.lineWidth = 2;
  for (let i = 0; i < data.length; i += 1) {
    const x = pad.left + i * stepX;
    const y = toPriceY(prices[i]);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  ctx.lineTo(pad.left + (data.length - 1) * stepX, toPriceY(vMin));
  ctx.lineTo(pad.left, toPriceY(vMin));
  ctx.closePath();
  ctx.fillStyle = 'rgba(79,126,255,0.06)';
  ctx.fill();

  ctx.beginPath();
  ctx.strokeStyle = '#f59e0b';
  ctx.lineWidth = 2;
  ctx.setLineDash([4, 3]);
  for (let i = 0; i < data.length; i += 1) {
    const x = pad.left + i * stepX;
    const y = toPriceY(navs[i]);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = '#4a5568';
  ctx.textAlign = 'left';
  for (let i = 0; i <= 3; i += 1) {
    const val = vMin + vRange * (1 - i / 3);
    const y = pad.top + (ch * i) / 3;
    ctx.fillText(val.toFixed(3), W - pad.right + 2, y + 3);
  }
}
