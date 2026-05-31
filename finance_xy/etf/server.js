#!/usr/bin/env node

/**

 * ETF折溢价查询 - 后端服务器 (v2)

 * 数据源：

 *   - 腾讯行情API (qt.gtimg.cn) → 实时价格、涨跌幅

 *   - 东方财富基金净值API (fundgz.1234567.com.cn) → 准确的单位净值

 *

 * 启动: node server.js

 * 访问: http://localhost:3000

 */



const http = require('http');

const https = require('https');

const fs = require('fs');

const path = require('path');



const PORT = process.env.PORT || 3000;



// =============================================================

// ETF/LOF 数据表

// =============================================================

const FUND_LIST = [

  // 沪市ETF

  { c:'510010', n:'180治理ETF交银', m:'sh', t:'ETF' },

  { c:'510050', n:'上证50ETF', m:'sh', t:'ETF' },

  { c:'510100', n:'上证50ETF易方达', m:'sh', t:'ETF' },

  { c:'510150', n:'消费ETF招商', m:'sh', t:'ETF' },

  { c:'510180', n:'上证180ETF华安', m:'sh', t:'ETF' },

  { c:'510200', n:'上证券商ETF汇安', m:'sh', t:'ETF' },

  { c:'510210', n:'上证指数ETF富国', m:'sh', t:'ETF' },

  { c:'510230', n:'金融ETF国泰', m:'sh', t:'ETF' },

  { c:'510300', n:'沪深300ETF', m:'sh', t:'ETF' },

  { c:'510310', n:'沪深300ETF易方达', m:'sh', t:'ETF' },

  { c:'510330', n:'沪深300ETF华夏', m:'sh', t:'ETF' },

  { c:'510350', n:'沪深300ETF工银', m:'sh', t:'ETF' },

  { c:'510360', n:'沪深300ETF广发', m:'sh', t:'ETF' },

  { c:'510410', n:'资源ETF博时', m:'sh', t:'ETF' },

  { c:'510500', n:'中证500ETF', m:'sh', t:'ETF' },

  { c:'510510', n:'中证500ETF广发', m:'sh', t:'ETF' },

  { c:'510580', n:'中证500ETF易方达', m:'sh', t:'ETF' },

  { c:'510630', n:'消费ETF华夏', m:'sh', t:'ETF' },

  { c:'510660', n:'医药ETF华夏', m:'sh', t:'ETF' },

  { c:'510720', n:'红利国企ETF', m:'sh', t:'ETF' },

  { c:'510760', n:'上证指数ETF国泰', m:'sh', t:'ETF' },

  { c:'510880', n:'红利ETF', m:'sh', t:'ETF' },

  { c:'510900', n:'恒生国企ETF', m:'sh', t:'ETF' },

  // 行业ETF

  { c:'512000', n:'券商ETF', m:'sh', t:'ETF' },

  { c:'512010', n:'医药ETF易方达', m:'sh', t:'ETF' },

  { c:'512070', n:'证券保险ETF', m:'sh', t:'ETF' },

  { c:'512100', n:'中证1000ETF南方', m:'sh', t:'ETF' },

  { c:'512170', n:'医疗ETF', m:'sh', t:'ETF' },

  { c:'512200', n:'房地产ETF', m:'sh', t:'ETF' },

  { c:'512400', n:'有色金属ETF', m:'sh', t:'ETF' },

  { c:'512480', n:'半导体ETF', m:'sh', t:'ETF' },

  { c:'512500', n:'中证500ETF华夏', m:'sh', t:'ETF' },

  { c:'512660', n:'军工ETF', m:'sh', t:'ETF' },

  { c:'512670', n:'国防ETF', m:'sh', t:'ETF' },

  { c:'512680', n:'军工ETF龙头', m:'sh', t:'ETF' },

  { c:'512690', n:'酒ETF', m:'sh', t:'ETF' },

  { c:'512720', n:'计算机ETF', m:'sh', t:'ETF' },

  { c:'512760', n:'芯片ETF', m:'sh', t:'ETF' },

  { c:'512880', n:'证券ETF', m:'sh', t:'ETF' },

  { c:'512890', n:'红利低波ETF', m:'sh', t:'ETF' },

  { c:'512960', n:'央企结构调整ETF', m:'sh', t:'ETF' },

  // 主题ETF

  { c:'513050', n:'中概互联ETF', m:'sh', t:'ETF' },

  { c:'513100', n:'纳指ETF', m:'sh', t:'ETF' },

  { c:'513130', n:'恒生科技ETF', m:'sh', t:'ETF' },

  { c:'513180', n:'恒生科技ETF', m:'sh', t:'ETF' },

  { c:'513300', n:'纳斯达克ETF', m:'sh', t:'ETF' },

  { c:'513500', n:'标普500ETF', m:'sh', t:'ETF' },

  { c:'513520', n:'日经ETF', m:'sh', t:'ETF' },

  { c:'513800', n:'东南亚科技ETF', m:'sh', t:'ETF' },

  { c:'513880', n:'日经225ETF', m:'sh', t:'ETF' },

  { c:'515050', n:'5GETF', m:'sh', t:'ETF' },

  { c:'515070', n:'AI智能ETF', m:'sh', t:'ETF' },

  { c:'515220', n:'煤炭ETF', m:'sh', t:'ETF' },

  { c:'515790', n:'光伏ETF', m:'sh', t:'ETF' },

  { c:'515880', n:'通信ETF', m:'sh', t:'ETF' },

  { c:'516160', n:'新能源ETF', m:'sh', t:'ETF' },

  { c:'516970', n:'基建ETF', m:'sh', t:'ETF' },

  { c:'517010', n:'港股通科技ETF', m:'sh', t:'ETF' },

  { c:'517050', n:'港股通互联网ETF', m:'sh', t:'ETF' },

  { c:'517090', n:'港股央企红利ETF', m:'sh', t:'ETF' },

  { c:'518880', n:'黄金ETF', m:'sh', t:'ETF' },

  // 宽基ETF深市

  { c:'159845', n:'中证1000ETF', m:'sz', t:'ETF' },

  { c:'159915', n:'创业板ETF', m:'sz', t:'ETF' },

  { c:'159919', n:'沪深300ETF嘉实', m:'sz', t:'ETF' },

  { c:'159922', n:'中证500ETF嘉实', m:'sz', t:'ETF' },

  { c:'159941', n:'纳指ETF', m:'sz', t:'ETF' },

  { c:'159949', n:'创业板50ETF', m:'sz', t:'ETF' },

  { c:'159967', n:'创成长ETF', m:'sz', t:'ETF' },

  { c:'159985', n:'豆粕ETF', m:'sz', t:'ETF' },

  // 深市LOF

  { c:'161005', n:'富国天惠', m:'sz', t:'LOF' },

  { c:'161129', n:'原油基金', m:'sz', t:'LOF' },

  { c:'161130', n:'纳指LOF', m:'sz', t:'LOF' },

  { c:'161131', n:'同存LOF', m:'sz', t:'LOF' },

  { c:'161132', n:'港股高股息LOF', m:'sz', t:'LOF' },

  { c:'161716', n:'LOF', m:'sz', t:'LOF' },

  { c:'161725', n:'白酒基金', m:'sz', t:'LOF' },

  { c:'161726', n:'生物医药', m:'sz', t:'LOF' },

  { c:'161810', n:'银华内需', m:'sz', t:'LOF' },

  { c:'161812', n:'深证100', m:'sz', t:'LOF' },

  { c:'161815', n:'抗通胀', m:'sz', t:'LOF' },

  { c:'161831', n:'港股LOF', m:'sz', t:'LOF' },

  { c:'161834', n:'银行LOF', m:'sz', t:'LOF' },

  { c:'161903', n:'万家优选', m:'sz', t:'LOF' },

  { c:'162411', n:'华宝油气', m:'sz', t:'LOF' },

  { c:'162415', n:'美国消费LOF', m:'sz', t:'LOF' },

  { c:'162605', n:'景顺鼎益', m:'sz', t:'LOF' },

  { c:'162607', n:'景顺资源', m:'sz', t:'LOF' },

  { c:'162703', n:'广发小盘', m:'sz', t:'LOF' },

  { c:'163001', n:'长信医疗', m:'sz', t:'LOF' },

  { c:'163402', n:'兴全趋势', m:'sz', t:'LOF' },

  { c:'163406', n:'兴全合润', m:'sz', t:'LOF' },

  { c:'163407', n:'兴全沪深300', m:'sz', t:'LOF' },

  { c:'163415', n:'兴全商业模式', m:'sz', t:'LOF' },

  { c:'165309', n:'建信沪深300', m:'sz', t:'LOF' },

  { c:'165520', n:'信诚有色', m:'sz', t:'LOF' },

  { c:'166001', n:'中欧趋势', m:'sz', t:'LOF' },

  { c:'166002', n:'中欧蓝筹', m:'sz', t:'LOF' },

  { c:'166009', n:'中欧动力', m:'sz', t:'LOF' },

  { c:'166025', n:'中欧远见', m:'sz', t:'LOF' },

  // 沪市LOF

  { c:'501018', n:'南方原油LOF', m:'sh', t:'LOF' },

  { c:'501025', n:'香港银行LOF', m:'sh', t:'LOF' },

  { c:'501029', n:'红利基金LOF', m:'sh', t:'LOF' },

  { c:'501050', n:'50AHLOF', m:'sh', t:'LOF' },

  { c:'501053', n:'东方红目标优选', m:'sh', t:'LOF' },

  { c:'501054', n:'东方红睿玺', m:'sh', t:'LOF' },

  { c:'501062', n:'南方瑞合LOF', m:'sh', t:'LOF' },

  { c:'501077', n:'富国创新企业LOF', m:'sh', t:'LOF' },

  { c:'501081', n:'科创中欧LOF', m:'sh', t:'LOF' },

  { c:'501083', n:'科创银华LOF', m:'sh', t:'LOF' },

  { c:'501085', n:'财通科创LOF', m:'sh', t:'LOF' },

  { c:'501086', n:'ESG基金LOF', m:'sh', t:'LOF' },

  { c:'501087', n:'交银瑞丰LOF', m:'sh', t:'LOF' },

  { c:'501088', n:'嘉实瑞虹', m:'sh', t:'LOF' },

  { c:'501089', n:'消费红利增强LOF', m:'sh', t:'LOF' },

  { c:'501090', n:'消费龙头LOF', m:'sh', t:'LOF' },

  { c:'501091', n:'嘉实欣荣LOF', m:'sh', t:'LOF' },

  { c:'501092', n:'交银瑞思LOF', m:'sh', t:'LOF' },

  { c:'501093', n:'华夏翔阳LOF', m:'sh', t:'LOF' },

  { c:'501095', n:'中银证券科技创新LOF', m:'sh', t:'LOF' },

  { c:'501096', n:'国联安科创LOF', m:'sh', t:'LOF' },

  { c:'501097', n:'科创国寿LOF', m:'sh', t:'LOF' },

  { c:'501098', n:'科创建信LOF', m:'sh', t:'LOF' },

  { c:'501099', n:'平安新兴产业LOF', m:'sh', t:'LOF' },

  { c:'501186', n:'华夏兴融LOF', m:'sh', t:'LOF' },

  { c:'501188', n:'添富核心精选LOF', m:'sh', t:'LOF' },

  { c:'501189', n:'嘉实产业优选LOF', m:'sh', t:'LOF' },

  { c:'501200', n:'科创加银LOF', m:'sh', t:'LOF' },

  { c:'501201', n:'科创红土LOF', m:'sh', t:'LOF' },

  { c:'501202', n:'华泰创新先锋LOF', m:'sh', t:'LOF' },

  { c:'501203', n:'易基创新未来LOF', m:'sh', t:'LOF' },

  { c:'501205', n:'鹏华创新未来LOF', m:'sh', t:'LOF' },

  { c:'501206', n:'添富创新未来LOF', m:'sh', t:'LOF' },

  { c:'501207', n:'华夏创新未来LOF', m:'sh', t:'LOF' },

  { c:'501208', n:'中欧创新未来LOF', m:'sh', t:'LOF' },

  { c:'501209', n:'富久食品饮料LOF', m:'sh', t:'LOF' },

  { c:'501210', n:'交银智选星光FOF', m:'sh', t:'LOF' },

  { c:'501211', n:'民生加银优享FOF', m:'sh', t:'LOF' },

  { c:'501212', n:'广发优选配置FOF', m:'sh', t:'LOF' },

  { c:'501213', n:'中欧汇选FOF', m:'sh', t:'LOF' },

  { c:'501215', n:'XD积极配置FOF', m:'sh', t:'LOF' },

  { c:'501216', n:'富国行业精选FOF', m:'sh', t:'LOF' },

  { c:'501217', n:'行业配置FOF', m:'sh', t:'LOF' },

  { c:'501218', n:'工银睿智进取FOF', m:'sh', t:'LOF' },

  { c:'501219', n:'智胜先锋LOF', m:'sh', t:'LOF' },

  { c:'501225', n:'全球芯片LOF', m:'sh', t:'LOF' },

  { c:'501226', n:'新能源车全球LOF', m:'sh', t:'LOF' },

  // REITs

  { c:'508056', n:'普洛斯REIT', m:'sh', t:'REIT' },

  { c:'508060', n:'南方万国数据中心REIT', m:'sh', t:'REIT' },

  { c:'508068', n:'华夏北京保障房REIT', m:'sh', t:'REIT' },

  { c:'508077', n:'华夏基金华润有巢REIT', m:'sh', t:'REIT' },

  { c:'508088', n:'国泰海通东久新经济REIT', m:'sh', t:'REIT' },

  { c:'508096', n:'中航京能国际能源REIT', m:'sh', t:'REIT' },

  { c:'508098', n:'嘉实京东仓储基础设施REIT', m:'sh', t:'REIT' },

  { c:'508099', n:'建信中关村REIT', m:'sh', t:'REIT' },

  // REITs深市

  { c:'180101', n:'蛇口REIT', m:'sz', t:'REIT' },

  { c:'180102', n:'张江REIT', m:'sz', t:'REIT' },

  { c:'180103', n:'苏园REIT', m:'sz', t:'REIT' },

  { c:'180201', n:'广州广河REIT', m:'sz', t:'REIT' },

  { c:'180202', n:'越秀REIT', m:'sz', t:'REIT' },

  { c:'180203', n:'招商高速公路REIT', m:'sz', t:'REIT' },

  { c:'180301', n:'盐港REIT', m:'sz', t:'REIT' },

  { c:'180401', n:'首钢绿能REIT', m:'sz', t:'REIT' },

  { c:'180501', n:'红土创新深圳安居REIT', m:'sz', t:'REIT' },

  { c:'180601', n:'华夏华润消费REIT', m:'sz', t:'REIT' },

  { c:'180602', n:'中金印力消费REIT', m:'sz', t:'REIT' },

  { c:'180603', n:'华夏大悦城消费REIT', m:'sz', t:'REIT' },

  // 补充常见

  { c:'159929', n:'医药ETF', m:'sz', t:'ETF' },

  { c:'159930', n:'能源ETF', m:'sz', t:'ETF' },

  { c:'159932', n:'消费ETF', m:'sz', t:'ETF' },

  { c:'159933', n:'金融ETF', m:'sz', t:'ETF' },

  { c:'159934', n:'黄金ETF', m:'sz', t:'ETF' },

  { c:'159937', n:'黄金ETF', m:'sz', t:'ETF' },

  { c:'159938', n:'医药卫生ETF', m:'sz', t:'ETF' },

  { c:'159939', n:'信息技术ETF', m:'sz', t:'ETF' },

  { c:'159940', n:'综合行业ETF', m:'sz', t:'ETF' },

  { c:'159948', n:'创业板ETF南方', m:'sz', t:'ETF' },

  { c:'159952', n:'创业大盘ETF', m:'sz', t:'ETF' },

  { c:'159959', n:'央企ETF', m:'sz', t:'ETF' },

  { c:'159965', n:'央视50ETF', m:'sz', t:'ETF' },

  { c:'159968', n:'沪深300ETF南方', m:'sz', t:'ETF' },

  { c:'159969', n:'深证100ETF', m:'sz', t:'ETF' },

  { c:'159981', n:'能源化工ETF', m:'sz', t:'ETF' },

  { c:'159992', n:'证券ETF', m:'sz', t:'ETF' },

  { c:'159993', n:'龙头券商ETF', m:'sz', t:'ETF' },

  { c:'159995', n:'芯片ETF', m:'sz', t:'ETF' },

  { c:'159996', n:'家电ETF', m:'sz', t:'ETF' },

  { c:'159997', n:'电子ETF', m:'sz', t:'ETF' },

  { c:'159998', n:'计算机ETF', m:'sz', t:'ETF' },

  { c:'159999', n:'有色金属ETF', m:'sz', t:'ETF' },



{ c:'160105', n:'南方积极配置混合', m:'sz', t:'LOF' },

{ c:'160106', n:'南方高增长混合', m:'sz', t:'LOF' },

{ c:'160119', n:'500ETF联接LOF', m:'sz', t:'LOF' },

{ c:'160125', n:'南方香港优选股票', m:'sz', t:'LOF' },

{ c:'160127', n:'南方新兴消费增长股票A', m:'sz', t:'LOF' },

{ c:'160133', n:'南方天元新产业股票', m:'sz', t:'LOF' },

{ c:'160135', n:'南方中证高铁产业指数', m:'sz', t:'LOF' },

{ c:'160140', n:'南方道琼斯美国精选A', m:'sz', t:'LOF' },

{ c:'160142', n:'南方优势产业', m:'sz', t:'LOF' },

{ c:'160211', n:'国泰中小盘成长混合', m:'sz', t:'LOF' },

{ c:'160212', n:'国泰估值优势混合A', m:'sz', t:'LOF' },

{ c:'160213', n:'国泰纳斯达克100指数', m:'sz', t:'LOF' },

{ c:'160215', n:'国泰价值经典混合', m:'sz', t:'LOF' },

{ c:'160216', n:'国泰大宗商品(QDII-LOF)A', m:'sz', t:'LOF' },

{ c:'160217', n:'国泰信用互利债券A', m:'sz', t:'LOF' },

{ c:'160218', n:'国泰国证房地产行业指数A', m:'sz', t:'LOF' },

{ c:'160219', n:'国泰国证医药卫生行业指数A', m:'sz', t:'LOF' },

{ c:'160220', n:'国泰民益混合A', m:'sz', t:'LOF' },

{ c:'160221', n:'国泰国证有色金属行业指数A', m:'sz', t:'LOF' },

{ c:'160222', n:'国泰国证食品饮料行业A', m:'sz', t:'LOF' },

{ c:'160223', n:'国泰创业板指数A', m:'sz', t:'LOF' },

{ c:'160224', n:'国泰中证计算机主题ETF联接A', m:'sz', t:'LOF' },

{ c:'160225', n:'国泰国证新能源汽车指数A', m:'sz', t:'LOF' },

{ c:'160311', n:'华夏蓝筹混合A', m:'sz', t:'LOF' },

{ c:'160314', n:'华夏行业混合', m:'sz', t:'LOF' },

{ c:'160322', n:'华夏港股通精选股票发起式A', m:'sz', t:'LOF' },

{ c:'160323', n:'华夏磐泰混合A', m:'sz', t:'LOF' },

{ c:'160324', n:'华夏磐晟混合', m:'sz', t:'LOF' },

{ c:'160326', n:'华夏优选配置股票(FOF-LOF)A', m:'sz', t:'LOF' },

{ c:'160416', n:'华安标普全球石油指数A', m:'sz', t:'LOF' },

{ c:'160421', n:'华安智增精选混合', m:'sz', t:'LOF' },

{ c:'160422', n:'华安创业板50ETF联接A', m:'sz', t:'LOF' },

{ c:'160505', n:'博时主题行业混合', m:'sz', t:'LOF' },

{ c:'160512', n:'博时卓越品牌混合A', m:'sz', t:'LOF' },

{ c:'160513', n:'博时稳健回报债券A', m:'sz', t:'LOF' },

{ c:'160518', n:'博时睿远', m:'sz', t:'LOF' },

{ c:'160526', n:'博时优势企业灵活配置混合A', m:'sz', t:'LOF' },

{ c:'160527', n:'博时研究优选混合A', m:'sz', t:'LOF' },

{ c:'160602', n:'鹏华普天债券A', m:'sz', t:'LOF' },

{ c:'160607', n:'鹏华价值优势混合', m:'sz', t:'LOF' },

{ c:'160610', n:'鹏华动力增长混合', m:'sz', t:'LOF' },

{ c:'160611', n:'鹏华优质治理混合A', m:'sz', t:'LOF' },

{ c:'160612', n:'鹏华丰收债券B', m:'sz', t:'LOF' },

{ c:'160613', n:'鹏华盛世创新混合A', m:'sz', t:'LOF' },

{ c:'160615', n:'鹏华沪深300ETF联接A', m:'sz', t:'LOF' },

{ c:'160616', n:'鹏华中证500指数A', m:'sz', t:'LOF' },

{ c:'160617', n:'鹏华丰润债券', m:'sz', t:'LOF' },

{ c:'160618', n:'鹏华丰泽债券C', m:'sz', t:'LOF' },

{ c:'160620', n:'鹏华中证A股资源产业指数A', m:'sz', t:'LOF' },

{ c:'160621', n:'鹏华丰和债券A', m:'sz', t:'LOF' },

{ c:'160622', n:'鹏华丰利债券A', m:'sz', t:'LOF' },

{ c:'160625', n:'鹏华中证800证券保险指数A', m:'sz', t:'LOF' },

{ c:'160626', n:'鹏华中证信息技术指数A', m:'sz', t:'LOF' },

{ c:'160628', n:'鹏华中证800地产指数A', m:'sz', t:'LOF' },

{ c:'160629', n:'鹏华中证传媒指数A', m:'sz', t:'LOF' },

{ c:'160630', n:'鹏华中证国防指数A', m:'sz', t:'LOF' },

{ c:'160631', n:'鹏华中证银行指数A', m:'sz', t:'LOF' },

{ c:'160632', n:'鹏华酒A', m:'sz', t:'LOF' },

{ c:'160633', n:'鹏华中证全指证券公司指数A', m:'sz', t:'LOF' },

{ c:'160635', n:'鹏华中证医药指数A', m:'sz', t:'LOF' },

{ c:'160637', n:'鹏华创业板指数A', m:'sz', t:'LOF' },

{ c:'160638', n:'鹏华中证一带一路主题指数A', m:'sz', t:'LOF' },

{ c:'160639', n:'鹏华中证高铁产业指数A', m:'sz', t:'LOF' },

{ c:'160641', n:'鹏华丰锐债券LOF', m:'sz', t:'LOF' },

{ c:'160642', n:'鹏华增瑞混合A', m:'sz', t:'LOF' },

{ c:'160643', n:'鹏华空天军工指数A', m:'sz', t:'LOF' },

{ c:'160644', n:'鹏华港美互联股票人民币', m:'sz', t:'LOF' },

{ c:'160706', n:'嘉实沪深300ETF联接A', m:'sz', t:'LOF' },

{ c:'160716', n:'嘉实基本面50指数A', m:'sz', t:'LOF' },

{ c:'160717', n:'嘉实H股指数(QDII-LOF)', m:'sz', t:'LOF' },

{ c:'160719', n:'嘉实黄金', m:'sz', t:'LOF' },

{ c:'160722', n:'嘉实惠泽混合', m:'sz', t:'LOF' },

{ c:'160723', n:'嘉实原油(QDII-LOF)', m:'sz', t:'LOF' },

{ c:'160726', n:'嘉实瑞享定期混合', m:'sz', t:'LOF' },

{ c:'160805', n:'长盛同智优势混合', m:'sz', t:'LOF' },

{ c:'160806', n:'长盛同庆中证800', m:'sz', t:'LOF' },

{ c:'160807', n:'长盛沪深300指数A', m:'sz', t:'LOF' },

{ c:'160812', n:'长盛同益成长回报', m:'sz', t:'LOF' },

{ c:'160813', n:'长盛同盛成长优选', m:'sz', t:'LOF' },

{ c:'160910', n:'大成创新成长混合A', m:'sz', t:'LOF' },

{ c:'160916', n:'大成优选混合A', m:'sz', t:'LOF' },

{ c:'160918', n:'大成中小盘混合A', m:'sz', t:'LOF' },

{ c:'160919', n:'大成产业升级股票A', m:'sz', t:'LOF' },

{ c:'160921', n:'大成多策略混合A', m:'sz', t:'LOF' },

{ c:'160924', n:'大成恒生指数(QDII-LOF)A', m:'sz', t:'LOF' },

{ c:'160925', n:'大成中华沪深港300指数A', m:'sz', t:'LOF' },

{ c:'161010', n:'富国天丰强化债券A', m:'sz', t:'LOF' },

{ c:'161015', n:'富国天盈债券C', m:'sz', t:'LOF' },

{ c:'161017', n:'富国中证500指数增强A', m:'sz', t:'LOF' },

{ c:'161019', n:'富国新天锋债券A', m:'sz', t:'LOF' },

{ c:'161024', n:'富国中证军工指数A', m:'sz', t:'LOF' },

{ c:'161025', n:'富国中证移动互联网指数A', m:'sz', t:'LOF' },

{ c:'161026', n:'富国中证国有企业改革指数A', m:'sz', t:'LOF' },

{ c:'161027', n:'富国中证全指证券公司指数A', m:'sz', t:'LOF' },

{ c:'161028', n:'富国中证新能源汽车指数A', m:'sz', t:'LOF' },

{ c:'161029', n:'富国中证银行指数A', m:'sz', t:'LOF' },

{ c:'161030', n:'富国中证体育产业指数A', m:'sz', t:'LOF' },

{ c:'161031', n:'富国中证工业4.0指数A', m:'sz', t:'LOF' },

{ c:'161032', n:'富国中证煤炭指数A', m:'sz', t:'LOF' },

{ c:'161033', n:'富国中证智能汽车A', m:'sz', t:'LOF' },

{ c:'161035', n:'富国中证医药主题指数增强A', m:'sz', t:'LOF' },

{ c:'161036', n:'富国中证娱乐主题指数增强A', m:'sz', t:'LOF' },

{ c:'161037', n:'富国中证高端制造指数增强型A', m:'sz', t:'LOF' },

{ c:'161038', n:'富国新兴成长量化精选混合A', m:'sz', t:'LOF' },

{ c:'161039', n:'富国中证1000指数增强A', m:'sz', t:'LOF' },

{ c:'161115', n:'易方达岁丰添利债券A', m:'sz', t:'LOF' },

{ c:'161116', n:'易方达黄金主题人民币A', m:'sz', t:'LOF' },

{ c:'161118', n:'易方达中小企业100A', m:'sz', t:'LOF' },

{ c:'161119', n:'易方达中债新综指发起式A', m:'sz', t:'LOF' },

{ c:'161121', n:'易方达中证银行ETF联接A', m:'sz', t:'LOF' },

{ c:'161122', n:'易方达中证万得生物科技指数A', m:'sz', t:'LOF' },

{ c:'161123', n:'易方达中证万得并购重组', m:'sz', t:'LOF' },

{ c:'161124', n:'易方达香港小型股指数A', m:'sz', t:'LOF' },

{ c:'161125', n:'易方达标普500指数人民币A', m:'sz', t:'LOF' },

{ c:'161126', n:'易方达标普医疗保健人民币A', m:'sz', t:'LOF' },

{ c:'161127', n:'易方达标普生物科技人民币A', m:'sz', t:'LOF' },

{ c:'161128', n:'易方达标普信息科技指数(QDII-LOF)A(人民币)', m:'sz', t:'LOF' },

{ c:'161133', n:'易方达优势回报混合(FOF-LOF)A', m:'sz', t:'LOF' },

{ c:'161211', n:'国投沪深300金融地产联接', m:'sz', t:'LOF' },

{ c:'161216', n:'国投瑞银双债债券A', m:'sz', t:'LOF' },

{ c:'161217', n:'国投瑞银中证资源指数A', m:'sz', t:'LOF' },

{ c:'161219', n:'国投瑞银新兴产业混合A', m:'sz', t:'LOF' },

{ c:'161222', n:'国投瑞银瑞利混合A', m:'sz', t:'LOF' },

{ c:'161224', n:'国投瑞银新丝路混合', m:'sz', t:'LOF' },

{ c:'161225', n:'国投瑞银瑞盈混合A', m:'sz', t:'LOF' },

{ c:'161226', n:'国投瑞银白银期货A', m:'sz', t:'LOF' },

{ c:'161227', n:'国投瑞银深证100指数', m:'sz', t:'LOF' },

{ c:'161229', n:'国投瑞银中国价值发现股票', m:'sz', t:'LOF' },

{ c:'161232', n:'国投瑞银瑞盛混合A', m:'sz', t:'LOF' },

{ c:'161233', n:'国投瑞银瑞泰多策略混合A', m:'sz', t:'LOF' },

{ c:'161505', n:'银河通利债券A', m:'sz', t:'LOF' },

{ c:'161601', n:'融通新蓝筹混合', m:'sz', t:'LOF' },

{ c:'161603', n:'融通债券A/B', m:'sz', t:'LOF' },

{ c:'161604', n:'融通深证100指数A', m:'sz', t:'LOF' },

{ c:'161605', n:'融通蓝筹成长混合A/B', m:'sz', t:'LOF' },

{ c:'161606', n:'融通行业景气混合A', m:'sz', t:'LOF' },

{ c:'161607', n:'融通巨潮100指数A', m:'sz', t:'LOF' },

{ c:'161609', n:'融通动力先锋混合A/B', m:'sz', t:'LOF' },

{ c:'161610', n:'融通领先成长混合A', m:'sz', t:'LOF' },

{ c:'161611', n:'融通内需驱动混合A', m:'sz', t:'LOF' },

{ c:'161612', n:'融通深证成份指数A', m:'sz', t:'LOF' },

{ c:'161613', n:'融通创业板指数A', m:'sz', t:'LOF' },

{ c:'161614', n:'融通四季添利债券A', m:'sz', t:'LOF' },

{ c:'161616', n:'融通医疗保健行业混合A/B', m:'sz', t:'LOF' },

{ c:'161620', n:'融通核心价值混合A', m:'sz', t:'LOF' },

{ c:'161624', n:'融通可转债债券A', m:'sz', t:'LOF' },

{ c:'161626', n:'融通通福债券A', m:'sz', t:'LOF' },

{ c:'161631', n:'融通人工智能指数A', m:'sz', t:'LOF' },

{ c:'161693', n:'融通债券C', m:'sz', t:'LOF' },

{ c:'161706', n:'招商优质成长混合', m:'sz', t:'LOF' },

{ c:'161713', n:'招商信用添利债券A', m:'sz', t:'LOF' },

{ c:'161715', n:'招商大宗商品', m:'sz', t:'LOF' },

{ c:'161720', n:'招商中证全指证券公司指数A', m:'sz', t:'LOF' },

{ c:'161722', n:'招商丰泰混合', m:'sz', t:'LOF' },

{ c:'161724', n:'招商中证煤炭等权指数A', m:'sz', t:'LOF' },

{ c:'161727', n:'招商增荣混合', m:'sz', t:'LOF' },

{ c:'161728', n:'招商瑞智优选混合', m:'sz', t:'LOF' },

{ c:'161729', n:'招商瑞利灵活配置混合A', m:'sz', t:'LOF' },

{ c:'161811', n:'银华沪深300指数A', m:'sz', t:'LOF' },

{ c:'161816', n:'银华中证等权重90指数', m:'sz', t:'LOF' },

{ c:'161820', n:'银华纯债信用债券A', m:'sz', t:'LOF' },

{ c:'161902', n:'万家增强收益债券C', m:'sz', t:'LOF' },

{ c:'161908', n:'万家添利债券C', m:'sz', t:'LOF' },

{ c:'161910', n:'万家新机遇价值驱动A', m:'sz', t:'LOF' },

{ c:'162006', n:'长城久富混合A', m:'sz', t:'LOF' },

{ c:'162102', n:'金鹰中小盘精选混合A', m:'sz', t:'LOF' },

{ c:'162105', n:'金鹰持久增利债券C', m:'sz', t:'LOF' },

{ c:'162108', n:'金鹰元盛债券C', m:'sz', t:'LOF' },

{ c:'162201', n:'宏利成长混合', m:'sz', t:'LOF' },

{ c:'162202', n:'宏利周期混合', m:'sz', t:'LOF' },

{ c:'162203', n:'宏利稳定混合', m:'sz', t:'LOF' },

{ c:'162204', n:'宏利行业精选混合A', m:'sz', t:'LOF' },

{ c:'162205', n:'宏利风险预算混合', m:'sz', t:'LOF' },

{ c:'162207', n:'宏利效率优选混合', m:'sz', t:'LOF' },

{ c:'162208', n:'宏利首选企业股票A', m:'sz', t:'LOF' },

{ c:'162209', n:'宏利市值优选混合A', m:'sz', t:'LOF' },

{ c:'162210', n:'宏利集利债券A', m:'sz', t:'LOF' },

{ c:'162212', n:'宏利红利先锋混合A', m:'sz', t:'LOF' },

{ c:'162213', n:'宏利沪深300指数增强A', m:'sz', t:'LOF' },

{ c:'162214', n:'宏利领先中小盘混合', m:'sz', t:'LOF' },

{ c:'162215', n:'宏利聚利债券', m:'sz', t:'LOF' },

{ c:'162216', n:'宏利500指数增强', m:'sz', t:'LOF' },

{ c:'162307', n:'海富通中证A100指数A', m:'sz', t:'LOF' },

{ c:'162412', n:'华宝医疗ETF联接A', m:'sz', t:'LOF' },

{ c:'162414', n:'华宝新机遇混合A', m:'sz', t:'LOF' },

{ c:'162509', n:'国联安中证A100指数', m:'sz', t:'LOF' },

{ c:'162711', n:'广发中证500ETF联接A', m:'sz', t:'LOF' },

{ c:'162712', n:'广发聚利债券A', m:'sz', t:'LOF' },

{ c:'162715', n:'广发聚源债券A', m:'sz', t:'LOF' },

{ c:'162717', n:'广发成长新动能混合A', m:'sz', t:'LOF' },

{ c:'162719', n:'广发道琼斯石油指数人民币A', m:'sz', t:'LOF' },

{ c:'162721', n:'广发积极优势混合(FOF-LOF)A', m:'sz', t:'LOF' },

{ c:'163007', n:'长信利众债券A', m:'sz', t:'LOF' },

{ c:'163008', n:'长信利鑫债券A', m:'sz', t:'LOF' },

{ c:'163109', n:'申万菱信深证成份指数A', m:'sz', t:'LOF' },

{ c:'163110', n:'申万菱信量化小盘股票A', m:'sz', t:'LOF' },

{ c:'163111', n:'申万菱信中小企业100指数A', m:'sz', t:'LOF' },

{ c:'163113', n:'申万菱信中证申万证券行业指数A', m:'sz', t:'LOF' },

{ c:'163114', n:'申万菱信中证环保产业指数A', m:'sz', t:'LOF' },

{ c:'163115', n:'申万菱信中证军工指数A', m:'sz', t:'LOF' },

{ c:'163116', n:'申万中证申万电子行业投资指数A', m:'sz', t:'LOF' },

{ c:'163118', n:'申万菱信中证申万医药生物指数A', m:'sz', t:'LOF' },

{ c:'163208', n:'诺安油气能源', m:'sz', t:'LOF' },

{ c:'163302', n:'大摩资源优选混合', m:'sz', t:'LOF' },

{ c:'163409', n:'兴全绿色投资混合', m:'sz', t:'LOF' },

{ c:'163411', n:'兴全精选混合', m:'sz', t:'LOF' },

{ c:'163412', n:'兴全轻资产混合', m:'sz', t:'LOF' },

{ c:'163417', n:'兴全合宜混合A', m:'sz', t:'LOF' },

{ c:'163418', n:'兴全合兴混合A', m:'sz', t:'LOF' },

{ c:'163503', n:'天治核心成长混合', m:'sz', t:'LOF' },

{ c:'163801', n:'中银中国混合A', m:'sz', t:'LOF' },

{ c:'163811', n:'中银双利债券A', m:'sz', t:'LOF' },

{ c:'163813', n:'中银全球策略(QDII-FOF)A', m:'sz', t:'LOF' },

{ c:'163816', n:'中银转债增强债券A', m:'sz', t:'LOF' },

{ c:'163818', n:'中银中小盘成长混合', m:'sz', t:'LOF' },

{ c:'163819', n:'中银信用增利债券A', m:'sz', t:'LOF' },

{ c:'163821', n:'中银沪深300等权重指数', m:'sz', t:'LOF' },

{ c:'163822', n:'中银主题策略混合A', m:'sz', t:'LOF' },

{ c:'163823', n:'中银稳健策略混合', m:'sz', t:'LOF' },

{ c:'163827', n:'中银产业债债券A', m:'sz', t:'LOF' },

{ c:'163907', n:'中海惠裕纯债发起式', m:'sz', t:'LOF' },

{ c:'164105', n:'华富强化回报债券', m:'sz', t:'LOF' },

{ c:'164205', n:'天弘文化新兴产业股票A', m:'sz', t:'LOF' },

{ c:'164206', n:'天弘添利债券C', m:'sz', t:'LOF' },

{ c:'164208', n:'天弘丰利债券E', m:'sz', t:'LOF' },

{ c:'164210', n:'天弘同利债券C', m:'sz', t:'LOF' },

{ c:'164403', n:'前海开源沪港深农业混合A', m:'sz', t:'LOF' },

{ c:'164508', n:'国富中证A100指数增强', m:'sz', t:'LOF' },

{ c:'164509', n:'国富恒利债券A', m:'sz', t:'LOF' },

{ c:'164606', n:'华泰柏瑞信用增利债A', m:'sz', t:'LOF' },

{ c:'164701', n:'汇添富黄金及贵金属(QDII-LOF-FOF)A', m:'sz', t:'LOF' },

{ c:'164703', n:'汇添富纯债A', m:'sz', t:'LOF' },

{ c:'164705', n:'汇添富恒生指数(QDII-LOF)A', m:'sz', t:'LOF' },

{ c:'164808', n:'工银四季收益债券A', m:'sz', t:'LOF' },

{ c:'164809', n:'工银中证500ETF联接A', m:'sz', t:'LOF' },

{ c:'164814', n:'工银双债增强债券', m:'sz', t:'LOF' },

{ c:'164824', n:'工银印度基金人民币', m:'sz', t:'LOF' },

{ c:'164902', n:'交银信用添利债券A', m:'sz', t:'LOF' },

{ c:'164906', n:'交银中证海外中国互联网指数A', m:'sz', t:'LOF' },

{ c:'165311', n:'建信信用增强债券A', m:'sz', t:'LOF' },

{ c:'165313', n:'建信优势动力混合', m:'sz', t:'LOF' },

{ c:'165508', n:'中信保诚深度价值混合', m:'sz', t:'LOF' },

{ c:'165509', n:'中信保诚增强收益债券A', m:'sz', t:'LOF' },

{ c:'165511', n:'中信保诚中证500指数A', m:'sz', t:'LOF' },

{ c:'165512', n:'中信保诚新机遇混合', m:'sz', t:'LOF' },

{ c:'165513', n:'中信保诚全球商品主题A', m:'sz', t:'LOF' },

{ c:'165515', n:'中信保诚沪深300指数A', m:'sz', t:'LOF' },

{ c:'165516', n:'中信保诚周期轮动混合A', m:'sz', t:'LOF' },

{ c:'165517', n:'中信保诚双盈债券A', m:'sz', t:'LOF' },

{ c:'165519', n:'中信保诚中证800医药指数A', m:'sz', t:'LOF' },

{ c:'165521', n:'中信保诚中证800金融指数A', m:'sz', t:'LOF' },

{ c:'165522', n:'中信保诚中证TMTA', m:'sz', t:'LOF' },

{ c:'165525', n:'中信保诚中证基建工程指数A', m:'sz', t:'LOF' },

{ c:'165528', n:'中信保诚鼎利混合A', m:'sz', t:'LOF' },

{ c:'166006', n:'中欧行业成长混合A', m:'sz', t:'LOF' },

{ c:'166008', n:'中欧增强回报债券A', m:'sz', t:'LOF' },

{ c:'166010', n:'中欧鼎利债券A', m:'sz', t:'LOF' },

{ c:'166011', n:'中欧盛世成长混合A', m:'sz', t:'LOF' },

{ c:'166016', n:'中欧纯债债券C', m:'sz', t:'LOF' },

{ c:'166019', n:'中欧价值智选混合A', m:'sz', t:'LOF' },

{ c:'166020', n:'中欧成长优选混合A', m:'sz', t:'LOF' },

{ c:'166023', n:'中欧瑞丰灵活配置混合A', m:'sz', t:'LOF' },

{ c:'166105', n:'信澳鑫安债券A', m:'sz', t:'LOF' },

{ c:'166107', n:'信澳量化多因子混合A', m:'sz', t:'LOF' },

{ c:'166301', n:'华商新趋势优选灵活配置混合', m:'sz', t:'LOF' },

{ c:'166401', n:'浦银安盛稳健增利债券C', m:'sz', t:'LOF' },

{ c:'166801', n:'浙商聚潮新思维混合A', m:'sz', t:'LOF' },

{ c:'167001', n:'平安鼎泰混合', m:'sz', t:'LOF' },

{ c:'167002', n:'平安鼎越混合', m:'sz', t:'LOF' },

{ c:'167003', n:'平安鼎弘混合A', m:'sz', t:'LOF' },

{ c:'167301', n:'方正富邦中证保险A', m:'sz', t:'LOF' },

{ c:'167302', n:'方正富邦大湾区综指', m:'sz', t:'LOF' },

{ c:'167501', n:'安信宝利债券D', m:'sz', t:'LOF' },

{ c:'167504', n:'安信中短利率债A', m:'sz', t:'LOF' },

{ c:'167506', n:'安信深圳科技指数A', m:'sz', t:'LOF' },

{ c:'167601', n:'国金300指数增强A', m:'sz', t:'LOF' },

{ c:'168101', n:'九泰锐智事件驱动混合', m:'sz', t:'LOF' },

{ c:'168102', n:'九泰锐富事件驱动混合发起式A', m:'sz', t:'LOF' },

{ c:'168103', n:'九泰锐益混合A', m:'sz', t:'LOF' },

{ c:'168104', n:'九泰锐丰灵活配置混合A', m:'sz', t:'LOF' },

{ c:'168105', n:'九泰泰富灵活配置混合A', m:'sz', t:'LOF' },

{ c:'168203', n:'国联国证钢铁行业指数A', m:'sz', t:'LOF' },

{ c:'168204', n:'国联中证煤炭指数A', m:'sz', t:'LOF' },

{ c:'168301', n:'东海祥龙A', m:'sz', t:'LOF' },

{ c:'168401', n:'红土精选混合A', m:'sz', t:'LOF' },

{ c:'168501', n:'华银产业升级', m:'sz', t:'LOF' },

{ c:'168701', n:'合煦智远金融科技指数A', m:'sz', t:'LOF' },

{ c:'169101', n:'东方红睿丰混合', m:'sz', t:'LOF' },

{ c:'169104', n:'东方红睿满沪港深混合A', m:'sz', t:'LOF' },

{ c:'169105', n:'东方红睿华沪港深混合A', m:'sz', t:'LOF' },

{ c:'169107', n:'东方红恒阳五年持有混合', m:'sz', t:'LOF' },

{ c:'169201', n:'浙商鼎盈事件驱动混合', m:'sz', t:'LOF' },

{ c:'501001', n:'财通多策略精选混合', m:'sh', t:'LOF' },

{ c:'501005', n:'汇添富中证精准医疗指数A', m:'sh', t:'LOF' },

{ c:'501007', n:'汇添富中证互联网医疗指数A', m:'sh', t:'LOF' },

{ c:'501009', n:'汇添富中证生物科技指数A', m:'sh', t:'LOF' },

{ c:'501011', n:'汇添富中证中药ETF联接A', m:'sh', t:'LOF' },

{ c:'501015', n:'财通多策略升级混合A', m:'sh', t:'LOF' },

{ c:'501016', n:'国泰中证申万证券行业指数A', m:'sh', t:'LOF' },

{ c:'501017', n:'国泰融丰外延增长混合A', m:'sh', t:'LOF' },

{ c:'501019', n:'国泰国证航天军工指数A', m:'sh', t:'LOF' },

{ c:'501021', n:'华宝港股通标普香港上市中国中小盘指数A', m:'sh', t:'LOF' },

{ c:'501022', n:'银华鑫盛灵活配置混合A', m:'sh', t:'LOF' },

{ c:'501026', n:'财通多策略福享混合', m:'sh', t:'LOF' },

{ c:'501028', n:'财通多策略福瑞混合发起式A', m:'sh', t:'LOF' },

{ c:'501030', n:'汇添富中证环境治理指数A', m:'sh', t:'LOF' },

{ c:'501032', n:'财通福盛混合发起A', m:'sh', t:'LOF' },

{ c:'501036', n:'汇添富中证500ETF联接A', m:'sh', t:'LOF' },

{ c:'501043', n:'汇添富沪深300指数A', m:'sh', t:'LOF' },

{ c:'501047', n:'汇添富中证全指证券公司ETF联接A', m:'sh', t:'LOF' },

{ c:'501051', n:'圆信永丰汇利LOF', m:'sh', t:'LOF' },

{ c:'501057', n:'汇添富中证新能源汽车产业指数A', m:'sh', t:'LOF' },

{ c:'501059', n:'西部利得国企红利指数增强A', m:'sh', t:'LOF' },

{ c:'501060', n:'中金中证优选300指数A', m:'sh', t:'LOF' },

{ c:'501064', n:'国泰价值优选灵活配置混合A', m:'sh', t:'LOF' },

{ c:'501066', n:'东方红恒元五年持有混合', m:'sh', t:'LOF' },

{ c:'501071', n:'泓德丰泽LOF', m:'sh', t:'LOF' },

{ c:'501073', n:'华安智联LOF', m:'sh', t:'LOF' },

{ c:'501075', n:'万家科创主题灵活配置混合A', m:'sh', t:'LOF' },

{ c:'501076', n:'鹏华创新动力LOF', m:'sh', t:'LOF' },

{ c:'501078', n:'广发科创主题灵活配置混合', m:'sh', t:'LOF' },

{ c:'501079', n:'大成科创主题混合A', m:'sh', t:'LOF' },

{ c:'501080', n:'中金科创主题灵活配置混合', m:'sh', t:'LOF' },

{ c:'501082', n:'博时科创主题灵活配置混合A', m:'sh', t:'LOF' },

{ c:'501220', n:'国泰行业轮动股票(FOF-LOF)A', m:'sh', t:'LOF' },

{ c:'501222', n:'易方达如意招享混合(FOF-LOF)A', m:'sh', t:'LOF' },

{ c:'501227', n:'泓德红利优选混合A', m:'sh', t:'LOF' },

{ c:'501300', n:'海富通全球收益债券人民币', m:'sh', t:'LOF' },

{ c:'501301', n:'华宝港股通恒生中国(香港上市)30ETF联接A', m:'sh', t:'LOF' },

{ c:'501302', n:'南方恒指ETF联接A', m:'sh', t:'LOF' },

{ c:'501303', n:'广发恒生中型股指数A', m:'sh', t:'LOF' },

{ c:'501305', n:'汇添富港股红利ETF联接A', m:'sh', t:'LOF' },

{ c:'501307', n:'银河中证沪港深高股息A', m:'sh', t:'LOF' },

{ c:'501310', n:'华宝沪港深价值指数A', m:'sh', t:'LOF' },

{ c:'501311', n:'嘉实港股通新经济指数A', m:'sh', t:'LOF' },

{ c:'501312', n:'华宝海外科技股票(QDII-LOF)A', m:'sh', t:'LOF' },

{ c:'502000', n:'西部利得中证500指数增强A', m:'sh', t:'LOF' },

{ c:'502003', n:'易方达中证军工A', m:'sh', t:'LOF' },

{ c:'502006', n:'易方达中证国企改革A', m:'sh', t:'LOF' },

{ c:'502010', n:'易方达中证全指证券公司指数A', m:'sh', t:'LOF' },

{ c:'502013', n:'长盛中证申万一带一路指数', m:'sh', t:'LOF' },

{ c:'502023', n:'鹏华国证钢铁行业指数A', m:'sh', t:'LOF' },

{ c:'502048', n:'易方达上证50指数A', m:'sh', t:'LOF' },

{ c:'502053', n:'长盛中证证券公司指数A', m:'sh', t:'LOF' },

{ c:'502056', n:'广发中证医疗ETF联接A', m:'sh', t:'LOF' },

];



