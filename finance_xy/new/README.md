# https://github.com/simonlin1212/a-stock-data
# https://github.com/skyformat99/a-stock-data/blob/main/SKILL.md
# 
# 猪猪基金 · 前后端分离版

原 `finance_xy/etf` 单体 Node 应用的重写版本，参照 `finance_fe` + `finance_server` 的分层结构：

```
new/
├── client/          # Vue 3 前端（类似 finance_fe）
├── server/          # Django 后端（类似 finance_server）
│   ├── service/     # HTTP 视图层
│   ├── dao/         # 数据层（当前为 mock，可替换真实抓取）
│   └── data/        # JSON 持久化（黑名单、自定义基金等）
└── README.md
```

## 环境要求

- Python 3.9+
- Node.js 18+

## 一键启动

```bash
cd finance_xy/new
chmod +x start.sh   # 首次需要
./start.sh
```

脚本会依次：

1. 检查 Python / Node 依赖，缺失则自动安装
2. 检测端口 **9001**（后端）、**5173**（前端）是否占用，占用则 `kill`
3. 启动 Django + Vite，日志写入 `.pids/backend.log`、`.pids/frontend.log`

自定义端口：

```bash
BACKEND_PORT=9001 FRONTEND_PORT=5173 ./start.sh
```

## 手动启动

### 后端

```bash
cd finance_xy/new/server
pip3 install -r requirements.txt
python3 manage.py runserver 9001
```

API 基址：`http://localhost:9001`

### 前端

```bash
cd finance_xy/new/client
npm install
npm run dev
```

浏览器打开 **http://localhost:5173**

开发模式下 Vite 会将 `/api/*` 代理到 `9001`。

也可指定 API 地址：

```bash
VITE_API_BASE=http://localhost:9001 npm run dev
```

## 页面与 API 对照

| 前端路由 | 原 etf 页面 | 主要 API |
|---------|-------------|----------|
| `/` | index.html | `GET /api/premium` |
| `/blacklist` | blacklist.html | `GET/POST /api/blacklist*` |
| `/calendar` | calendar.html | `GET /api/calendar` |
| `/futures` | futures.html | `GET /api/futures-basis` |
| `/house` | house.html | `GET /api/house-prices` |
| `/perks` | perks.html | `GET /api/perks` |

完整端点列表见 `server/new_server/urls.py`。

## Mock 说明

当前 `dao/mock_data.py` 提供：

- 基金折溢价列表（内置 10 只 + custom-funds.json）
- 指数栏、历史净值、期货基差、房价、日历、股东福利
- 黑名单读写（持久化到 `server/data/`）

后续可在 `dao/` 新增真实数据源模块（腾讯行情、东方财富等），在 `service/etf.py` 中切换调用。

## 响应格式

与 `finance_server` 一致，成功响应：

```json
{ "code": 200, "message": "请求成功", "data": { ... } }
```

部分端点（如 `/api/blacklist`）为兼容原 etf 前端，直接返回业务 JSON（含 `ok` 字段）。
