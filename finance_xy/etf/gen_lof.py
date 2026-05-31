#!/usr/bin/env python3
"""Generate LOF list for etf app from eastmoney fund code list.
Filter out: A/C shares (keep primary), 后端, 货币, 定开/定期/封闭, already-existing codes.
"""
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVER_JS = ROOT / 'server.js'
EXTRA_LOF = ROOT / 'extra_lof.txt'

# Get the full list from eastmoney
result = subprocess.run(
    ["curl", "-s", "https://fund.eastmoney.com/js/fundcode_search.js"],
    capture_output=True, text=True, timeout=30
)
data = result.stdout

# Extract JS array
m = re.search(r'var\s+r\s*=\s*\[(.*?)\];', data, re.DOTALL)
if not m:
    print("Failed to parse")
    exit(1)

content = '[' + m.group(1) + ']'
funds = eval(content)

# Filter LOF codes: 16xxxx (深), 501xxx (沪), 502xxx (沪)
raw_lof = []
for f in funds:
    code = str(f[0]).zfill(6)
    name = f[2] if len(f) > 2 else ''
    if code.startswith('16') or code.startswith('501') or code.startswith('502'):
        market = 'sz' if code.startswith('16') else 'sh'
        raw_lof.append((code, name, market))

# Read existing FUND_LIST to find codes already present
existing_codes = set()
try:
    with open(SERVER_JS, 'r') as f:
        content = f.read()
        for m in re.finditer(r"c:'(\d+)'", content):
            existing_codes.add(m.group(1))
except:
    pass

print(f"Total raw LOF candidates: {len(raw_lof)}")
print(f"Existing codes: {len(existing_codes)}")

# Filtering rules:
# 1. Remove backend shares (后端)
# 2. Remove C/E/I/H/O/R shares (prefer A shares)
# 3. Remove 货币 funds
# 4. Remove existing codes
# 5. Group by base name, keep A share

# Key: base name without suffix like (LOF), A, C etc.
def get_base_name(name):
    """Extract base name removing suffix noise"""
    n = name
    # Remove (LOF)
    n = re.sub(r'\(.*?LOF.*?\)', '', n)
    n = re.sub(r'\(QDII.*?\)', '', n)
    # Remove share class
    n = re.sub(r'\s*[A-Z]$', '', n)
    n = re.sub(r'\(后端\)', '', n)
    n = re.sub(r'人民币$', '', n)
    n = n.strip()
    return n

# First pass: deduplicate, prefer A shares
seen_bases = {}
for code, name, market in raw_lof:
    # Skip 后端
    if '(后端)' in name:
        continue
    
    # Skip pure money market funds
    if name.startswith('货币') or name.startswith('货') or '货币A' in name or '货币B' in name:
        if '货币' in name and not any(x in name for x in ['ETF', '指数', '股票', '混合', '债券']):
            continue
    
    # Skip if already in current list
    if code in existing_codes:
        continue
    
    base = get_base_name(name)
    
    # Determine priority: A > (none) > C > others
    priority = 5
    if 'A' in name and '(LOF)A' in name:
        priority = 1
    elif name.endswith(' A') or name.endswith('A'):
        priority = 1
    elif not re.search(r'[BCDEHIJKL]', name):
        priority = 2
    elif 'C' in name:
        priority = 3
    else:
        priority = 4
    
    if base not in seen_bases or priority < seen_bases[base][2]:
        seen_bases[base] = (code, name, priority, market)

# Also keep all existing LOFs (they're already in the list)
# We need to know which are currently LOF vs ETF vs REIT
existing_lof = set()
with open(SERVER_JS, 'r') as f:
    for line in f:
        m = re.search(r"c:'(\d+)'.*t:'LOF'", line)
        if m:
            existing_lof.add(m.group(1))

# Filter by removing: base name with "定开" or "定期" or "封闭" or "持有" in name (closed-end)
filtered = []
for base, (code, name, pri, market) in seen_bases.items():
    if any(kw in name for kw in ['定开', '定期开放', '封闭', '两年', '三年', '18个月', '12个月']):
        continue
    # Skip if base name is too generic
    base_short = base.replace('指数', '').replace('ETF', '').replace('联接', '').strip()
    if len(base_short) <= 1:
        continue
    filtered.append((code, name, market))

# Sort by code
filtered.sort(key=lambda x: x[0])

print(f"\nNew LOF funds to add: {len(filtered)}")

# Generate JS entries
js_lines = []
for code, name, market in filtered:
    short_name = name
    # Shorten for display
    short_name = short_name.replace('(LOF)', '')
    short_name = short_name.replace('指数型', '')
    short_name = short_name.replace('(QDII-FOF-LOF)', '')
    short_name = short_name.strip()
    if len(short_name) > 20:
        # Shorten further
        short_name = short_name.replace('证券投资', '').replace('灵活配置', '').replace('指数增强', '增强')
        short_name = short_name.replace('行业精选', '')
    js_lines.append(f"  {{ c:'{code}', n:'{short_name}', m:'{market}', t:'LOF' }},")

with open(EXTRA_LOF, 'w') as f:
    for line in js_lines:
        f.write(line + '\n')

print(f"Written {len(js_lines)} entries to extra_lof.txt")
print("\nFirst 10:")
for l in js_lines[:10]:
    print(l)

# Also show new counts vs old
new_codes = {x[0] for x in filtered}
print(f"\nNew codes: {len(new_codes)}")
print(f"Total would be: {len(existing_codes) + len(new_codes)}")