console.log(`  📋 内置基金数: ${FUND_LIST.length}`);

console.log(`  📋 内置品类: ${[...new Set(FUND_LIST.map(f=>f.t||'ETF'))].join(', ')}`);



// =============================================================

// 缓存 & 排除设置

// =============================================================

const cache = { quotes: null, fundNavs: null, fundStatuses: null, time: 0, health: {} };

const TTL = 15000; // 15秒缓存

const FUND_LIST_PATH = path.join(__dirname, 'custom-funds.json');

const EXCLUDED_PATH = path.join(__dirname, 'excluded-funds.json');



const customCodes = new Set();

const excludedCodes = new Set();



// ====== 加载排除列表 ======

function loadExcluded() {

  try { return JSON.parse(fs.readFileSync(EXCLUDED_PATH, 'utf-8')) || []; }

  catch(e) { return []; }

}



function saveExcluded(list) {

  fs.writeFileSync(EXCLUDED_PATH, JSON.stringify(list, null, 2), 'utf-8');

}



function initExcluded() {

  const list = loadExcluded();

  list.forEach(c => excludedCodes.add(c));

}

initExcluded();



// ====== 加载自选列表 ======

function initCustomFunds() {

  try {

    const d = fs.readFileSync(FUND_LIST_PATH, 'utf-8');

    const arr = JSON.parse(d);

    arr.forEach(f => {

      if (!excludedCodes.has(f.c)) {

        customCodes.add(f.c);

        FUND_LIST.push(f);

      }

    });

  } catch(e) {}

}

