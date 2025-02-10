export interface StockData {
  date: string;
  code: string;
  open: number;
  high: number;
  low: number;
  close: number;
  preclose: number;
  volume: number;
  amount: number;
  pctChg: number;
}
export const mockStockData: StockData[] = [{
    date: '2017-07-03',
    code: 'sh.600000',
    open: 12.64,
    high: 12.65,
    low: 12.47,
    close: 12.56,
    preclose: 12.65,
    volume: 38778949,
    amount: 486264672,
    pctChg: -0.711456,
  },
  {
    date: '2017-07-04',
    code: 'sh.600000',
    open: 12.55,
    high: 12.58,
    low: 12.41,
    close: 12.55,
    preclose: 12.56,
    volume: 36659128,
    amount: 458434432,
    pctChg: -0.07962,
  },
  {
    date: '2017-07-05',
    code: 'sh.600000',
    open: 12.5,
    high: 12.65,
    low: 12.47,
    close: 12.62,
    preclose: 12.55,
    volume: 26470507,
    amount: 332542464,
    pctChg: 0.557767,
  },
];
