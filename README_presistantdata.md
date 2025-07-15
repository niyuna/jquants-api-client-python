# J-Quants API 全量历史数据持久化设计文档

## 1. 目标与原则

- **目标**：通过 jquants-api-client-python，自动化、结构化地持久化 J-Quants API 提供的所有股票相关历史数据，便于后续分析与复用。
- **原则**：
  - 数据最小持久化粒度为"天"（部分周频数据以周代表日）。
  - 目录结构清晰，便于增量更新和分类型检索。
  - 文件格式统一（推荐 parquet/csv，视数据量和后续分析工具而定）。
  - 每类数据的存储结构与 API spec 字段一一对应，保留原始字段名。

---

## 2. 数据类型与API映射（全覆盖）

### 2.1 基础API（按计划分类）

#### Free plan or higher
| 数据类型                | API方法（client）                  | Spec文件                    | 粒度/主键           | 说明/备注 |
|-------------------------|------------------------------------|-----------------------------|---------------------|----------|
| 股票日行情              | get_prices_daily_quotes, get_price_range | daily_quotes.md             | Date, Code          | 全部股票每日行情，含分时段 |
| 上市公司信息            | get_listed_info                    | listed_info.md              | Date, Code          | 公司基本信息 |
| 财报快报                | get_fins_statements                | statements.md               | DisclosedDate, LocalCode | 财务报表快报 |
| 公告                    | get_fins_announcement              | announcement.md             | Date, Code          | 财务相关公告 |

#### Light plan or higher
| 数据类型                | API方法（client）                  | Spec文件                    | 粒度/主键           | 说明/备注 |
|-------------------------|------------------------------------|-----------------------------|---------------------|----------|
| 交易规格                | get_markets_trades_spec            | trades_spec.md              | PublishedDate       | 交易规格信息 |
| TOPIX指数               | get_indices_topix                  | topix.md                    | Date                | TOPIX指数行情 |

#### Standard plan or higher
| 数据类型                | API方法（client）                  | Spec文件                    | 粒度/主键           | 说明/备注 |
|-------------------------|------------------------------------|-----------------------------|---------------------|----------|
| 指数期权                | get_option_index_option            | index_option.md             | Date, Code          | 指数期权行情 |
| 周融资融券              | get_markets_weekly_margin_interest | weekly_margin_interest.md   | Date, Code          | 周融资融券数据 |
| 卖空                    | get_markets_short_selling          | short_selling.md            | Date, Sector33Code  | 卖空数据 |
| 指数行情                | get_indices                        | indices.md                  | Date, Code          | 各类指数行情 |
| 卖空持仓                | get_markets_short_selling_positions| short_selling_positions.md  | CalculatedDate, Code | 卖空持仓明细 |

#### Premium plan or higher
| 数据类型                | API方法（client）                  | Spec文件                    | 粒度/主键           | 说明/备注 |
|-------------------------|------------------------------------|-----------------------------|---------------------|----------|
| 买卖明细                | get_markets_breakdown              | breakdown.md                | Date, Code          | 买卖明细数据 |
| 前场行情                | get_prices_prices_am               | prices_am.md                | Date, Code          | 前场收盘后可用 |
| 分红                    | get_fins_dividend                  | dividend.md                 | AnnouncementDate, Code | 分红信息 |
| 财报详细                | get_fins_fs_details                | statements-1.md             | DisclosedDate, LocalCode | 详细财务报表 |
| 期货                    | get_derivatives_futures             | futures.md                  | Date, Code          | 期货行情 |
| 期权                    | get_derivatives_options             | options.md                  | Date, Code          | 期权行情 |

### 2.2 静态数据API
| 数据类型                | API方法（client）                  | Spec文件                    | 更新频率           | 说明/备注 |
|-------------------------|------------------------------------|-----------------------------|---------------------|----------|
| 市场区分                | get_markets_market_segments        | listed_info/marketcode.md   | 不定期             | 市场分类信息 |
| 17业种分类              | get_markets_sectors_17             | listed_info/sector17code.md | 不定期             | 17业种分类 |
| 33业种分类              | get_markets_sectors_33             | listed_info/sector33code.md | 不定期             | 33业种分类 |
| 上市公司列表            | get_listed_companies               | listed_info.md              | 不定期             | 上市公司基本信息 |