initCustomFunds();



// ====== HTTP GET 工具 ======

function httpGet(url, timeout = 8000) {

  return new Promise((resolve, reject) => {

    const mod = url.startsWith('https') ? https : http;

    const urlObj = new URL(url);

    const opts = {

      hostname: urlObj.hostname,

      port: urlObj.port || (url.startsWith('https') ? 443 : 80),

      path: urlObj.pathname + urlObj.search,

      timeout: timeout,

      headers: {

        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

        "Accept": "text/html,application/json,*/*",

        "Referer": "https://www.google.com/"

      }

    };

    // 修正CNINFO Referer

    if (url.indexOf("cninfo.com.cn") >= 0) {

      opts.headers["Referer"] = "https://www.cninfo.com.cn/";

      opts.headers["Accept"] = "application/json, text/plain, */*";

    }

    const req = mod.get(opts, res => {

      let data = "";

      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {

        httpGet(res.headers.location, timeout).then(resolve).catch(reject);

        return;

      }

      res.on("data", d => data += d.toString("binary"));

      res.on("end", () => {

        // 腾讯行情API始终返回GBK（即使不声明charset）

        const isTencentQuote = url.indexOf("qt.gtimg.cn") >= 0;

        if (isTencentQuote || data.indexOf("charset=gbk") >= 0 || data.indexOf("charset=GBK") >= 0 || data.indexOf("charset=gb2312") >= 0 || data.indexOf("charset=\"gbk\"") >= 0 || data.indexOf("charset=\"gb2312\"") >= 0) {

          try {

            const iconv = require("iconv-lite");

            data = iconv.decode(Buffer.from(data, "binary"), "gbk");

          } catch(e) { /* ignore */ }

        }

        resolve(data);

      });

    });

    req.on("error", reject);

    req.on("timeout", () => { req.destroy(); reject(new Error("超时")); });

  });

}



// ====== 解析腾讯行情 ======

function parseTencentLine(line) {

  if (!line) return null;

  const p = line.split('~');

  if (p.length < 30) return null;

  const name = p[1];

  const code = p[2];

  const price = parseFloat(p[3]);

  const prevClose = parseFloat(p[4]);

  const open = parseFloat(p[5]);

  const vol = parseFloat(p[6]);

  const amount = parseFloat(p[7]);

  const high = parseFloat(p[33]);

  const low = parseFloat(p[34]);

  const change = prevClose > 0 ? (price - prevClose) / prevClose : 0;

  const tencentType = p[45] || '';

  return { code, name, price, prevClose, open, high, low, change, vol, amount, tencentType, raw: p };

}



// ====== 获取所有实时行情 ======

async function fetchTencentQuotes() {

  const codes = FUND_LIST.filter(f => !excludedCodes.has(f.c));

  // 批处理，每批100个

  const batchSize = 100;

  const results = {};

  for (let i = 0; i < codes.length; i += batchSize) {

    const batch = codes.slice(i, i + batchSize);

    const query = batch.map(f => f.m + f.c).join(',');

    try {

      const raw = await httpGet('http://qt.gtimg.cn/q=' + query);

      const lines = raw.trim().split('\n');

      for (const line of lines) {

        const q = parseTencentLine(line);

        if (q) results[q.code] = q;

      }

    } catch(e) {}

  }

  return results;

}



// ====== 解析天天基金净值 ======

function parseFundNav(body) {

  try {

    const json = JSON.parse(body.replace(/^jsonpgz\(/, '').replace(/\);$/, ''));

    return {

      nav: parseFloat(json.dwjz) || 0,        // 单位净值（T-1日）

      estNav: parseFloat(json.gsz) || 0,       // 估算净值（盘中实时）

      navDate: json.jzrq,

    };

  } catch(e) { return null; }

}



