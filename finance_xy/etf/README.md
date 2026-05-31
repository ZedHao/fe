# ETF 折溢价实时查询

一个类似 HaoETF 的基金折溢价查询工具。📊

## 环境要求

- **Node.js** 16+（运行 Web 服务）
- **Python** 3.8+（仅生成 LOF 列表时需要；`gen_lof.py` 只用标准库）
- **curl**（`gen_lof.py` 拉取东方财富数据，macOS/Linux 一般已自带）

## 安装

```bash
cd finance_xy/etf

# Node 依赖（iconv-lite，用于 GBK 行情解码）
npm install

# Python 依赖（当前无第三方包，走一遍即可保持流程一致）
pip3 install -r requirements.txt
```

## 运行

```bash
cd finance_xy/etf
npm start
```

或直接：

```bash
node server.js
```

浏览器打开 **http://localhost:3000**

指定端口（可选）：

```bash
PORT=8080 node server.js
```

### macOS 一键启动

双击 `start.command`，或在终端执行：

```bash
cd finance_xy/etf
chmod +x start.command   # 首次需要
./start.command
```

会启动本地服务，并可选开启外网穿透（Serveo）。

### 生成 / 更新 LOF 列表（可选）

从东方财富拉取 LOF 基金代码，输出到 `extra_lof.txt`：

```bash
cd finance_xy/etf
python3 gen_lof.py
```

## 功能

- 59 只主流 ETF/LOF 折溢价实时查询
- 现价、净值、估算净值、溢价率、实时溢价率
- 指数行情栏（上证、沪深300、创业板指等）
- 按代码/名称搜索、按类型筛选、按溢价率筛选
- 按任意列排序（点击表头）
- 深色主题，响应式布局
- 每 15 秒自动刷新数据

## 数据说明

- **净值**：上一交易日基金净值（腾讯行情 API data[48]）
- **估算净值** = 净值 × (1 + 涨跌幅 × 0.9)
- **溢价率** = (现价 − 净值) ÷ 净值 × 100%
- **实时溢价率** = (现价 − 估算净值) ÷ 估算净值 × 100%

## 技术栈

- 后端：Node.js（原生 http 模块 + iconv-lite）
- 前端：纯 HTML/CSS/JS
- 数据源：腾讯行情 API (qt.gtimg.cn)、东方财富基金净值 API
- 辅助脚本：Python 3（`gen_lof.py`）

## 说明

数据仅供参考，不构成投资建议。
