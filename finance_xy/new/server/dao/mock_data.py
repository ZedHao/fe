"""ETF 业务 mock 数据层。外部行情/巨潮等接口暂用 mock，后续可替换为真实 dao。"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

# ---------- 内置基金池（节选） ----------
BASE_FUNDS = [
    {'c': '510300', 'n': '沪深300ETF', 'm': 'sh', 't': 'ETF'},
    {'c': '510500', 'n': '中证500ETF', 'm': 'sh', 't': 'ETF'},
    {'c': '159915', 'n': '创业板ETF', 'm': 'sz', 't': 'ETF'},
    {'c': '512880', 'n': '证券ETF', 'm': 'sh', 't': 'ETF'},
    {'c': '512690', 'n': '酒ETF', 'm': 'sh', 't': 'ETF'},
    {'c': '518880', 'n': '黄金ETF', 'm': 'sh', 't': 'ETF'},
    {'c': '161725', 'n': '招商中证白酒', 'm': 'sz', 't': 'LOF'},
    {'c': '160222', 'n': '食品LOF', 'm': 'sz', 't': 'LOF'},
    {'c': '164403', 'n': '前海开源沪港深农业', 'm': 'sz', 't': 'LOF'},
    {'c': '501018', 'n': '南方原油LOF', 'm': 'sh', 't': 'LOF'},
]

INDEXES = [
    {'name': '上证指数', 'code': '000001', 'price': 3350.12, 'change': 0.85},
    {'name': '深证成指', 'code': '399001', 'price': 10820.45, 'change': 1.12},
    {'name': '创业板指', 'code': '399006', 'price': 2156.78, 'change': -0.32},
    {'name': '科创50', 'code': '000688', 'price': 982.34, 'change': 0.56},
]

FUTURES_BASIS = [
    {'code': 'IF', 'name': '沪深300', 'exchange': 'cffex', 'price': 3850.2, 'changePct': 0.6,
     'volume': 82000, 'mainContract': 'IF2506', 'contract2Name': 'IF2507',
     'spread': -12.5, 'spreadPct': -0.32, 'isBackwardation': True},
    {'code': 'IC', 'name': '中证500', 'exchange': 'cffex', 'price': 5420.8, 'changePct': 0.4,
     'volume': 45000, 'mainContract': 'IC2506', 'contract2Name': 'IC2507',
     'spread': -8.2, 'spreadPct': -0.15, 'isBackwardation': True},
    {'code': 'AU', 'name': '黄金', 'exchange': 'shfe', 'price': 782.5, 'changePct': 0.2,
     'volume': 120000, 'mainContract': 'au2508', 'contract2Name': 'au2510',
     'spread': 1.2, 'spreadPct': 0.15, 'isBackwardation': False},
]

HOUSE_CITIES = {
    'suzhou': {'cityName': '苏州', 'prices': [
        {'month': '2024-12', 'price': 16800, 'mom': -0.3, 'yoy': -2.1},
        {'month': '2025-01', 'price': 16750, 'mom': -0.3, 'yoy': -2.5},
        {'month': '2025-02', 'price': 16720, 'mom': -0.2, 'yoy': -2.8},
        {'month': '2025-03', 'price': 16680, 'mom': -0.2, 'yoy': -3.0},
        {'month': '2025-04', 'price': 16650, 'mom': -0.2, 'yoy': -3.2},
        {'month': '2025-05', 'price': 16620, 'mom': -0.2, 'yoy': -3.4},
    ]},
    'shanghai': {'cityName': '上海', 'prices': [
        {'month': '2025-03', 'price': 58200, 'mom': 0.1, 'yoy': -1.2},
        {'month': '2025-04', 'price': 58100, 'mom': -0.2, 'yoy': -1.5},
        {'month': '2025-05', 'price': 58050, 'mom': -0.1, 'yoy': -1.8},
    ]},
}

CALENDAR = {
    'ipo': [
        {'code': '301234', 'name': '示例科技', 'apply_code': '301234', 'apply_date': '2025-06-02',
         'listing_date': '2025-06-12', 'price': 25.8, 'pe': 22.5, 'industry': '电子',
         'apply_upper': 0.75, 'trade_market': '创业板'},
    ],
    'cb': [
        {'code': '127045', 'name': '示例转债', 'event_type': '到期', 'date': '2025-06-15'},
    ],
    'listed': [
        {'code': '688999', 'name': '示例新股', 'date': '2025-05-28', 'price': 18.6, 'trade_market': '科创板'},
    ],
}


def _load_json(name, default):
    path = DATA_DIR / name
    if not path.exists():
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _save_json(name, data):
    path = DATA_DIR / name
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _mock_quote(meta):
    """根据基金元数据生成 mock 行情行。"""
    seed = int(meta['c']) % 1000
    random.seed(seed)
    nav = round(0.5 + seed / 500, 3)
    change_pct = round(random.uniform(-3, 3), 2)
    change = change_pct / 100
    price = round(nav * (1 + change), 3)
    est_nav = round(nav * (1 + change * 0.9), 3)
    premium = round((price - nav) / nav * 100, 2)
    real_premium = round((price - est_nav) / est_nav * 100, 2)
    return {
        'code': meta['c'],
        'name': meta['n'],
        'market': meta['m'],
        'type': meta['t'],
        'price': price,
        'open': round(price * 0.998, 3),
        'high': round(price * 1.005, 3),
        'low': round(price * 0.995, 3),
        'change': change,
        'changePct': change_pct,
        'amount': round(random.uniform(500, 80000), 1),
        'vol': random.randint(1000, 500000),
        'nav': nav,
        'navDate': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        'estNav': est_nav,
        'premium': premium,
        'realPremium': real_premium,
        'sgzt': random.choice(['开放申购', '暂停申购', '限大额']),
        'sgLimit': random.choice(['无限额', '限1000元', '限100元']),
        'status': 'mock',
        'isCustom': meta.get('_custom', False),
    }


def get_fund_pool():
    custom = _load_json('custom-funds.json', [])
    excluded = set(_load_json('excluded-funds.json', []))
    pool = list(BASE_FUNDS)
    for item in custom:
        pool.append({'c': item['c'], 'n': item['n'], 'm': item['m'], 't': item['t'], '_custom': True})
    return [m for m in pool if m['c'] not in excluded]


def get_premium_data():
    funds = [_mock_quote(m) for m in get_fund_pool()]
    return {'data': funds, 'indexes': INDEXES, 'fundNavs': {}, 'fundStatuses': {}}


def get_fund_history(code):
    meta = next((m for m in get_fund_pool() if m['c'] == code), None)
    if not meta:
        return {'ok': False, 'error': '基金不存在'}
    history = []
    nav = 0.8
    for i in range(20, 0, -1):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        random.seed(int(code) + i)
        chg = random.uniform(-0.02, 0.02)
        nav = round(nav * (1 + chg * 0.5), 3)
        price = round(nav * (1 + chg), 3)
        premium = round((price - nav) / nav * 100, 4)
        history.append({
            'date': d, 'price': price, 'nav': nav, 'premium': premium,
            'volume': random.randint(100, 5000), 'jzzzl': round(chg * 100, 2),
            'shares': random.randint(100000, 500000),
        })
    return {
        'ok': True,
        'code': code,
        'name': meta['n'],
        'type': meta['t'],
        'history': history,
        'shares': {'current': 3200000, 'quarterHistory': []},
    }


def get_fund_limit(code):
    return {
        'ok': True, 'code': code, 'status': '限大额',
        'limit': '1000元', 'limitNum': 1000, 'limitUnit': '元',
        'detailHtml': '<p>mock 限额说明</p>',
    }


def get_custom_funds():
    return {'list': _load_json('custom-funds.json', [])}


def add_custom_fund(code, name=None):
    pool = get_fund_pool()
    if any(m['c'] == code for m in pool):
        return {'error': '基金已存在'}
    market = 'sh' if code.startswith(('5', '6')) else 'sz'
    fund_type = 'LOF' if code.startswith(('16', '501', '502')) else 'ETF'
    entry = {'c': code, 'n': name or code, 'm': market, 't': fund_type}
    custom = _load_json('custom-funds.json', [])
    custom.append(entry)
    _save_json('custom-funds.json', custom)
    excluded = _load_json('excluded-funds.json', [])
    if code in excluded:
        excluded.remove(code)
        _save_json('excluded-funds.json', excluded)
    return {'ok': True, 'code': code, 'name': entry['n'], 'market': market}


def remove_fund(code):
    custom = _load_json('custom-funds.json', [])
    custom = [x for x in custom if x['c'] != code]
    _save_json('custom-funds.json', custom)
    excluded = _load_json('excluded-funds.json', [])
    if code not in excluded:
        excluded.append(code)
        _save_json('excluded-funds.json', excluded)
    return {'ok': True}


def get_perks(filter_type='all', search=''):
    perks = _load_json('shareholder-perks.json', [])
    if not perks:
        perks = [
            {'code': '600519', 'name': '贵州茅台', 'perkName': '股东品鉴会',
             'description': 'mock 股东福利', 'startDate': '2025-01-01', 'endDate': '2025-12-31',
             'status': 'ongoing', 'minShares': 100, 'source': 'manual',
             'sourceUrl': '', 'benefit': '品鉴', 'updatedAt': '2025-05-01'},
        ]
    if filter_type != 'all':
        perks = [p for p in perks if p.get('status') == filter_type]
    if search:
        q = search.lower()
        perks = [p for p in perks if q in p.get('code', '').lower() or q in p.get('name', '').lower()]
    return {
        'perks': perks,
        'quotes': {'600519': {'price': 1680.5, 'changePct': 0.5}},
        'total': len(perks), 'cninfoCount': 0, 'manualCount': len(perks),
        'updated': datetime.now().isoformat(),
    }


def update_perks(perks):
    _save_json('shareholder-perks.json', perks)
    return {'ok': True, 'count': len(perks), 'saved': True}


def get_futures_basis():
    return {'ok': True, 'data': FUTURES_BASIS, 'total': len(FUTURES_BASIS),
            'updated': datetime.now().isoformat()}


def get_futures_detail(symbol):
    item = next((x for x in FUTURES_BASIS if x['code'] == symbol.upper()), None)
    if not item:
        return {'ok': False, 'error': '品种不存在'}
    contracts = [
        {'month': '2506', 'price': item['price'], 'prevClose': item['price'] - 5,
         'change': item['changePct'], 'volume': item['volume'], 'openInterest': 120000,
         'date': datetime.now().strftime('%Y-%m-%d'), 'basis': item['spread'],
         'basisPct': item['spreadPct']},
        {'month': '2507', 'price': item['price'] - item['spread'], 'prevClose': item['price'],
         'change': item['changePct'] * 0.8, 'volume': item['volume'] // 2,
         'openInterest': 80000, 'date': datetime.now().strftime('%Y-%m-%d')},
    ]
    return {
        'ok': True, 'code': item['code'], 'name': item['name'],
        'exchange': item['exchange'], 'unit': '点',
        'contracts': contracts,
        'basis': item['spread'], 'basisPct': item['spreadPct'],
        'isContango': not item['isBackwardation'],
    }


def get_house_prices(city='suzhou'):
    info = HOUSE_CITIES.get(city, HOUSE_CITIES['suzhou'])
    return {
        'ok': True, 'city': city, 'cityName': info['cityName'],
        'prices': info['prices'], 'fetchTime': datetime.now().isoformat(), 'note': 'mock',
    }


def get_calendar():
    return CALENDAR


def get_blacklist():
    items = _load_json('blacklist-stocks.json', [])
    return {'ok': True, 'list': items, 'total': len(items)}


def add_blacklist(code, name='', reason=''):
    items = _load_json('blacklist-stocks.json', [])
    if any(x['code'] == code for x in items):
        return {'error': '已在黑名单'}
    stock = {'code': code, 'name': name or code, 'reason': reason}
    items.append(stock)
    _save_json('blacklist-stocks.json', items)
    return {'ok': True, 'stock': stock, 'total': len(items)}


def remove_blacklist(code):
    items = _load_json('blacklist-stocks.json', [])
    items = [x for x in items if x['code'] != code]
    _save_json('blacklist-stocks.json', items)
    return {'ok': True, 'total': len(items)}


def get_stock_risk(code):
    items = _load_json('blacklist-stocks.json', [])
    bl = next((x for x in items if x['code'] == code), None)
    return {
        'ok': True,
        'data': {
            'code': code,
            'name': bl['name'] if bl else f'股票{code}',
            'auditOpinion': '标准无保留',
            'auditOpinionDesc': 'mock',
            'csrcCase': False,
            'csrcCaseDesc': '',
            'stRisk': False,
            'stRiskDesc': '',
            'inBlacklist': bl is not None,
            'blacklistReason': bl.get('reason', '') if bl else '',
        },
    }


def health():
    return {'ok': True, 'quotes': len(get_fund_pool()), 'navs': len(get_fund_pool())}