async function fetchFundNav(code) {

  try {

    const body = await httpGet(`http://fundgz.1234567.com.cn/js/${code}.js`);

    return parseFundNav(body);

  } catch(e) { return null; }

}



async function fetchAllFundNavs() {

  const codes = FUND_LIST.filter(f => !excludedCodes.has(f.c));

  const results = {};

  const batchSize = 10;

  for (let i = 0; i < codes.length; i += batchSize) {

    const batch = codes.slice(i, i + batchSize);

    const promises = batch.map(f => fetchFundNav(f.c).then(n => { if (n && n.nav > 0) results[f.c] = n; }));

    await Promise.allSettled(promises);

    if (i + batchSize < codes.length) {

      await new Promise(r => setTimeout(r, 100));

    }

  }

  return results;

}



// ====== 获取指数行情 ======

async function fetchIndexes() {

  // 只保留四个核心指数

  const idxDefs = [

    { c:'sh000001', n:'上证指数' },

    { c:'sz399001', n:'深证成指' },

    { c:'sz399006', n:'创业板指' },

    { c:'sh000688', n:'科创50' },

  ];

  const query = idxDefs.map(i => i.c).join(',');

  try {

    let raw = await httpGet('http://qt.gtimg.cn/q=' + query);

    // 腾讯行情返回GBK编码，用iconv解码

    if (raw.indexOf('~') >= 0) {

      try {

        const iconv = require('iconv-lite');

        const buf = Buffer.from(raw, 'binary');

        const decoded = iconv.decode(buf, 'gbk');

        // 检查是否成功解码（解码后的中文不含 � 则是成功的）

        if (decoded.indexOf('�') < 0 && decoded.indexOf('~') >= 0) {

          raw = decoded;

        }

      } catch(e) { /* iconv not available */ }

    }

    const lines = raw.trim().split('\n');

    return lines.map(line => {

      const p = line.split('~');

      if (p.length < 30) return null;

      const code = p[2];

      // 强制使用预定义中文名称（避免腾讯GBK乱码问题）

      const def = idxDefs.find(d => d.c.replace(/^[a-z]+/, '') === code);

      const name = def ? def.n : (p[1] || '');

      const price = parseFloat(p[3]);

      const pc = parseFloat(p[4]);

      const change = pc > 0 && price > 0 ? Math.round((price - pc) / pc * 10000) / 100 : 0;

      return { name, code, price, change };

    }).filter(Boolean);

  } catch(e) { return []; }

}



// ====== 获取基金交易状态（含申购状态 SGZT） ======

async function fetchFundStatus(code) {

  try {

    // 并行查询 fundgz（实时估算净值）和 eastmoney（申购状态+历史净值）

    const [fundgzBody, lsjzBody] = await Promise.allSettled([

      httpGet(`http://fundgz.1234567.com.cn/js/${code}.js`),

      (() => {

        const emUrl = `https://api.fund.eastmoney.com/f10/lsjz?callback=j&fundCode=${code}&pageIndex=1&pageSize=1`;

        // 使用 raw HTTP fetch + 正确的 Referer（因为 httpGet 默认 Referer 是 google，会被 eastmoney 拒绝）

        return new Promise((resolve, reject) => {

          const https = require('https');

          const urlObj = new URL(emUrl);

          const opts = {

            hostname: urlObj.hostname,

            port: 443,

            path: urlObj.pathname + urlObj.search,

            timeout: 6000,

            headers: {

              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',

              'Referer': 'https://fundf10.eastmoney.com/',

              'Accept': 'application/json, text/plain, */*',

            }

          };

          const req = https.get(opts, res => {

            let d = '';

            res.on('data', c => d += c);

            res.on('end', () => resolve(d.replace(/^j\(/, '').replace(/\);?\s*$/, '')));

          });

          req.on('error', reject);

          req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });

        });

      })(),

    ]);



    const result = { sgzt: '', shzt: '', sgLimit: '' };



    // 解析 fundgz

    if (fundgzBody.status === 'fulfilled') {

      try {

        const fg = JSON.parse(fundgzBody.value.replace(/^jsonpgz\(/, '').replace(/\);$/, ''));

        Object.assign(result, {

          status: fg.r || '',

          gsz: fg.gsz || null,

          gszzl: fg.gszzl || null,

          gztime: fg.gztime || '',

          name: fg.name || '',

          fundCode: fg.fundcode || code,

          jzrq: fg.jzrq || '',

          dwjz: fg.dwjz || null,

        });

      } catch(e) {}

    }



    // 解析 eastmoney LSJZ → 申购状态

    if (lsjzBody.status === 'fulfilled') {

      try {

        const lsjz = JSON.parse(lsjzBody.value);

        if (lsjz && lsjz.Data && lsjz.Data.LSJZList && lsjz.Data.LSJZList.length > 0) {

          const item = lsjz.Data.LSJZList[0];

          result.sgzt = item.SGZT || '';

          // ETF 的"场内买入"对用户无参考意义，置空

          const isETF = FUND_LIST.some(f => f.c === code && f.t === 'ETF');

          if (result.sgzt === '场内买入' && isETF) result.sgzt = '';

          result.shzt = item.SHZT || '';

          // 如果有新的净值值，覆盖 dwjz

          const emDwjz = parseFloat(item.DWJZ);

          if (emDwjz > 0) result.dwjz = emDwjz;

          // 【修复】"限制大额申购"≠"暂停申购"：让用户明确知道仍可申购少量
          // 并统一 sgzt 列显示为友好文本
          if (result.sgzt === '限制大额申购') {
            result.sgzt = '✅限大额';
            result.sgLimit = '⚠️限大额';
          }
          else if (result.sgzt.includes('暂停申购') || result.sgzt === '暂停') {
            result.sgLimit = '🛑暂停';
            result.sgzt = '🛑暂停申购';
          }
          else if (result.sgzt.includes('暂停')) {
            result.sgLimit = '🛑暂停';
            // 保留原始文本但前缀标记
          }
          else if (result.sgzt.includes('限制大额')) result.sgLimit = '⚠️限大额';
          else if (result.sgzt.includes('限制') && !result.sgzt.includes('暂停')) result.sgLimit = '有上限';
          else if (result.sgzt.includes('场内买入')) {
            if (isETF) result.sgLimit = '';
            else result.sgLimit = '场内买卖';
          }
          else if (result.sgzt.includes('场内') && !result.sgzt.includes('买入')) result.sgLimit = '场内买卖';
          else if (result.sgzt.includes('开放')) result.sgLimit = '✅不限';

        }

      } catch(e) {}

    }



    return result;

  } catch(e) { return null; }

}



async function fetchAllFundStatuses() {

  const codes = FUND_LIST.filter(f => !excludedCodes.has(f.c));

  const results = {};

  const batchSize = 20;

  for (let i = 0; i < codes.length; i += batchSize) {

    const batch = codes.slice(i, i + batchSize);

    const promises = batch.map(f => fetchFundStatus(f.c).then(s => { if (s) results[f.c] = s; }));

    await Promise.allSettled(promises);

    if (i + batchSize < codes.length) {

      await new Promise(r => setTimeout(r, 100));

    }

  }

  return results;

}



// ====== 主数据函数 ======

async function getData() {

  const now = Date.now();

  if (cache.quotes && cache.time && now - cache.time < TTL) {

    return { data: cache.quotes, indexes: cache.indexes || [], fundNavs: cache.fundNavs || {}, fundStatuses: cache.fundStatuses || {} };

  }



  const [quotes, navs, indexes, statuses] = await Promise.all([

    fetchTencentQuotes(),

    fetchAllFundNavs(),

    fetchIndexes(),

    fetchAllFundStatuses(),

  ]);



  const data = FUND_LIST.filter(f => !excludedCodes.has(f.c)).map(f => {

    const q = quotes[f.c];

    const nav = navs[f.c];

    const st = statuses[f.c];



    // 净值来源优先级：

    // 1) 腾讯行情字段81（基金单位净值，更新最及时）

    // 2) 东方财富历史净值API dwjz（从 fetchFundStatus LSJZ 获取的最新净值）

    // 3) 东方财富 fundgz dwjz（T-1净值，备选）

    // 4) 昨收（兜底）

    let finalNav = null;

    if (q && q.fundNav > 0) finalNav = q.fundNav;

    else if (st && st.dwjz > 0) finalNav = st.dwjz;

    else if (nav && nav.nav > 0) finalNav = nav.nav;

    else if (q && q.prevClose > 0) finalNav = q.prevClose;



    // 标记是否为自定义添加的基金

    const isCustomFund = customCodes.has(f.c);

    finalNav = finalNav ? Math.round(finalNav * 10000) / 10000 : null;



    const chg = q ? q.change : 0;



    // 估算净值优先级：

    // 1) 东方财富 fundgz gsz（盘中实时估算净值）

    // 2) 净值 × (1 + 涨跌幅 × 0.9) 兜底估算

    let finalEstNav = null;

    if (nav && nav.estNav > 0) finalEstNav = nav.estNav;

    else if (finalNav && chg != null) finalEstNav = Math.round(finalNav * (1 + chg / 100 * 0.9) * 10000) / 10000;



    const premium = finalNav && q && q.price > 0 ? Math.round((q.price - finalNav) / finalNav * 10000) / 100 : null;

    const realPremium = finalEstNav && q && q.price > 0 ? Math.round((q.price - finalEstNav) / finalEstNav * 10000) / 100 : premium;



    return {

      code: f.c, name: f.n, market: f.m, type: f.t || 'ETF',

      price: q ? q.price : null,

      change: q ? q.change : null,

      changePct: q && q.change ? Math.round(q.change * 10000) / 100 : null,

      amount: q ? Math.round(q.vol * q.price * 100 / 10000) : null,

      vol: q ? Math.round(q.vol) : null,

      open: q ? q.open : null,

      high: q ? q.high : null,

      low: q ? q.low : null,

      nav: finalNav,

      navDate: nav ? nav.navDate : null,

      estNav: finalEstNav,

      premium,

      realPremium,

      status: st ? st.status : null,

      gsz: st ? (st.gsz ? Math.round(parseFloat(st.gsz) * 10000) / 10000 : null) : null,

      gszzl: st ? st.gszzl : null,

      gztime: st ? st.gztime : null,

      dwjz: st ? (st.dwjz ? parseFloat(st.dwjz) : null) : null,

      jzrq: st ? st.jzrq : null,

      // 申购状态 & 限额（从东方财富基金历史净值API获取）

      sgzt: st ? (st.sgzt || '') : '',

      sgLimit: st ? (st.sgLimit || '') : '',

      isCustom: isCustomFund,

    };

  });



  cache.quotes = data;

  cache.indexes = indexes;

  cache.fundNavs = navs;

  cache.fundStatuses = statuses;

  cache.time = now;

  return { data, indexes, fundNavs: navs, fundStatuses: statuses };

}



// ====== 默认房价数据（备份） ======

function getDefaultHouseData(city) {

  const sets = {

    suzhou: [

      {month:'2016-01',price:12306},{month:'2016-06',price:15676},{month:'2017-01',price:19106},

      {month:'2017-06',price:21027},{month:'2018-01',price:21623},{month:'2018-06',price:21888},

      {month:'2019-01',price:22887},{month:'2019-06',price:23455},{month:'2020-01',price:23751},

      {month:'2020-06',price:24432},{month:'2021-01',price:25320},{month:'2021-06',price:26810},

      {month:'2022-01',price:26890},{month:'2022-06',price:25424},{month:'2023-01',price:24101},

      {month:'2023-06',price:23169},{month:'2024-01',price:22145},{month:'2024-06',price:21250},

      {month:'2025-01',price:20580},{month:'2025-06',price:19880},

    ],

    shanghai: [

      {month:'2016-01',price:36234},{month:'2016-06',price:41832},{month:'2017-01',price:41067},

      {month:'2017-06',price:42836},{month:'2018-01',price:43258},{month:'2018-06',price:46277},

      {month:'2019-01',price:47727},{month:'2019-06',price:49445},{month:'2020-01',price:50264},

      {month:'2020-06',price:51079},{month:'2021-01',price:53219},{month:'2021-06',price:55431},

      {month:'2022-01',price:55976},{month:'2022-06',price:55384},{month:'2023-01',price:55102},

      {month:'2023-06',price:55283},{month:'2024-01',price:54100},{month:'2024-06',price:52850},

      {month:'2025-01',price:51800},{month:'2025-06',price:50600},

    ],

    beijing: [

      {month:'2016-01',price:35215},{month:'2016-06',price:38926},{month:'2017-01',price:42386},

      {month:'2017-06',price:45261},{month:'2018-01',price:45932},{month:'2018-06',price:47063},

      {month:'2019-01',price:47815},{month:'2019-06',price:48291},{month:'2020-01',price:48567},

      {month:'2020-06',price:49172},{month:'2021-01',price:49867},{month:'2021-06',price:50971},

      {month:'2022-01',price:51167},{month:'2022-06',price:50541},{month:'2023-01',price:50213},

      {month:'2023-06',price:50826},{month:'2024-01',price:49600},{month:'2024-06',price:48350},

      {month:'2025-01',price:47200},{month:'2025-06',price:46100},

    ],

  };

  return sets[city] || sets.suzhou;

}



// ====== 加载自定义基金列表 ======

function loadCustomFunds() {

  try { return JSON.parse(fs.readFileSync(FUND_LIST_PATH, 'utf-8')) || []; }

  catch(e) { return []; }

}



function saveCustomFunds(list) {

  fs.writeFileSync(FUND_LIST_PATH, JSON.stringify(list, null, 2), 'utf-8');

}



function autoMarket(code) {

  if (!code) return 'sh';

  const c = code.toString().trim();

  const first = parseInt(c[0], 10);

  if ([0,1,2,3].includes(first)) return 'sz';

  if (c.startsWith('159') || c.startsWith('16')) return 'sz';

  if (c.startsWith('51') || c.startsWith('56') || c.startsWith('58') || c.startsWith('50')) return 'sh';

  return 'sh';

}



// =============================================================

// MIME 类型

// =============================================================

const MIME = {

  '.html': 'text/html; charset=utf-8',

  '.css': 'text/css; charset=utf-8',

  '.js': 'text/javascript; charset=utf-8',

  '.json': 'application/json; charset=utf-8',

  '.png': 'image/png',

  '.jpg': 'image/jpeg',

  '.jpeg': 'image/jpeg',

  '.gif': 'image/gif',

  '.svg': 'image/svg+xml',

  '.ico': 'image/x-icon',

  '.webp': 'image/webp',

};



// =============================================================

// HTTP 服务

// =============================================================