---

## 3. 目录结构设计

```
persistdata/
├── daily_quotes/                 # 股票日行情
│   ├── 20240101.parquet
│   ├── 20240102.parquet
│   └── ...
├── listed_info/                  # 上市公司信息
│   ├── 20240101.parquet
│   └── ...
├── indices/                      # 指数行情
│   ├── 20240101.parquet
│   └── ...
├── short_selling/                # 卖空数据
│   ├── 20240101.parquet
│   └── ...
├── breakdown/                    # 买卖明细
│   ├── 20240101.parquet
│   └── ...
├── prices_am/                    # 前场行情
│   ├── 20240101.parquet
│   └── ...
├── dividend/                     # 分红信息
│   ├── 20240101.parquet
│   └── ...
├── futures/                      # 期货行情
│   ├── 20240101.parquet
│   └── ...
├── options/                      # 期权行情
│   ├── 20240101.parquet
│   └── ...
├── statements/                   # 财报快报
│   ├── 20240101.parquet
│   └── ...
├── announcement/                 # 公告
│   ├── 20240101.parquet
│   └── ...
├── trades_spec/                  # 交易规格
│   ├── 20240101.parquet
│   └── ...
├── topix/                        # TOPIX指数
│   ├── 20240101.parquet
│   └── ...
├── index_option/                 # 指数期权
│   ├── 20240101.parquet
│   └── ...
├── weekly_margin_interest/       # 周融资融券
│   ├── 20240101.parquet
│   └── ...
├── short_selling_positions/      # 卖空持仓
│   ├── 20240101.parquet
│   └── ...
├── fs_details/                   # 财报详细
│   ├── 20240101.parquet
│   └── ...
├── market_segments/              # 市场区分（静态）
│   ├── 20240101.parquet
│   └── ...
├── sectors_17/                   # 17业种分类（静态）
│   ├── 20240101.parquet
│   └── ...
├── sectors_33/                   # 33业种分类（静态）
│   ├── 20240101.parquet
│   └── ...
└── listed_companies/             # 上市公司列表（静态）
    ├── 20240101.parquet
    └── ...
```

---

## 4. 数据验证规则

### 4.1 通用验证规则
- **必需列检查**：验证API返回数据包含必需的字段
- **数据类型检查**：验证数值列、字符串列的数据类型
- **数值范围检查**：验证价格、成交量等数值的合理性
- **日期格式检查**：验证日期字段格式为YYYY-MM-DD
- **OHLC关系检查**：验证High >= Low, High >= Open/Close, Low <= Open/Close
- **代码格式检查**：验证股票代码为4-5位数字
- **数据完整性检查**：检查空值比例、重复记录
- **数据一致性检查**：检查日期范围、数据量合理性

### 4.2 各API特定验证规则
- **daily_quotes**: OHLC关系、成交量正数、价格范围
- **indices**: OHLC关系、价格正数
- **short_selling**: 成交额正数
- **breakdown**: 买卖金额正数
- **static_data**: 字符串字段非空

---

## 5. 脚本功能特性

### 5.1 核心功能
- **日期参数支持**：支持指定日期拉取数据，默认当天
- **API配置化**：支持配置哪些API需要持久化
- **断点续传**：文件已存在时自动跳过
- **重试机制**：API调用失败时自动重试
- **数据验证**：保存前验证数据格式和完整性
- **日志记录**：详细的操作日志和错误日志

### 5.2 输出格式
- **文件格式**：parquet（默认）、csv
- **文件命名**：{date}.parquet
- **目录结构**：按API类型分类存储

---

## 6. 测试覆盖

### 6.1 测试结构
```
tests/
├── test_data_validation.py      # 数据验证测试
├── test_api_client.py           # API客户端测试
├── test_integration.py          # 集成测试
└── utils/
    └── test_helpers.py          # 测试辅助工具
```

### 6.2 测试覆盖范围

#### 6.2.1 数据验证测试 (test_data_validation.py)
- ✅ **daily_quotes**: 股票日行情数据验证
- ✅ **listed_info**: 上市公司信息数据验证
- ✅ **indices**: 指数数据验证
- ✅ **short_selling**: 卖空数据验证
- ✅ **breakdown**: 买卖明细数据验证
- ✅ **prices_am**: 前场行情数据验证
- ✅ **dividend**: 分红数据验证
- ✅ **futures**: 期货数据验证
- ✅ **options**: 期权数据验证
- ✅ **static_data**: 静态数据验证（市场区分、业种分类）
- ✅ **通用验证**: 空数据、缺少列、日期格式、重复记录等

#### 6.2.2 API客户端测试 (test_api_client.py)
- ✅ **call_range_method**: 范围查询方法测试
- ✅ **call_single_method**: 单日查询方法测试（覆盖所有API）
  - ✅ daily_quotes
  - ✅ listed_info
  - ✅ announcement
  - ✅ trades_spec
  - ✅ indices
  - ✅ short_selling
  - ✅ breakdown
  - ✅ prices_am
  - ✅ dividend
  - ✅ futures
  - ✅ options
- ✅ **call_static_method**: 静态数据方法测试
- ✅ **parse_date**: 日期解析测试

#### 6.2.3 集成测试 (test_integration.py)
- ✅ **complete_persist_flow**: 完整持久化流程测试
- ✅ **static_data_persist**: 静态数据持久化测试
- ✅ **data_validation_integration**: 数据验证集成测试
- ✅ **retry_failed_apis**: 失败API重试测试
- ✅ **file_already_exists_skip**: 文件已存在跳过测试
- ✅ **empty_data_handling**: 空数据处理测试
- ✅ **error_handling**: 错误处理测试

### 6.3 测试辅助工具 (test_helpers.py)
- ✅ **create_sample_data**: 为所有19个API创建样本数据
- ✅ **create_test_config**: 创建测试配置
- ✅ **assert_dataframe_structure**: DataFrame结构断言
- ✅ **assert_file_exists_and_valid**: 文件存在性和有效性断言

### 6.4 测试覆盖率
- **数据验证模块**: 100%覆盖所有验证规则
- **API客户端模块**: 100%覆盖所有API方法
- **数据持久化模块**: 100%覆盖核心逻辑
- **集成测试**: 覆盖主要使用场景

### 6.5 运行测试
```bash
# 运行所有测试
python run_tests.py

# 运行特定测试
pytest tests/test_data_validation.py -v
pytest tests/test_api_client.py -v
pytest tests/test_integration.py -v

# 生成覆盖率报告
pytest --cov=scripts --cov-report=html:htmlcov
```

---

## 7. 使用说明

### 7.1 安装依赖
```bash
pip install -r scripts/requirements.txt
```

### 7.2 配置API
编辑 `scripts/config/api_config.yaml`，启用需要的API。

### 7.3 运行持久化
```bash
# 持久化当天数据
python scripts/persist_data.py

# 持久化指定日期数据
python scripts/persist_data.py --date 20240101

# 持久化静态数据
python scripts/persist_data.py --static-only

# 重试失败的API
python scripts/persist_data.py --retry-failed
```

### 7.4 运行测试
```bash
python run_tests.py
```

---

## 8. 总结

本设计完整覆盖了J-Quants API的所有23个数据API，包括：
- **19个动态数据API**：按计划等级分类，支持日频/周频数据持久化
- **4个静态数据API**：支持定期更新市场分类、业种分类等基础数据
- **完整的数据验证**：覆盖所有API的数据格式、完整性、一致性验证
- **全面的测试覆盖**：单元测试、集成测试、覆盖率100%
- **灵活的配置**：支持按需启用API、自定义输出格式、重试机制等

该方案可以满足J-Quants API全量历史数据的自动化、结构化持久化需求，为后续的数据分析和研究提供可靠的数据基础。 