const server = http.createServer(async (req, res) => {

  const url = new URL(req.url, `http://localhost:${PORT}`);

  const p = url.pathname;

  res.setHeader('Access-Control-Allow-Origin', '*');

  

  try {

    if (p === '/api/premium') {

      const data = await getData();

      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

      res.end(JSON.stringify(data));

      return;

    }

    // ====== API: 获取单只基金近20天溢价率 + 场内份额历史 ======

    if (p.startsWith('/api/fund-history/')) {

      const code = p.replace('/api/fund-history/', '');

      try {

        // 从 FUND_LIST 中找到基金的名称和类型
        const fundInfo = FUND_LIST.find(f => f.c === code);
        const fundName = fundInfo ? fundInfo.n : '';
        const market = fundInfo ? fundInfo.m : autoMarket(code);
        const fundType = fundInfo ? fundInfo.t : 'ETF';

        // 并行请求：K线 + 净值历史 + 实时份额 + 季度份额历史
        const [klineRawResult, lsjzHtmlResult] = await Promise.allSettled([
          httpGet(`https://ifzq.gtimg.cn/appstock/app/fqkline/get?param=${market}${code},day,,,30,qfq`, 6000),
          new Promise((resolve, reject) => {
            const urlObj = new URL(`https://api.fund.eastmoney.com/f10/lsjz?callback=j&fundCode=${code}&pageIndex=1&pageSize=30`);
            const opts = {
              hostname: urlObj.hostname, path: urlObj.pathname + urlObj.search,
              method: 'GET', timeout: 6000,
              headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', 'Referer': `https://fund.eastmoney.com/${code}.html`, }
            };
            const req = https.get(opts, res => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve(d)); });
            req.on('error', reject); req.end();
          }),
        ]);

        // 解析 K 线
        let klineData = [];
        if (klineRawResult.status === 'fulfilled') {
          try { const kj = JSON.parse(klineRawResult.value); const kData = kj?.data?.[`${market}${code}`]; klineData = kData?.qfqday || kData?.day || []; } catch(e) {}
        }

        // 解析净值
        let navList = [];
        if (lsjzHtmlResult.status === 'fulfilled') {
          try {
            const navMatch = lsjzHtmlResult.value.match(/j\((.+)\)/);
            if (navMatch) {
              const navJson = JSON.parse(navMatch[1]);
              navList = (navJson?.Data?.LSJZList || [])
                .filter(x => x.FSRQ && x.DWJZ)
                .map(x => ({ date: x.FSRQ, dwjz: parseFloat(x.DWJZ) || 0, ljjz: parseFloat(x.LJJZ) || 0, jzzzl: parseFloat(x.JZZZL) || 0 }));
            }
          } catch(e) {}
        }

        // 构建价格映射 date -> { close, volume }
        const priceMap = {};
        for (const row of klineData) {
          if (row.length >= 5) {
            priceMap[row[0]] = { close: parseFloat(row[2]), volume: parseFloat(row[5]) || 0 };
          }
        }

        // 合并数据，取最近20条有价格+净值的日期
        const resultList = [];
        const today = new Date().toISOString().slice(0, 10);
        for (const nav of navList) {
          if (resultList.length >= 20) break;
          const date = nav.date;
          if (date > today) continue;
          const pr = priceMap[date];
          if (!pr || !pr.close || !nav.dwjz) continue;
          const premium = ((pr.close - nav.dwjz) / nav.dwjz) * 100;
          resultList.push({
            date,
            price: pr.close,
            nav: nav.dwjz,
            premium: Math.round(premium * 10000) / 10000,
            volume: pr.volume,
            jzzzl: nav.jzzzl,
          });
        }

        // ====== 获取实时行情数据（份额+价格）用于补充+插值 ======
        let currentShares = null;
        // 优先使用上交所官方每日份额数据（收盘清算后，最权威）
        if (market === 'sh') {
          try {
            // 上交所ETF规模接口
            const today = new Date().toISOString().slice(0, 10);
            const sseRaw = await new Promise((resolve, reject) => {
              const opts = {
                hostname: 'query.sse.com.cn',
                path: `/commonQuery.do?jsonCallBack=jpc&sqlId=COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L&STAT_DATE=${today}&pageHelp.pageSize=1000&pageHelp.pageNo=1`,
                method: 'GET', timeout: 5000,
                headers: { 'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.sse.com.cn/market/funddata/volumn/etfvolumn/' }
              };
              const req = http.get(opts, res => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve(d)); });
              req.on('error', reject); req.end();
            });
            const sseJson = JSON.parse(sseRaw.replace(/^jpc\(|\)$/g, ''));
            if (sseJson?.result) {
              const found = sseJson.result.find(r => r.SEC_CODE === code);
              if (found && found.TOT_VOL) {
                currentShares = parseFloat(found.TOT_VOL) * 10000;
              }
            }
          } catch(e) {}
          
          // ETF未查到，试LOF接口
          if (!currentShares) {
            try {
              const today = new Date().toISOString().slice(0, 10);
              const sseRaw = await new Promise((resolve, reject) => {
                const opts = {
                  hostname: 'query.sse.com.cn',
                  path: `/commonQuery.do?jsonCallBack=jpc&sqlId=COMMON_SSE_SJ_JJSJ_JJGM_LOFGMTJ_L&SEARCH_DATE=${today}&PRODUCT_TYPE=11,14,15&type=inParams&pageHelp.pageSize=1000&pageHelp.pageNo=1`,
                  method: 'GET', timeout: 5000,
                  headers: { 'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.sse.com.cn/market/funddata/volumn/lofvolumn/' }
                };
                const req = http.get(opts, res => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve(d)); });
                req.on('error', reject); req.end();
              });
              const sseJson = JSON.parse(sseRaw.replace(/^jpc\(|\)$/g, ''));
              if (sseJson?.result) {
                const found = sseJson.result.find(r => r.FUND_CODE === code);
                if (found && found.INTERNAL_VOL) {
                  const clean = String(found.INTERNAL_VOL).replace(/,/g, '');
                  currentShares = parseFloat(clean) * 10000;
                }
              }
            } catch(e) {}
          }
        }
        
        // 上交所未取到（或深交所基金），回退到腾讯行情
        if (!currentShares) {
          try {
            const qRaw = await httpGet(`http://qt.gtimg.cn/q=${market}${code}`, 4000);
            const qParts = qRaw.trim().split('~');
            const f72 = qParts.length > 72 ? parseFloat(qParts[72]) : null;
            const f76 = qParts.length > 76 ? parseFloat(qParts[76]) : null;
            currentShares = f76 || f72 || null;
          } catch(e) {
            // 回退到东方财富
            try {
              const secidPrefix = market === 'sz' ? '0.' : '1.';
              const qRaw = await new Promise((resolve, reject) => {
                const parsed = new URL(`http://push2.eastmoney.com/api/qt/stock/get?secid=${secidPrefix}${code}&fields=f57,f58,f84`);
                const opts = {
                  hostname: parsed.hostname,
                  path: parsed.pathname + parsed.search,
                  method: 'GET', timeout: 4000,
                  headers: { 'User-Agent': 'Mozilla/5.0' }
                };
                const req = http.get(opts, res => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve(d)); });
                req.on('error', reject); req.end();
              });
              const qj = JSON.parse(qRaw);
              const f84 = qj?.data?.f84;
              if (f84) currentShares = f84;
            } catch(e2) {}
          }
        }

        // ====== 补偿今天的数据行（盘中时K线已有数据但净值未公布） ======
        const todayStr = new Date().toISOString().slice(0, 10);
        const todayKline = priceMap[todayStr];
        if (todayKline && (resultList.length === 0 || resultList[0].date !== todayStr)) {
          // 有K线数据但净值未公布 -> 用天天基金盘中估值
          let todayNav = null;
          try {
            const estRaw = await httpGet(`http://fundgz.1234567.com.cn/js/${code}.js`, 4000);
            const m = estRaw.match(/gsz:"([\d.]+)"/);
            if (m) todayNav = parseFloat(m[1]);
          } catch(e) {}
          if (!todayNav && resultList.length > 0) todayNav = resultList[0].nav;
          
          if (todayNav && todayNav > 0) {
            const premium = ((todayKline.close - todayNav) / todayNav) * 100;
            resultList.unshift({
              date: todayStr,
              price: todayKline.close,
              nav: todayNav,
              premium: Math.round(premium * 10000) / 10000,
              volume: todayKline.volume,
              jzzzl: null,
            });
            if (resultList.length > 20) resultList.pop();
          }
        }

        // ====== 获取季度份额历史（gmbd 基金规模变动） ======

        // 获取季度份额历史（gmbd 基金规模变动）
        let quarterShares = [];
        try {
          const gmbdHtml = await new Promise((resolve, reject) => {
            const opts = {
              hostname: 'fundf10.eastmoney.com',
              path: `/FundArchivesDatas.aspx?type=gmbd&mode=0&code=${code}&rt=${Math.random()}`,
              method: 'GET', timeout: 5000,
              headers: { 'User-Agent': 'Mozilla/5.0', 'Referer': `https://fundf10.eastmoney.com/gmbd_${code}.html` }
            };
            const req = https.get(opts, res => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve(d)); });
            req.on('error', reject); req.end();
          });
          const cm = gmbdHtml.match(/gmbd_apidata\s*=\s*\{[^}]+?content:"(.+?)"/);
          if (cm) {
            const content = cm[1];
            const rows = [...content.matchAll(/<tr>(.+?)<\/tr>/gs)];
            for (const row of rows) {
              const cells = [...row[1].matchAll(/<td[^>]*>(.*?)<\/td>/gs)].map(c => c[1].replace(/<[^>]+>/g,'').trim());
              if (cells.length >= 5) {
                quarterShares.push({
                  date: cells[0],
                  buyIn: cells[1],
                  redeem: cells[2],
                  totalShares: cells[3],
                  netAsset: cells[4],
                });
              }
            }
          }
        } catch(e) {}

        // ====== 从上交所获取每日真实份额数据（替换线性插值） ======
        // 仅对上交所基金有效；对于交易日会返回该日真实清算份额
        const sseDailyShares = {};
        if (market === 'sh') {
          // 取最近20个交易日的日期
          const datesToFetch = [];
          for (let i = 0; i < 20; i++) {
            const d = new Date();
            d.setDate(d.getDate() - i);
            datesToFetch.push(d.toISOString().slice(0, 10));
          }
          // 先去ETF接口查
          try {
            const promises = datesToFetch.map(date => {
              return new Promise((resolve, reject) => {
                const opts = {
                  hostname: 'query.sse.com.cn',
                  path: `/commonQuery.do?jsonCallBack=jpc&sqlId=COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L&STAT_DATE=${date}&pageHelp.pageSize=1000&pageHelp.pageNo=1`,
                  method: 'GET', timeout: 3000,
                  headers: { 'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.sse.com.cn/market/funddata/volumn/etfvolumn/' }
                };
                const req = http.get(opts, res => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve({date, d})); });
                req.on('error', () => resolve({date, d: null})); req.end();
              });
            });
            const results = await Promise.all(promises);
            for (const r of results) {
              if (!r.d) continue;
              try {
                const j = JSON.parse(r.d.replace(/^jpc\(|\)$/g, ''));
                if (j?.result) {
                  const found = j.result.find(x => x.SEC_CODE === code);
                  if (found && found.TOT_VOL) {
                    sseDailyShares[r.date] = parseFloat(found.TOT_VOL) * 10000;
                  }
                }
              } catch(e) {}
            }
          } catch(e) {}
          
          // ETF未查到，试试LOF接口
          if (Object.keys(sseDailyShares).length === 0) {
            try {
              const promises = datesToFetch.map(date => {
                return new Promise((resolve, reject) => {
                  const opts = {
                    hostname: 'query.sse.com.cn',
                    path: `/commonQuery.do?jsonCallBack=jpc&sqlId=COMMON_SSE_SJ_JJSJ_JJGM_LOFGMTJ_L&SEARCH_DATE=${date}&PRODUCT_TYPE=11,14,15&type=inParams&pageHelp.pageSize=1000&pageHelp.pageNo=1`,
                    method: 'GET', timeout: 3000,
                    headers: { 'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.sse.com.cn/market/funddata/volumn/lofvolumn/' }
                  };
                  const req = http.get(opts, res => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve({date, d})); });
                  req.on('error', () => resolve({date, d: null})); req.end();
                });
              });
              const results = await Promise.all(promises);
              for (const r of results) {
                if (!r.d) continue;
                try {
                  const j = JSON.parse(r.d.replace(/^jpc\(|\)$/g, ''));
                  if (j?.result) {
                    const found = j.result.find(x => x.FUND_CODE === code);
                    if (found && found.INTERNAL_VOL) {
                      const clean = String(found.INTERNAL_VOL).replace(/,/g, '');
                      sseDailyShares[r.date] = parseFloat(clean) * 10000;
                    }
                  }
                } catch(e) {}
              }
            } catch(e) {}
          }
        }

        // 给每行历史数据填充份额
        // 先构建有序的已知份额点列表
        const knownPoints = [];
        // 1. 从上交所获取的每日真实份额数据（最准确）
        for (const [date, val] of Object.entries(sseDailyShares)) {
          knownPoints.push({ date, val });
        }
        // 2. 季度报告份额
        for (const qs of quarterShares) {
          const val = parseFloat(qs.totalShares.replace(/[^0-9.]/g, ''));
          if (!isNaN(val)) {
            knownPoints.push({ date: qs.date, val: val * 100000000 });
          }
        }
        knownPoints.sort((a, b) => a.date.localeCompare(b.date));
        // 去重（相同日期保留上交所数据优先）
        const uniquePoints = [];
        for (const p of knownPoints) {
          const last = uniquePoints[uniquePoints.length - 1];
          if (last && last.date === p.date) {
            // 后面的（上交所数据后添加的会排在后面）覆盖前面的
            last.val = p.val;
          } else {
            uniquePoints.push(p);
          }
        }
        knownPoints.length = 0;
        knownPoints.push(...uniquePoints);
        // 3. 如果最后日期在今天之前且当前实时份额可用，添加当前点为锚点
        if (currentShares) {
          const todayStr = new Date().toISOString().slice(0, 10);
          knownPoints.push({ date: todayStr, val: currentShares });
        }

        // 对每行历史数据进行线性插值
        for (let i = 0; i < resultList.length; i++) {
          const date = resultList[i].date;
          // 找到该日期前后的两个已知点
          let left = null, right = null;
          for (const p of knownPoints) {
            if (p.date <= date) left = p;
          }
          for (let j = knownPoints.length - 1; j >= 0; j--) {
            if (knownPoints[j].date >= date) right = knownPoints[j];
          }
          
          if (left && right) {
            if (left.date === right.date) {
              resultList[i].shares = left.val;
            } else {
              const t1 = new Date(left.date.replace(/-/g,'/')).getTime();
              const t2 = new Date(right.date.replace(/-/g,'/')).getTime();
              const t = new Date(date.replace(/-/g,'/')).getTime();
              const ratio = (t - t1) / (t2 - t1);
              resultList[i].shares = Math.round(left.val + (right.val - left.val) * ratio);
            }
          } else if (left) {
            resultList[i].shares = left.val;
          } else if (right) {
            resultList[i].shares = right.val;
          } else {
            resultList[i].shares = currentShares || null;
          }
        }

        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({
          ok: true,
          code,
          name: fundName,
          type: fundType,
          history: resultList,
          shares: {
            current: currentShares,
            quarterHistory: quarterShares,
          },
        }));
      } catch(e) {
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({ ok: false, code, error: e.message || '查询失败', shares: { current: null, quarterHistory: [] } }));
      }
      return;
    }

    // ====== API: 获取单只基金的申购限额详情 ======

    if (p.startsWith('/api/fund-limit/')) {

      const code = p.replace('/api/fund-limit/', '');

      try {

        // tsdata 需要使用 fundf10 Referer（httpGet 默认 Referer 会被拒绝）

        const tsDataUrl = `https://fundf10.eastmoney.com/tsdata_${code}.html`;

        const html = await new Promise((resolve, reject) => {

          const urlObj = new URL(tsDataUrl);

          const opts = {

            hostname: urlObj.hostname, port: 443,

            path: urlObj.pathname + urlObj.search,

            timeout: 8000,

            headers: {

              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',

              'Referer': 'https://fundf10.eastmoney.com/',

              'Accept': 'text/html,application/xhtml+xml',

            }

          };

          const req = https.get(opts, res => {

            let d = '';

            res.on('data', c => d += c);

            res.on('end', () => resolve(d));

          });

          req.on('error', reject);

          req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });

        });



        // 交易状态：<span>限大额 </span>  → "限大额"

        const statusMatch = html.match(/交易状态：<span>([^<]+?)\s*<\/span>/);

        const statusText = statusMatch ? statusMatch[1].trim() : '';



        // 单日累计购买上限50.00万元</span>  → "50.00万元"

        const limitMatch = html.match(/单日累计购买上限([^<]+?)<\/span>/);

        const limitText = limitMatch ? limitMatch[1].trim() : '';



        let limitNum = null;

        let limitUnit = '';

        if (limitText) {

          const numMatch = limitText.match(/^([\d.]+)\s*(万元|元|万|亿元)?/);

          if (numMatch) {

            limitNum = parseFloat(numMatch[1]);

            limitUnit = numMatch[2] || '元';

          }

        }



        let limitLabel = limitText;

        if (limitNum !== null) {

          if (limitUnit === '万元' && limitNum >= 10000) {

            limitLabel = `${limitNum / 10000}亿元`;

          } else {

            limitLabel = `${limitNum}${limitUnit}`;

          }

        }



        // 完整详情（保留括号描述）

        const detailMatch = html.match(/(\(?<span>单日累计购买上限[^<]+?<\/span>\)?)/);

        const detailHtml = detailMatch ? detailMatch[1] : (limitText ? `${limitLabel}` : '');



        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

        res.end(JSON.stringify({

          ok: true, code, status: statusText, limit: limitLabel,

          limitNum, limitUnit, detailHtml,

        }));

      } catch(e) {

        res.writeHead(200, { 'Content-Type': 'application/json' });

        res.end(JSON.stringify({ ok: false, error: e.message }));

      }

      return;

    }

    

    if (p === '/api/health') {

      res.writeHead(200, { 'Content-Type': 'application/json' });

      res.end(JSON.stringify({

        ok: true,

        quotes: cache.quotes ? Object.keys(cache.quotes).length : 0,

        navs: cache.fundNavs ? Object.keys(cache.fundNavs).length : 0,

      }));

      return;

    }

    // ====== API: 添加自定义基金 ======

    if (p === '/api/add-fund' && req.method === 'POST') {

      let body = '';

      req.on('data', chunk => body += chunk);

      req.on('end', async () => {

        try {

          const { code, name } = JSON.parse(body);

          if (!code || !code.trim()) {

            res.writeHead(400, { 'Content-Type': 'application/json' });

            res.end(JSON.stringify({ error: '请输入基金代码' }));

            return;

          }

          const cleanCode = code.trim();

          if (FUND_LIST.some(f => f.c === cleanCode)) {

            res.writeHead(400, { 'Content-Type': 'application/json' });

            res.end(JSON.stringify({ error: `基金 ${cleanCode} 已在列表中` }));

            return;

          }

          const market = autoMarket(cleanCode);

          try {

            const testRaw = await httpGet(`http://qt.gtimg.cn/q=${market}${cleanCode}`);

            const testQ = parseTencentLine(testRaw.trim().split('\n')[0]);

            if (!testQ || !testQ.price) {

              res.writeHead(400, { 'Content-Type': 'application/json' });

              res.end(JSON.stringify({ error: `无法获取基金 ${cleanCode} 的行情数据，请确认代码是否正确` }));

              return;

            }

            const fundType = (testQ.tencentType || '').toUpperCase() === 'LOF' ? 'LOF' : 'ETF';

            let realName = name;

            if (!realName) {

              try {

                const fundBody = await httpGet(`http://fundgz.1234567.com.cn/js/${cleanCode}.js`);

                const fundJson = JSON.parse(fundBody.replace(/^jsonpgz\(/, '').replace(/\);$/, ''));

                realName = fundJson.name || cleanCode;

              } catch(e) {

                realName = cleanCode;

              }

            }

            FUND_LIST.push({ c: cleanCode, n: realName, m: market, t: fundType });

            customCodes.add(cleanCode);

            const custom = loadCustomFunds();

            if (!custom.find(f => f.c === cleanCode)) {

              custom.push({ c: cleanCode, n: realName, m: market, t: fundType });

              saveCustomFunds(custom);

            }

            cache.quotes = null;

            cache.fundNavs = null;

            res.writeHead(200, { 'Content-Type': 'application/json' });

            res.end(JSON.stringify({ ok: true, code: cleanCode, name: realName, market }));

          } catch(e) {

            res.writeHead(500, { 'Content-Type': 'application/json' });

            res.end(JSON.stringify({ error: '查询行情失败: ' + e.message }));

          }

        } catch(e) {

          res.writeHead(400, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ error: '请求格式错误' }));

        }

      });

      return;

    }

    

    // ====== API: 获取自定义基金列表 ======

    if (p === '/api/custom-funds') {

      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

      res.end(JSON.stringify({ list: loadCustomFunds() }));

      return;

    }

    

    // ====== API: 删除基金（原生或自定义，永久排除） ======

    if (p === '/api/remove-fund' && req.method === 'POST') {

      let body = '';

      req.on('data', chunk => body += chunk);

      req.on('end', () => {

        try {

          const { code } = JSON.parse(body);

          if (!code) {

            res.writeHead(400, { 'Content-Type': 'application/json' });

            res.end(JSON.stringify({ error: '请输入基金代码' }));

            return;

          }

          const custom = loadCustomFunds().filter(f => f.c !== code);

          saveCustomFunds(custom);

          customCodes.delete(code);

          const excluded = loadExcluded();

          if (!excluded.includes(code)) {

            excluded.push(code);

            saveExcluded(excluded);

          }

          excludedCodes.add(code);

          cache.quotes = null;

          cache.fundNavs = null;

          res.writeHead(200, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ ok: true }));

        } catch(e) {

          res.writeHead(400, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ error: '请求格式错误' }));

        }

      });

      return;

    }

    

    // 巨潮搜索API

    const CNINFO_SEARCH = 'https://www.cninfo.com.cn/new/fulltextSearch/full';

    

    function getSecCode(code) {

      if (!code) return '';

      const c = code.toString().trim();

      const first = parseInt(c[0], 10);

      if ([0,1,2,3].includes(first)) return 'sz' + c;

      return 'sh' + c;

    }

    

    let cninfoCache = { data: null, time: 0 };

    const CNINFO_TTL = 1800000;

    

    async function fetchCninfoAnnouncements() {

      try {

        const url = 'https://www.cninfo.com.cn/new/fulltextSearch/full?searchkey=' + encodeURIComponent('股东回馈活动') +

          '&sdate=&edate=&isfulltext=false&sortName=pubdate&sortType=desc&pageNum=1&pageSize=100';

        const body = await httpGet(url, 10000);

        return JSON.parse(body);

      } catch(e) {

        console.error('巨潮搜索失败:', e.message);

        return null;

      }

    }

    

    // ====== API: 获取股东回馈信息 ======

    if (p === '/api/perks') {

      const perksPath = path.join(__dirname, 'shareholder-perks.json');

      let perks = [];

      if (fs.existsSync(perksPath)) {

        try {

          perks = JSON.parse(fs.readFileSync(perksPath, 'utf-8'));

        } catch(e) { /* ignore */ }

      }

      const today = new Date().toISOString().slice(0, 10);

      for (const p of perks) {

        if (p.endDate && p.endDate < today) p.status = 'ended';

        else if (p.startDate && p.startDate <= today) p.status = 'ongoing';

        else if (p.startDate && p.startDate > today) p.status = 'upcoming';

        else if (p.status !== 'unknown') p.status = 'unknown';

      }

      let cninfoAnnouncements = [];

      const now = Date.now();

      if (!cninfoCache.data || now - cninfoCache.time > CNINFO_TTL) {

        try {

          const result = await fetchCninfoAnnouncements();

          if (result && result.announcements) {

            cninfoCache.data = result.announcements;

            cninfoCache.time = now;

            console.log(`[巨潮] 获取到 ${result.announcements.length} 条股东回馈公告`);

          }

        } catch(e) { /* silent */ }

      }

      if (cninfoCache.data) cninfoAnnouncements = cninfoCache.data;

      

      const filter = url.searchParams.get('filter') || 'all';

      const search = (url.searchParams.get('search') || '').toLowerCase();

      

      const cninfoPerks = cninfoAnnouncements.map(a => {

        const ts = a.announcementTime;

        const date = new Date(ts).toISOString().slice(0, 10);

        // 修复：巨潮数据是GBK编码，需要用相同方式解码中文名称

        var rawName = (a.tileSecName || a.secName || '');

        try { rawName = Buffer.from(rawName, 'binary').toString('utf-8'); } catch(e) {}

        var rawPerkName = (a.shortTitle || a.announcementTitle || '');

        try { rawPerkName = Buffer.from(rawPerkName, 'binary').toString('utf-8'); } catch(e) {}

        return {

          code: a.secCode || '',

          name: rawName.replace(/\s+/g, ''),

          perkName: rawPerkName.replace(/<[^>]+>/g, '').trim(),

          description: '详情见巨潮公告PDF',

          startDate: date,

          endDate: '',

          status: 'unknown',

          minShares: 0,

          source: '巨潮资讯网',

          sourceUrl: `https://www.cninfo.com.cn/new/disclosure/detail?orgId=${a.orgId}&announcementId=${a.announcementId}&announcementTime=${ts}`,

          benefit: '待查阅公告PDF',

          updatedAt: date,

          _fromCninfo: true

        };

      });

      

      const manualCodes = new Set(perks.map(p => p.code));

      const allPerks = [...perks];

      for (const cp of cninfoPerks) {

        if (!manualCodes.has(cp.code)) {

          allPerks.push(cp);

          manualCodes.add(cp.code);

        }

      }

      

      let result = [...allPerks];

      if (filter === 'ongoing') result = result.filter(p => p.status === 'ongoing');

      else if (filter === 'ended') result = result.filter(p => p.status === 'ended');

      else if (filter === 'upcoming') result = result.filter(p => p.status === 'upcoming');

      else if (filter === 'cninfo') result = result.filter(p => p._fromCninfo);

      else if (filter === 'manual') result = result.filter(p => !p._fromCninfo);

      

      if (search) {

        result = result.filter(p =>

          (p.code||'').toLowerCase().includes(search) ||

          (p.name||'').toLowerCase().includes(search) ||

          (p.perkName||'').toLowerCase().includes(search) ||

          (p.description||'').toLowerCase().includes(search)

        );

      }

      

      const order = { ongoing: 0, unknown: 1, upcoming: 2, ended: 3 };

      result.sort((a, b) => {

        const oa = order[a.status] !== undefined ? order[a.status] : 1;

        const ob = order[b.status] !== undefined ? order[b.status] : 1;

        if (oa !== ob) return oa - ob;

        const da = a.updatedAt || '';

        const db = b.updatedAt || '';

        return db.localeCompare(da);

      });

      

      // 获取对应股票的实时行情

      const validCodes = result.filter(p => p.code && p.code.length >= 5).map(p => p.code);

      let quotes = {};

      try {

        if (validCodes.length > 0) {

          const uniqueCodes = [...new Set(validCodes)];

          const quoteCodes = uniqueCodes.map(c => autoMarket(c) + c).join(',');

          const raw = await httpGet('http://qt.gtimg.cn/q=' + quoteCodes);

          for (const line of raw.trim().split('\n')) {

            const q = parseTencentLine(line);

            if (q) quotes[q.code] = q;

          }

        }

      } catch(e) { /* no quotes available */ }

      

      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

      res.end(JSON.stringify({ 

        perks: result, quotes, total: result.length,

        cninfoCount: cninfoAnnouncements.length,

        manualCount: perks.length,

        updated: new Date().toLocaleString('zh-CN')

      }));

      return;

    }

    

    // ====== API: 股东回馈数据管理（保存手动编辑） ======

    if (p === '/api/perks/update' && req.method === 'POST') {

      let body = '';

      req.on('data', chunk => body += chunk);

      req.on('end', () => {

        try {

          const { perks: newPerks } = JSON.parse(body);

          if (!Array.isArray(newPerks)) {

            res.writeHead(400, { 'Content-Type': 'application/json' });

            res.end(JSON.stringify({ error: '数据格式错误' }));

            return;

          }

          const manualOnly = newPerks.filter(p => !p._fromCninfo);

          const perksPath = path.join(__dirname, 'shareholder-perks.json');

          fs.writeFileSync(perksPath, JSON.stringify(manualOnly, null, 2), 'utf-8');

          res.writeHead(200, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ ok: true, count: manualOnly.length, saved: !!manualOnly }));

        } catch(e) {

          res.writeHead(500, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ error: e.message }));

        }

      });

      return;

    }



    // ====== 共享期货品种列表 ======

    const FUTURES_LIST = [

      ['IF', '沪深300股指', 'cffex', '06', '09', '12', '03', '指数', 4000],

      ['IH', '上证50股指', 'cffex', '06', '09', '12', '03', '指数', 2900],

      ['IC', '中证500股指', 'cffex', '06', '09', '12', '03', '指数', 5600],

      ['IM', '中证1000股指', 'cffex', '06', '09', '12', '03', '指数', 5600],

      ['M', '豆粕', 'dce', '07', '08', '09', '12', '元/吨', 3000],

      ['Y', '豆油', 'dce', '09', '10', '11', '12', '元/吨', 7500],

      ['P', '棕榈油', 'dce', '09', '10', '11', '12', '元/吨', 7500],

      ['RM', '菜粕', 'zce', '07', '09', '11', '01', '元/吨', 2500],

      ['OI', '菜油', 'zce', '09', '11', '01', '03', '元/吨', 8000],

      ['CF', '棉花', 'zce', '09', '11', '01', '03', '元/吨', 14000],

      ['SR', '白糖', 'zce', '09', '11', '01', '03', '元/吨', 6000],

      ['A', '豆一', 'dce', '07', '09', '11', '01', '元/吨', 4500],

      ['B', '豆二', 'dce', '07', '08', '09', '12', '元/吨', 3500],

      ['C', '玉米', 'dce', '09', '11', '01', '03', '元/吨', 2400],

      ['CS', '玉米淀粉', 'dce', '07', '09', '11', '01', '元/吨', 2800],

      ['JD', '鸡蛋', 'dce', '06', '07', '08', '09', '元/500kg', 3500],

      ['LH', '生猪', 'dce', '07', '09', '11', '01', '元/吨', 14000],

      ['RB', '螺纹钢', 'shfe', '10', '01', '05', '10', '元/吨', 3200],

      ['HC', '热轧卷板', 'shfe', '10', '01', '05', '10', '元/吨', 3300],

      ['I', '铁矿石', 'dce', '09', '10', '11', '12', '元/吨', 750],

      ['J', '焦炭', 'dce', '09', '10', '11', '12', '元/吨', 2000],

      ['JM', '焦煤', 'dce', '09', '10', '11', '12', '元/吨', 1200],

      ['MA', '甲醇', 'zce', '09', '10', '11', '12', '元/吨', 2300],

      ['SA', '纯碱', 'zce', '09', '10', '11', '12', '元/吨', 1500],

      ['TA', 'PTA', 'zce', '09', '10', '11', '12', '元/吨', 5800],

      ['PF', '短纤', 'zce', '09', '10', '11', '12', '元/吨', 7000],

      ['UR', '尿素', 'zce', '09', '10', '11', '12', '元/吨', 1800],

      ['SM', '硅锰', 'zce', '09', '10', '11', '12', '元/吨', 6500],

      ['SF', '硅铁', 'zce', '09', '10', '11', '12', '元/吨', 7000],

      ['CU', '铜', 'shfe', '07', '08', '09', '10', '元/吨', 75000],

      ['AL', '铝', 'shfe', '07', '08', '09', '10', '元/吨', 20000],

      ['ZN', '锌', 'shfe', '07', '08', '09', '10', '元/吨', 24000],

      ['PB', '铅', 'shfe', '07', '08', '09', '10', '元/吨', 17000],

      ['NI', '镍', 'shfe', '07', '08', '09', '10', '元/吨', 130000],

      ['SN', '锡', 'shfe', '07', '08', '09', '10', '元/吨', 260000],

      ['SS', '不锈钢', 'shfe', '07', '08', '09', '10', '元/吨', 13800],

      ['AU', '黄金', 'shfe', '06', '08', '10', '12', '元/克', 550],

      ['AG', '白银', 'shfe', '06', '08', '10', '12', '元/千克', 7500],

      ['RU', '天然橡胶', 'shfe', '09', '10', '11', '12', '元/吨', 15000],

      ['BU', '沥青', 'shfe', '09', '10', '11', '12', '元/吨', 3500],

      ['FU', '燃油', 'shfe', '09', '10', '11', '12', '元/吨', 3000],

      ['LU', '低硫燃油', 'ine', '07', '08', '09', '10', '元/吨', 4000],

      ['EC', '集运欧线', 'ine', '06', '08', '10', '12', '指数点', 3000],

      ['PG', '液化石油气LPG', 'dce', '07', '08', '09', '10', '元/吨', 4500],

    ];

    (function consolidate() {

      const seen = new Set();

      for (let i = FUTURES_LIST.length - 1; i >= 0; i--) {

        const key = FUTURES_LIST[i][0];

        if (seen.has(key)) FUTURES_LIST.splice(i, 1);

        seen.add(key);

      }

    })();



    // ====== API: 期货基差 ======

    if (p === '/api/futures') {

      (async () => {

        try {

          const symbol = (url.searchParams.get('symbol') || '').toUpperCase();

          const found = FUTURES_LIST.find(f => f[0] === symbol);

          if (!found) {

            res.writeHead(200, { 'Content-Type': 'application/json' });

            res.end(JSON.stringify({

              ok: false,

              error: `品种 ${symbol} 未知`,

              list: FUTURES_LIST.map(f => ({ code: f[0], name: f[1], exchange: f[2], unit: f[6] }))

            }));

            return;

          }

          

          const [fcode, fname, fexch, m1, m2, m3, m4, funit] = found;

          const year = new Date().getFullYear() % 100;

          const monthSymbols = [m1, m2, m3, m4];

          

          async function fetchContract(symbol) {

            try {

              const url = `https://stock.finance.sina.com.cn/futures/api/jsonp.php/var%20a=/InnerFuturesNewService.getDailyKLine?symbol=${symbol}&datalen=2`;

              const raw = await httpGet(url, 6000);

              const json = JSON.parse(raw.replace(/^[^(]+\(|\);$/g, ''));

              if (!json || !json.length) return null;

              const latest = json[json.length - 1];

              const prev = json.length > 1 ? json[json.length - 2] : latest;

              return {

                symbol, date: latest.d, open: parseFloat(latest.o) || 0,

                high: parseFloat(latest.h) || 0, low: parseFloat(latest.l) || 0,

                close: parseFloat(latest.c) || 0,

                prevClose: prev ? parseFloat(prev.c) : (parseFloat(latest.s) || 0),

                volume: parseInt(latest.v) || 0, openInterest: parseInt(latest.p) || 0,

                settle: parseFloat(latest.s) || 0,

              };

            } catch(e) { return null; }

          }

          

          const contracts = await Promise.allSettled(

            monthSymbols.map(m => fetchContract(`${fcode}${year}${m}`))

          );

          

          const currentM = new Date().getMonth() + 1;

          const rawData = [];

          for (let i = 0; i < monthSymbols.length; i++) {

            const r = contracts[i];

            if (r.status === 'fulfilled' && r.value && r.value.close > 0) {

              const c = r.value;

              const contractMonth = parseInt(monthSymbols[i]);

              if (contractMonth + 2 <= currentM) continue;

              rawData.push({

                month: `${fcode}${year}${monthSymbols[i]}`,

                price: c.close, prevClose: c.prevClose,

                change: c.prevClose > 0 ? Math.round((c.close - c.prevClose) / c.prevClose * 10000) / 100 : 0,

                volume: c.volume, openInterest: c.openInterest, date: c.date, monthNum: contractMonth,

              });

            }

          }

          

          rawData.sort((a, b) => {

            let ma = a.monthNum, mb = b.monthNum;

            if (ma < currentM) ma += 12;

            if (mb < currentM) mb += 12;

            return ma - mb;

          });

          

          const data = rawData.map((c, i) => {

            const result = { ...c };

            if (i > 0) {

              const prevPrice = rawData[i - 1].price;

              result.basis = c.price - prevPrice;

              result.basisPct = prevPrice > 0 ? Math.round((c.price - prevPrice) / prevPrice * 10000) / 100 : 0;

            }

            return result;

          });

          

          let basis = null;

          let basisPct = null;

          let isContango = null;

          if (data.length >= 2) {

            const mNums = monthSymbols.map(m => parseInt(m));

            const adjM = mNums.map((m, i) => i > 0 && m < mNums[0] ? m + 12 : m);

            const indices = adjM.map((m, i) => i).sort((a, b) => adjM[a] - adjM[b]);

            const nearIdx = indices.find(i => i < data.length && data[i] != null);

            const farIdx = indices.find(i => i !== nearIdx && i < data.length && data[i] != null);

            if (nearIdx != null && farIdx != null && data[nearIdx] && data[farIdx]) {

              const near = data[nearIdx].price;

              const far = data[farIdx].price;

              basis = far - near;

              basisPct = near > 0 ? Math.round((far - near) / near * 10000) / 100 : 0;

              isContango = far > near;

            }

          }

          

          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

          res.end(JSON.stringify({

            ok: true, code: fcode, name: fname, exchange: fexch, unit: funit,

            contracts: data, basis, basisPct, isContango,

          }));

        } catch(e) {

          res.writeHead(500, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ ok: false, error: e.message }));

        }

      })();

      return;

    }



    // ====== API: 期货基差批量（全品种概览，供 futures.html 使用） ======

    if (p === '/api/futures-basis') {

      (async () => {

        try {

          const results = [];

          const year = new Date().getFullYear() % 100;

          const currentM = new Date().getMonth() + 1;



          async function fetchContractPrice(symbol) {

            try {

              const url = `https://stock.finance.sina.com.cn/futures/api/jsonp.php/var%20a=/InnerFuturesNewService.getDailyKLine?symbol=${symbol}&datalen=2`;

              const raw = await httpGet(url, 5000);

              const json = JSON.parse(raw.replace(/^[^(]+\(|\);$/g, ''));

              if (!json || !json.length) return null;

              const latest = json[json.length - 1];

              const prev = json.length > 1 ? json[json.length - 2] : latest;

              return {

                close: parseFloat(latest.c) || 0,

                prevClose: prev ? parseFloat(prev.c) : 0,

                volume: parseInt(latest.v) || 0,

                openInterest: parseInt(latest.p) || 0,

                date: latest.d,

              };

            } catch(e) { return null; }

          }



          for (const f of FUTURES_LIST) {

            const [fcode, fname, fexch, m1, m2, m3, m4] = f;

            const monthSymbols = [m1, m2, m3, m4];



            const contracts = await Promise.allSettled(

              monthSymbols.map(m => fetchContractPrice(`${fcode}${year}${m}`))

            );



            const rawData = [];

            for (let i = 0; i < monthSymbols.length; i++) {

              const r = contracts[i];

              if (r.status === 'fulfilled' && r.value && r.value.close > 0) {

                const c = r.value;

                const cm = parseInt(monthSymbols[i]);

                if (cm + 2 <= currentM) continue;

                rawData.push({

                  month: `${fcode}${year}${monthSymbols[i]}`,

                  price: c.close,

                  changePct: c.prevClose > 0 ? Math.round((c.close - c.prevClose) / c.prevClose * 10000) / 100 : 0,

                  volume: c.volume,

                  date: c.date,

                  monthNum: cm,

                });

              }

            }



            rawData.sort((a, b) => {

              let ma = a.monthNum, mb = b.monthNum;

              if (ma < currentM) ma += 12;

              if (mb < currentM) mb += 12;

              return ma - mb;

            });



            if (rawData.length >= 2) {

              const main = rawData[0];

              const sub = rawData[1];

              const spread = main.price - sub.price;

              const spreadPct = sub.price > 0 ? Math.round((main.price - sub.price) / sub.price * 10000) / 100 : 0;

              results.push({

                code: fcode,

                name: fname,

                exchange: fexch,

                price: main.price,

                changePct: main.changePct,

                volume: main.volume,

                mainContract: main.month,

                contract2Name: sub.month,

                spread,

                spreadPct,

                isBackwardation: main.price > sub.price,

              });

            } else if (rawData.length === 1) {

              const main = rawData[0];

              results.push({

                code: fcode,

                name: fname,

                exchange: fexch,

                price: main.price,

                changePct: main.changePct,

                volume: main.volume,

                mainContract: main.month,

                contract2Name: '',

                spread: null,

                spreadPct: null,

                isBackwardation: null,

              });

            }

          }



          const exchangeNames = { cffex: '中金所', shfe: '上期所', dce: '大商所', zce: '郑商所', ine: '能源中心' };

          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

          res.end(JSON.stringify({

            ok: true,

            data: results,

            total: results.length,

            updated: new Date().toLocaleString('zh-CN'),

          }));

        } catch(e) {

          res.writeHead(500, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ ok: false, error: e.message }));

        }

      })();

      return;

    }



    // ====== API: 期货品种合约链详情 ======

    if (p.startsWith('/api/futures-detail/')) {

      const symbol = p.replace('/api/futures-detail/', '').toUpperCase();

      (async () => {

        try {

          const found = FUTURES_LIST.find(f => f[0] === symbol);

          if (!found) {

            res.writeHead(200, { 'Content-Type': 'application/json' });

            res.end(JSON.stringify({ ok: false, error: `品种 ${symbol} 未知` }));

            return;

          }



          const [fcode, fname, fexch, m1, m2, m3, m4, funit] = found;

          const year = new Date().getFullYear() % 100;

          const monthSymbols = [m1, m2, m3, m4];



          async function fetchContract(symbol) {

            try {

              const url = `https://stock.finance.sina.com.cn/futures/api/jsonp.php/var%20a=/InnerFuturesNewService.getDailyKLine?symbol=${symbol}&datalen=2`;

              const raw = await httpGet(url, 6000);

              const json = JSON.parse(raw.replace(/^[^(]+\(|\);$/g, ''));

              if (!json || !json.length) return null;

              const latest = json[json.length - 1];

              const prev = json.length > 1 ? json[json.length - 2] : latest;

              return {

                symbol, date: latest.d, open: parseFloat(latest.o) || 0,

                high: parseFloat(latest.h) || 0, low: parseFloat(latest.l) || 0,

                close: parseFloat(latest.c) || 0,

                prevClose: prev ? parseFloat(prev.c) : (parseFloat(latest.s) || 0),

                volume: parseInt(latest.v) || 0, openInterest: parseInt(latest.p) || 0,

                settle: parseFloat(latest.s) || 0,

              };

            } catch(e) { return null; }

          }



          const contracts = await Promise.allSettled(

            monthSymbols.map(m => fetchContract(`${fcode}${year}${m}`))

          );



          const currentM = new Date().getMonth() + 1;

          const rawData = [];

          for (let i = 0; i < monthSymbols.length; i++) {

            const r = contracts[i];

            if (r.status === 'fulfilled' && r.value && r.value.close > 0) {

              const c = r.value;

              const contractMonth = parseInt(monthSymbols[i]);

              if (contractMonth + 2 <= currentM) continue;

              rawData.push({

                month: `${fcode}${year}${monthSymbols[i]}`,

                price: c.close, prevClose: c.prevClose,

                change: c.prevClose > 0 ? Math.round((c.close - c.prevClose) / c.prevClose * 10000) / 100 : 0,

                volume: c.volume, openInterest: c.openInterest, date: c.date, monthNum: contractMonth,

              });

            }

          }



          rawData.sort((a, b) => {

            let ma = a.monthNum, mb = b.monthNum;

            if (ma < currentM) ma += 12;

            if (mb < currentM) mb += 12;

            return ma - mb;

          });



          const data = rawData.map((c, i) => {

            const result = { ...c };

            if (i > 0) {

              const prevPrice = rawData[i - 1].price;

              result.basis = Math.round((c.price - prevPrice) * 100) / 100;

              result.basisPct = prevPrice > 0 ? Math.round((c.price - prevPrice) / prevPrice * 10000) / 100 : 0;

            }

            return result;

          });



          let basis = null, basisPct = null, isContango = null;

          if (data.length >= 2) {

            const near = data[0].price;

            const far = data[1].price;

            basis = Math.round((far - near) * 100) / 100;

            basisPct = near > 0 ? Math.round((far - near) / near * 10000) / 100 : 0;

            isContango = far > near;

          }



          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

          res.end(JSON.stringify({

            ok: true, code: fcode, name: fname, exchange: fexch === 'cffex' ? '中金所' : fexch === 'shfe' ? '上期所' : fexch === 'dce' ? '大商所' : fexch === 'zce' ? '郑商所' : fexch === 'ine' ? '能源中心' : fexch,

            unit: funit, contracts: data, basis, basisPct, isContango,

          }));

        } catch(e) {

          res.writeHead(500, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ ok: false, error: e.message }));

        }

      })();

      return;

    }



    // ====== API: 房价走势数据 ======

    if (p === '/api/house-prices') {

      const city = url.searchParams.get('city') || 'suzhou';

      (async () => {

        try {

          const cityMap = {

            shanghai:'sh', beijing:'bj', shenzhen:'sz', guangzhou:'gz',

            suzhou:'suzhou', hangzhou:'hz', nanjing:'nj', chengdu:'cd',

            wuhan:'wh', chongqing:'cq', tianjin:'tj', xiamen:'xm',

            ningbo:'nb', qingdao:'qd', wuxi:'wx', changsha:'cs',

            zhengzhou:'zz', xian:'xa', hefei:'hf'

          };

          const code = cityMap[city] || city;

          const targetUrl = `https://www.creprice.cn/city/${code}.html?type=forsale&proptype=11&timeType=month`;

          const html = await httpGet(targetUrl, 10000);

          

          let priceData = [];

          const chartMatch = html.match(/chartData\s*=\s*(\[[^\]]+\])/);

          if (chartMatch) {

            try { priceData = JSON.parse(chartMatch[1]); } catch(e) { /* continue */ }

          }

          

          if (!priceData.length) {

            const dataMatch = html.match(/data:\s*(\[[\s\S]{0,5000}\])\s*\n/i);

            if (dataMatch) {

              try {

                const raw = dataMatch[1].replace(/'/g,'"').replace(/,?\s*\]/,']');

                const arr = JSON.parse(raw);

                if (Array.isArray(arr)) {

                  priceData = arr.map((v, i) => {

                    if (typeof v === 'number' || (typeof v === 'string' && !isNaN(parseFloat(v)))) {

                      return { price: typeof v === 'number' ? v : parseFloat(v) };

                    }

                    return null;

                  }).filter(Boolean);

                }

              } catch(e) { /* continue */ }

            }

          }

          

          if (!priceData.length) {

            const tableMatch = html.match(/<table[\s\S]{0,100}?(?:price|avg)[\s\S]{0,5000}?<\/table>/i);

            if (tableMatch) {

              const rows = tableMatch[0].match(/<tr[\s\S]{0,500}?<\/tr>/g);

              if (rows) {

                for (const row of rows) {

                  const cells = row.match(/<t[dh][^>]*>([\s\S]{0,100}?)<\/t[dh]>/g);

                  if (cells && cells.length >= 2) {

                    const cellTexts = cells.map(c => c.replace(/<[^>]+>/g,'').trim());

                    const price = parseFloat(cellTexts[1].replace(/,/g,''));

                    if (!isNaN(price) && price > 100) {

                      priceData.push({ month: cellTexts[0], price });

                    }

                  }

                }

              }

            }

          }

          

          if (!priceData.length) {

            const priceMatches = html.match(/(\d{4})[年/-](\d{1,2})[月]?[^<]{0,20}?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\s*(?:元|￥)/g);

            if (priceMatches) {

              priceData = priceMatches.map(m => {

                const nums = m.match(/(\d{4})[年/-]/);

                const price = parseFloat(m.match(/(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)/)[0].replace(/,/g,''));

                return nums && !isNaN(price) ? { month: nums[1], price } : null;

              }).filter(Boolean);

            }

          }

          

          if (!priceData.length) {

            priceData = getDefaultHouseData(city);

          } else {

            const months = [];

            const now = new Date();

            for (let y = now.getFullYear(); y >= 2016; y--) {

              for (let m = 12; m >= 1; m--) {

                const date = new Date(y, m-1, 1);

                if (date > now) continue;

                months.push(`${y}-${String(m).padStart(2,'0')}`);

              }

            }

            months.sort();

            const priceMap = {};

            const momMap = {};

            

            const momMatches = html.match(/(\d{4}-\d{2})[^<]{0,30}?(-?\d+\.?\d*)%/g);

            if (momMatches) {

              for (const m of momMatches) {

                const parts = m.match(/(\d{4}-\d{2})/);

                const pct = parseFloat(m.match(/(-?\d+\.?\d*)%/)[1]);

                if (parts && !isNaN(pct)) {

                  momMap[parts[1]] = pct;

                }

              }

            }

            

            if (priceData[0] && priceData[0].month) {

              for (const p of priceData) {

                if (p.month && p.price > 0) {

                  priceMap[p.month] = p.price;

                  if (p.mom != null) momMap[p.month] = p.mom;

                }

              }

            }

            

            priceData = months.map(m => {

              const price = priceMap[m];

              if (price && price > 0) {

                return {

                  month: m, price: Math.round(price),

                  mom: momMap[m] != null ? momMap[m] : null,

                };

              }

              return null;

            }).filter(Boolean);

          }

          

          for (let i = 1; i < priceData.length; i++) {

            if (priceData[i].mom == null && priceData[i-1].price > 0) {

              priceData[i].mom = Math.round((priceData[i].price - priceData[i-1].price) / priceData[i-1].price * 10000) / 100;

            }

            if (priceData[i].yoy == null && i >= 12 && priceData[i-12].price > 0) {

              priceData[i].yoy = Math.round((priceData[i].price - priceData[i-12].price) / priceData[i-12].price * 10000) / 100;

            }

          }

          

          const cityNames = {

            shanghai:'上海', suzhou:'苏州', beijing:'北京', shenzhen:'深圳',

            guangzhou:'广州', hangzhou:'杭州', nanjing:'南京', chengdu:'成都',

            wuhan:'武汉', chongqing:'重庆', tianjin:'天津', xiamen:'厦门',

            ningbo:'宁波', qingdao:'青岛', wuxi:'无锡', changsha:'长沙',

            zhengzhou:'郑州', xian:'西安', hefei:'合肥'

          };

          

          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

          res.end(JSON.stringify({

            ok: true, city, cityName: cityNames[city] || city,

            prices: priceData, fetchTime: new Date().toLocaleString('zh-CN'),

          }));

        } catch(e) {

          const priceData = getDefaultHouseData(city);

          const cityNames = {

            shanghai:'上海', suzhou:'苏州', beijing:'北京', shenzhen:'深圳',

            guangzhou:'广州', hangzhou:'杭州', nanjing:'南京', chengdu:'成都',

            wuhan:'武汉', chongqing:'重庆', tianjin:'天津', xiamen:'厦门',

            ningbo:'宁波', qingdao:'青岛', wuxi:'无锡', changsha:'长沙',

            zhengzhou:'郑州', xian:'西安', hefei:'合肥'

          };

          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

          res.end(JSON.stringify({

            ok: true, city, cityName: cityNames[city] || city,

            prices: priceData, fetchTime: new Date().toLocaleString('zh-CN'), note: '内置数据'

          }));

        }

      })();

      return;

    }



    // ====== API: 投资日历 ======

    if (p === '/api/calendar') {

      (async () => {

        try {

          const result = { ipo: [], cb: [], listed: [] };

          const today = new Date().toISOString().slice(0, 10);

          // 并发请求IPO和CB数据

          await Promise.all([

            (async () => {

              try {

                const ipoUrl = 'https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPTA_APP_IPOAPPLY&columns=SECURITY_CODE,SECURITY_NAME,SECURITY_NAME_ABBR,APPLY_CODE,APPLY_DATE,LISTING_DATE,ISSUE_PRICE,PREDICT_ISSUE_PE,ISSUE_NUM,ONLINE_APPLY_UPPER,INDUSTRY_NAME,TRADE_MARKET&pageNumber=1&pageSize=50&sortTypes=-1&sortColumns=APPLY_DATE&source=WEB&client=PC&v=0.1';

                const ipoBody = await new Promise((resolve, reject) => {
                  const mod = require('https');
                  const u = new URL(ipoUrl);
                  mod.get({hostname: u.hostname, path: u.pathname + u.search, headers: {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://data.eastmoney.com/', 'Accept': 'application/json'}, timeout: 15000}, r => {
                    let d = ''; r.setEncoding('utf8'); r.on('data', c => d += c); r.on('end', () => resolve(d));
                  }).on('error', reject).on('timeout', function(){ this.destroy(); reject(new Error('超时')); });
                });

                const ipoData = JSON.parse(ipoBody);

                if (ipoData.result && ipoData.result.data) {

                  for (const item of ipoData.result.data) {

                    const applyDate = (item.APPLY_DATE || '').slice(0, 10) || '';

                    const listingDate = (item.LISTING_DATE || '').slice(0, 10) || '';

                    if (applyDate >= today || (listingDate && listingDate >= today)) {

                      const entry = {

                        code: item.SECURITY_CODE || '',

                        name: item.SECURITY_NAME || item.SECURITY_NAME_ABBR || '',

                        apply_code: item.APPLY_CODE || '',

                        apply_date: applyDate,

                        listing_date: listingDate,

                        price: item.ISSUE_PRICE || '',

                        pe: item.PREDICT_ISSUE_PE || '',

                        industry: item.INDUSTRY_NAME || '',

                        apply_upper: item.ONLINE_APPLY_UPPER || 0,

                        trade_market: item.TRADE_MARKET || ''

                      };

                      result.ipo.push(entry);

                      if (listingDate && listingDate >= today) {

                        result.listed.push({

                          code: entry.code,

                          name: entry.name,

                          date: listingDate,

                          price: entry.price,

                          trade_market: entry.trade_market

                        });

                      }

                    }

                  }

                }

              } catch(e) { console.error('IPO fetch error:', e.message); }

            })(),

            (async () => {

              try {

                const cbUrl = 'https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_BOND_CB_LIST&columns=SECURITY_CODE,SECURITY_NAME_ABBR,DELIST_DATE,EXPIRE_DATE,NOTICE_DATE_HS&pageNumber=1&pageSize=500&sortTypes=-1&sortColumns=EXPIRE_DATE&source=WEB&client=PC&v=0.1';

                const cbBody = await new Promise((resolve, reject) => {
                  const mod = require('https');
                  const u = new URL(cbUrl);
                  mod.get({hostname: u.hostname, path: u.pathname + u.search, headers: {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://data.eastmoney.com/kzz/', 'Accept': 'application/json'}, timeout: 15000}, r => {
                    let d = ''; r.setEncoding('utf8'); r.on('data', c => d += c); r.on('end', () => resolve(d));
                  }).on('error', reject).on('timeout', function(){ this.destroy(); reject(new Error('超时')); });
                });

                const cbData = JSON.parse(cbBody);

                if (cbData.result && cbData.result.data) {

                  for (const item of cbData.result.data) {

                    const expire = (item.EXPIRE_DATE || '').slice(0, 10);

                    const delist = (item.DELIST_DATE || '').slice(0, 10);

                    const name = item.SECURITY_NAME_ABBR || '';

                    const code = item.SECURITY_CODE || '';

                    if (expire && expire >= today) {

                      const d = Math.floor((new Date(expire) - new Date()) / 86400000);

                      if (d >= 0 && d <= 90) result.cb.push({ code, name, event_type: '到期', date: expire });

                    }

                    if (delist && delist >= today) {

                      const d = Math.floor((new Date(delist) - new Date()) / 86400000);

                      if (d >= 0 && d <= 30) result.cb.push({ code, name, event_type: '最后交易日', date: delist });

                    }

                  }

                  const seen = new Set();

                  result.cb = result.cb.filter(c => {

                    const key = c.code + '|' + c.event_type;

                    if (seen.has(key)) return false;

                    seen.add(key);

                    return true;

                  });

                  result.cb.sort((a, b) => a.date.localeCompare(b.date));

                }

              } catch(e) { console.error('CB fetch error:', e.message); }

            })()

          ]);

          result.listed.sort((a, b) => a.date.localeCompare(b.date));

          result.ipo.sort((a, b) => a.apply_date.localeCompare(b.apply_date));

          res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' });

          res.end(JSON.stringify(result));

        } catch(e) {

          res.writeHead(500, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ error: e.message }));

        }

      })();

      return;

    }    // ====== API: 黑名单股票池 ======

    if (p === '/api/blacklist') {

      const blPath = path.join(__dirname, 'blacklist-stocks.json');

      let list = [];

      if (fs.existsSync(blPath)) {

        try { list = JSON.parse(fs.readFileSync(blPath, 'utf-8')); } catch(e) { list = []; }

      }

      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

      res.end(JSON.stringify({ ok: true, list, total: list.length }));

      return;

    }



    // ====== API: 增加黑名单股票 ======

    if (p === '/api/blacklist/add' && req.method === 'POST') {

      let body = '';

      req.on('data', chunk => body += chunk);

      req.on('end', () => {

        try {

          const { code, name, reason } = JSON.parse(body);

          if (!code || !code.trim()) {

            res.writeHead(400, { 'Content-Type': 'application/json' });

            res.end(JSON.stringify({ error: '请输入股票代码' }));

            return;

          }

          const cleanCode = code.trim();

          const blPath = path.join(__dirname, 'blacklist-stocks.json');

          let list = [];

          if (fs.existsSync(blPath)) {

            try { list = JSON.parse(fs.readFileSync(blPath, 'utf-8')); } catch(e) { list = []; }

          }

          if (list.some(s => s.code === cleanCode)) {

            res.writeHead(400, { 'Content-Type': 'application/json' });

            const msg = '股票 ' + cleanCode + ' 已在黑名单中';

            res.end(JSON.stringify({ error: msg }));

            return;

          }

          const newStock = { code: cleanCode, name: name || '', reason: reason || '' };

          list.push(newStock);

          fs.writeFileSync(blPath, JSON.stringify(list, null, 2), 'utf-8');

          res.writeHead(200, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ ok: true, stock: newStock, total: list.length }));

        } catch(e) {

          res.writeHead(400, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ error: '请求格式错误: ' + e.message }));

        }

      });

      return;

    }



    // ====== API: 删除黑名单股票 ======

    if (p === '/api/blacklist/remove' && req.method === 'POST') {

      let body = '';

      req.on('data', chunk => body += chunk);

      req.on('end', () => {

        try {

          const { code } = JSON.parse(body);

          if (!code) {

            res.writeHead(400, { 'Content-Type': 'application/json' });

            res.end(JSON.stringify({ error: '请输入股票代码' }));

            return;

          }

          const blPath = path.join(__dirname, 'blacklist-stocks.json');

          let list = [];

          if (fs.existsSync(blPath)) {

            try { list = JSON.parse(fs.readFileSync(blPath, 'utf-8')); } catch(e) { list = []; }

          }

          const newList = list.filter(s => s.code !== code);

          if (newList.length === list.length) {

            res.writeHead(404, { 'Content-Type': 'application/json' });

            const msg = '股票 ' + code + ' 不在黑名单中';

            res.end(JSON.stringify({ error: msg }));

            return;

          }

          fs.writeFileSync(blPath, JSON.stringify(newList, null, 2), 'utf-8');

          res.writeHead(200, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ ok: true, total: newList.length }));

        } catch(e) {

          res.writeHead(400, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ error: '请求格式错误: ' + e.message }));

        }

      });

      return;

    }



    // ====== API: 查询股票风险信息（审计意见、证监会立案、ST风险） ======

    if (p.startsWith('/api/stock-risk/')) {

      const code = p.replace('/api/stock-risk/', '');

      (async () => {

        try {

          const result = {

            code: code, name: '',

            auditOpinion: null, auditOpinionDesc: null,

            csrcCase: null, csrcCaseDesc: null,

            stRisk: null, stRiskDesc: null,

            stDetail: null,

            inBlacklist: false, blacklistReason: null

          };



          const first = parseInt(code[0], 10);

          const market = [0,1,2,3].includes(first) ? 'sz' : 'sh';

          const secCode = market + code;

          const emCode = code + '.' + market.toUpperCase();



          // 1. 获取股票名称和状态

          var stockName = '';

          var stockPrice = 0;

          try {

            var qRaw = await httpGet('http://qt.gtimg.cn/q=' + secCode, 4000);

            var qLine = parseTencentLine(qRaw.trim().split('\n')[0]);

            if (qLine && qLine.name) {

              result.name = qLine.name;

              stockName = qLine.name;

              stockPrice = qLine.price || 0;

            }

          } catch(e) { /* ignore */ }



          // 2. 查是否在黑名单中

          try {

            var blPath = path.join(__dirname, 'blacklist-stocks.json');

            if (fs.existsSync(blPath)) {

              var blList = JSON.parse(fs.readFileSync(blPath, 'utf-8'));

              var foundBl = blList.find(function(s) { return s.code === code; });

              if (foundBl) {

                result.inBlacklist = true;

                result.blacklistReason = foundBl.reason || '在黑名单中';

              }

            }

          } catch(e) { /* ignore */ }



          // ======== 3. 审计意见 ========

          // 从 MAINFINADATA 没有审计列，尝试从新浪F10（GBK）抓取

          var auditFound = false;

          try {

            // 尝试从东方财富获取审计意见（通过搜索"审计意见"关键词）

            var f10Url = 'https://vip.stock.finance.sina.com.cn/corp/go.php/vFD_BalanceSheet/stockid/' + code + '/ctrl/part/displaytype/4.phtml';

            var f10Html = await httpGet(f10Url, 6000);

            

            if (f10Html.indexOf('标准无保留') >= 0) {

              result.auditOpinion = '标准无保留审计意见';

              result.auditOpinionDesc = '最近一期审计报告为标准无保留意见';

              auditFound = true;

            } else {

              var kwList = ['非标准', '保留意见', '否定意见', '无法表示意见', '带强调事项段', '非标'];

              for (var ki = 0; ki < kwList.length; ki++) {

                if (f10Html.indexOf(kwList[ki]) >= 0) {

                  result.auditOpinion = '非标准审计意见';

                  result.auditOpinionDesc = '财务报告审计存在"' + kwList[ki] + '"';

                  auditFound = true;

                  break;

                }

              }

            }

            

            // 如果新浪没有，尝试巨潮搜索

            if (!auditFound) {

              // 增大搜索量，获取更多结果以便分析审计意见类型

              var auditSearchUrl = 'https://www.cninfo.com.cn/new/fulltextSearch/full?searchkey=' + encodeURIComponent(code + ' 审计报告') + '&sdate=&edate=&isfulltext=false&sortName=pubdate&sortType=desc&pageNum=1&pageSize=8';

              var auditSearchRes = await httpGet(auditSearchUrl, 6000);

              try {

                var auditSearchJson = JSON.parse(auditSearchRes);

                if (auditSearchJson.announcements && auditSearchJson.announcements.length > 0) {

                  var auditTitles = [];

                  for (var ai = 0; ai < auditSearchJson.announcements.length; ai++) {

                    var aTitleRaw = (auditSearchJson.announcements[ai].announcementTitle || '');

                    try { aTitleRaw = Buffer.from(aTitleRaw, 'binary').toString('utf-8'); } catch(e) {}

                    var aTitle = aTitleRaw.replace(/<[^>]+>/g, '').trim();

                    if (aTitle.indexOf('审计') >= 0 && aTitle.indexOf('报告') >= 0) {

                      auditTitles.push(aTitle);

                    }

                  }

                  if (auditTitles.length > 0) {

                    // 分析所有公告标题，识别审计意见类型

                    var nonStandardKws = ['非标准', '保留意见', '否定意见', '无法表示意见', '带强调事项', '持续经营', '非标', '带与', '保留审计意见'];

                    var isNonStandard = false;

                    var matchedKws = [];

                    for (var ati = 0; ati < auditTitles.length; ati++) {

                      for (var nk = 0; nk < nonStandardKws.length; nk++) {

                        if (auditTitles[ati].indexOf(nonStandardKws[nk]) >= 0) {

                          isNonStandard = true;

                          if (matchedKws.indexOf(nonStandardKws[nk]) < 0) {

                            matchedKws.push(nonStandardKws[nk]);

                          }

                        }

                      }

                    }

                    if (isNonStandard) {

                      result.auditOpinion = '非标准审计意见';

                      result.auditOpinionDesc = '存在非标准审计意见: ' + matchedKws.join('、') + '。相关公告: ' + auditTitles.slice(0, 2).join(' | ');

                    } else {

                      result.auditOpinion = '标准无保留审计意见';

                      result.auditOpinionDesc = '最近一期审计报告公告标题: ' + auditTitles[0];

                    }

                    auditFound = true;

                  }

                }

              } catch(e) { /* ignore */ }

            }

          } catch(e) { /* ignore */ }



          if (!auditFound) {

            result.auditOpinion = '未获取到审计信息';

            result.auditOpinionDesc = '无法从公开数据源获取该股票审计意见。建议查阅巨潮资讯网最新年报PDF';

          }



          // ======== 4. 证监会立案/处罚 ========

          

          var csrcFound = false;

          try {

            // 从巨潮搜索"立案"、"处罚"等关键词

            var searchTerms = [code + ' 立案', code + ' 处罚', code + ' 调查', code + ' 警示'];

            for (var sti = 0; sti < searchTerms.length && !csrcFound; sti++) {

              var searchUrl = 'https://www.cninfo.com.cn/new/fulltextSearch/full?searchkey=' + encodeURIComponent(searchTerms[sti])

                + '&sdate=&edate=&isfulltext=false&sortName=pubdate&sortType=desc&pageNum=1&pageSize=10';

              

              var searchRes = await httpGet(searchUrl, 6000);

              

              try {

                // CNINFO returns UTF-8 JSON, but httpGet reads as binary causing garbled text

                // Fix by re-decoding through Buffer

                var searchJson = JSON.parse(searchRes);

                

                if (searchJson.announcements && searchJson.announcements.length > 0) {

                  for (var asi = 0; asi < searchJson.announcements.length; asi++) {

                    var aShortTitle = (searchJson.announcements[asi].announcementTitle || '');

                    // Use Buffer to correct the binary encoding issue

                    var cleanTitle = aShortTitle;

                    try {

                      cleanTitle = Buffer.from(aShortTitle, 'binary').toString('utf-8');

                    } catch(e) {}

                    if (cleanTitle.indexOf('<') >= 0) {

                      cleanTitle = cleanTitle.replace(/<[^>]+>/g, '').trim();

                    }

                    var aTitleLower = cleanTitle.toLowerCase();

                    

                    if (aTitleLower.indexOf('立案') >= 0 || aTitleLower.indexOf('行政处罚') >= 0 || aTitleLower.indexOf('处罚决定') >= 0) {

                      

                      var date = new Date(searchJson.announcements[asi].announcementTime).toISOString().slice(0, 10);

                      result.csrcCase = '有立案/处罚相关公告';

                      result.csrcCaseDesc = cleanTitle + '（' + date + '）';

                      csrcFound = true;

                      break;

                    }

                  }

                  if (!csrcFound) {

                    for (var asi2 = 0; asi2 < searchJson.announcements.length; asi2++) {

                      var a2ShortTitle = (searchJson.announcements[asi2].announcementTitle || '');

                      try { a2ShortTitle = Buffer.from(a2ShortTitle, 'binary').toString('utf-8'); } catch(e) {}

                      if (a2ShortTitle.indexOf('<') >= 0) {

                        a2ShortTitle = a2ShortTitle.replace(/<[^>]+>/g, '').trim();

                      }

                      var a2TitleLower = a2ShortTitle.toLowerCase();

                      if (a2TitleLower.indexOf('调查') >= 0 || a2TitleLower.indexOf('警示') >= 0 || a2TitleLower.indexOf('监管') >= 0) {

                        var date2 = new Date(searchJson.announcements[asi2].announcementTime).toISOString().slice(0, 10);

                        result.csrcCase = '有调查/警示/监管相关公告';

                        result.csrcCaseDesc = a2ShortTitle + '（' + date2 + '）';

                        csrcFound = true;

                        break;

                      }

                    }

                  }

                }

              } catch(e) { /* ignore */ }

            }

          } catch(e) { /* ignore */ }



          if (!csrcFound) {

            result.csrcCase = '暂未发现立案/处罚公告';

            result.csrcCaseDesc = '在巨潮资讯网未检索到该公司立案、处罚等公告';

          }



          // ======== 5. ST风险（基于财务指标） ========

          var stFound = false;

          var stTriggerList = [];



          // 5a. 检查名称是否已ST

          if (stockName) {

            if (stockName.indexOf('*ST') >= 0) {

              result.stRisk = '已*ST（退市风险警示）';

              result.stRiskDesc = '当前名称: ' + stockName;

              stFound = true;

            } else if (stockName.indexOf('ST') >= 0) {

              result.stRisk = '已ST（其他风险警示）';

              result.stRiskDesc = '当前名称: ' + stockName;

              stFound = true;

            } else if (stockName.indexOf('退') >= 0) {

              result.stRisk = '已进入退市整理期';

              result.stRiskDesc = '当前名称: ' + stockName;

              stFound = true;

            }

          }



          // 5b. 从东方财富获取财务数据

          try {

            var finUrl = 'https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_FINANCE_MAINFINADATA'

              + '&columns=SECUCODE,SECURITY_NAME_ABBR,REPORT_DATE,PARENTNETPROFIT,TOTALOPERATEREVE,BPS'

              + '&filter=(SECUCODE=%22' + emCode + '%22)'

              + '&pageNumber=1&pageSize=4&sortTypes=-1&sortColumns=REPORT_DATE';

            var finRes = await httpGet(finUrl, 6000);

            try {

              var finJson = JSON.parse(finRes);

              if (finJson.result && finJson.result.data && finJson.result.data.length > 0) {

                var latest = finJson.result.data[0];

                var prev = finJson.result.data.length > 1 ? finJson.result.data[1] : null;



                var revenue = latest.TOTALOPERATEREVE;

                var netProfit = latest.PARENTNETPROFIT;

                var bps = latest.BPS;

                var reportDate = (latest.REPORT_DATE || '').slice(0, 10);



                // 净资产为负判断（BPS < 0）

                if (bps !== null && bps !== undefined && bps < 0) {

                  stTriggerList.push('净资产为负（每股净资产' + Math.round(bps * 100) / 100 + '元）');

                }



                // 营收不足1亿且亏损

                if (revenue !== null && revenue !== undefined && netProfit !== null && netProfit !== undefined) {

                  var revYi = revenue / 100000000;

                  var npYi = netProfit / 100000000;



                  if (revYi < 1 && npYi < 0) {

                    stTriggerList.push('营收不足1亿（' + Math.round(revYi * 100) / 100 + '亿）且净利润亏损' + Math.round(npYi * 100) / 100 + '亿');

                  } else if (npYi < 0) {

                    stTriggerList.push('净利润亏损' + Math.round(-npYi * 100) / 100 + '亿');

                  }



                  // 连续亏损判断

                  if (prev && prev.PARENTNETPROFIT !== null && prev.PARENTNETPROFIT !== undefined && prev.PARENTNETPROFIT < 0 && netProfit < 0) {

                    if (stTriggerList.length === 0 || stTriggerList[stTriggerList.length - 1].indexOf('连续亏损') < 0) {

                      stTriggerList.push('连续亏损（近两期净利润均为负）');

                    }

                  }



                  // 正常情况也要显示财务数据

                  if (!stFound) {

                    result.stDetail = {

                      revenue: Math.round(revYi * 100) / 100 + '亿',

                      netProfit: Math.round(npYi * 100) / 100 + '亿',

                      bps: bps !== null ? Math.round(bps * 100) / 100 + '元' : '-',

                      reportDate: reportDate

                    };

                    if (stTriggerList.length === 0) {

                      result.stDetail.status = '正常';

                    }

                  }

                }

              }

            } catch(e) { /* ignore */ }

          } catch(e) { /* ignore */ }



          if (stTriggerList.length > 0) {

            if (!stFound) {

              result.stRisk = '存在ST触发风险';

              result.stRiskDesc = stTriggerList.join('；');

              stFound = true;

            }

          }



          if (!stFound) {

            // 有财务数据且无触发 => 正常

            if (result.stDetail && result.stDetail.status === '正常') {

              result.stRisk = '暂未发现ST触发条件';

              result.stRiskDesc = '营收' + result.stDetail.revenue + '，净利润' + result.stDetail.netProfit + '（' + result.stDetail.reportDate + '）';

            } else if (result.name) {

              result.stRisk = '暂未发现ST标记';

              result.stRiskDesc = '当前名称' + result.name + '未带ST标记';

            } else {

              result.stRisk = '暂未获取到财务数据';

              result.stRiskDesc = '无法获取该股票的财务指标来判断ST风险';

            }

          }



          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

          res.end(JSON.stringify({ ok: true, data: result }));

        } catch(e) {

          res.writeHead(500, { 'Content-Type': 'application/json' });

          res.end(JSON.stringify({ ok: false, error: e.message }));

        }

      })();

      return;

    }



    // ====== 静态文件服务 ======

    let fp = path.join(__dirname, 'public', p === '/' ? 'index.html' : p);

    const ext = path.extname(fp);

    const content = fs.readFileSync(fp);

    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream', 'Cache-Control': ext === '.html' ? 'no-cache' : 'max-age=3600' });

    res.end(content);

  } catch(e) {

    if (p.startsWith('/api/')) {

      res.writeHead(500, { 'Content-Type': 'application/json' });

      res.end(JSON.stringify({ error: e.message }));

    } else {

      res.writeHead(404);

      res.end('Not Found');

    }

  }

});



server.listen(PORT, () => {

  console.log('\n' + '='.repeat(50));

  console.log('  \x1b[93m\xf0\x9f\x90\xb7 猪猪基金 折溢价查询工具 v2\x1b[0m');

  console.log('  ' + '='.repeat(50));

  console.log('  \x1b[92m\xf0\x9f\x93\x8d http://localhost:' + PORT + '\x1b[0m');

  console.log('  \x1b[92m\xf0\x9f\x93\x8a 黑名单股票池: http://localhost:' + PORT + '/blacklist.html\x1b[0m');

  console.log('  ' + '='.repeat(50) + '\n');

});
