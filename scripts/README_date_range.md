# 日期范围数据持久化使用说明（优化版）

## 概述

本工具支持对指定日期范围执行批量数据持久化，**优化版新增了Range API支持**，可以大幅减少API调用次数，避免触发J-Quants API的rate limiting。

## 主要优化

### 1. Range API批量调用
- **自动识别**：自动识别支持range的API（如`daily_quotes`, `statements`, `options`等）
- **批量获取**：使用range调用一次性获取多天数据，然后按日期分割保存
- **大幅减少API调用**：对于7天的数据，range API从7次调用减少到1次调用

### 2. 智能Chunk处理
- **可配置chunk大小**：默认7天，可根据需要调整
- **避免单次请求过大**：将长日期范围分割成小块处理
- **并行处理**：每个chunk可以并行处理

### 3. API调用统计
- **实时统计**：显示节省的API调用次数
- **效率对比**：显示优化前后的效率提升

## 使用方法

### 1. Python脚本方式

```bash
# 基本用法（使用默认7天chunk）
python scripts/persist_date_range.py --start-date 20240501 --end-date 20240531

# 指定chunk大小
python scripts/persist_date_range.py --start-date 20240501 --end-date 20240531 --chunk-size 14

# 指定线程数和跳过周末
python scripts/persist_date_range.py --start-date 20240501 --end-date 20240531 --max-workers 5 --skip-weekends

# 试运行模式（只显示将要处理的chunks）
python scripts/persist_date_range.py --start-date 20240501 --end-date 20240531 --dry-run

# 启用重试失败chunks
python scripts/persist_date_range.py --start-date 20240501 --end-date 20240531 --retry-failed
```

### 2. Windows批处理方式

```cmd
# 基本用法
scripts\batch_persist.bat 20240501 20240531 3 7

# 指定chunk大小
scripts\batch_persist.bat 20240501 20240531 3 14

# 跳过周末
scripts\batch_persist.bat 20240501 20240531 1 7 --skip-weekends
```

## 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--start-date` | str | 是 | - | 开始日期 (YYYYMMDD格式) |
| `--end-date` | str | 是 | - | 结束日期 (YYYYMMDD格式) |
| `--config` | str | 否 | config/api_config.yaml | API配置文件路径 |
| `--output-dir` | str | 否 | persistdata | 输出目录 |
| `--max-workers` | int | 否 | 3 | 最大并行工作线程数 |
| `--chunk-size` | int | 否 | 7 | 每个chunk的日期数量 |
| `--retry-failed` | flag | 否 | False | 重试失败的chunks |
| `--skip-weekends` | flag | 否 | False | 跳过周末 (周六和周日) |
| `--dry-run` | flag | 否 | False | 试运行模式，只显示将要处理的chunks |

## 优化效果示例

### 示例1: 处理一周的数据
```bash
python scripts/persist_date_range.py --start-date 20240527 --end-date 20240531 --skip-weekends
```

**优化前（旧方式）：**
- 5个工作日 × 3个API = 15次API调用
- 处理时间：约30秒

**优化后（新方式）：**
- Range API：1次调用获取5天数据
- 单日API：5次调用
- 总计：6次API调用
- 节省：9次API调用（60%减少）
- 处理时间：约15秒

### 示例2: 处理一个月的数据
```bash
python scripts/persist_date_range.py --start-date 20240501 --end-date 20240531 --chunk-size 7 --max-workers 3
```

**优化前（旧方式）：**
- 31天 × 3个API = 93次API调用
- 处理时间：约3分钟

**优化后（新方式）：**
- 5个chunks × (1次range调用 + 7次单日调用) = 40次API调用
- 节省：53次API调用（57%减少）
- 处理时间：约1.5分钟

## 支持的Range API

根据配置文件，以下API支持range调用：

### Free Plan
- `daily_quotes` - 股票日行情
- `statements` - 财报快报

### Standard Plan
- `index_option` - 日经225期权
- `weekly_margin_interest` - 信用残高
- `short_selling` - 空卖比率

### Premium Plan
- `breakdown` - 卖买内訳
- `dividend` - 配当信息
- `fs_details` - 财报明细
- `futures` - 先物行情
- `options` - 期权行情

## 输出示例

```
INFO: 开始优化版日期范围持久化: 20240501 到 20240531
INFO: 发现 8 个支持range的API，2 个单日API
INFO: 处理支持range的API...
INFO: 处理Range API: daily_quotes (20240501 - 20240507)
INFO: 调用Range API: get_price_range (20240501 - 20240507)
INFO: Range API daily_quotes 数据保存成功: 7 个文件
INFO: 处理单日API...
INFO: 处理API: listed_info
INFO: 调用单日API: get_listed_info (20240501)
INFO: 批量持久化完成: 成功 10/10, 跳过 0/10, 失败 0/10
INFO: 通过range调用节省了 49 次API调用
```

## 性能建议

### 1. Chunk大小选择
- **小范围（1-7天）**：使用默认7天chunk
- **中等范围（1-2周）**：使用7-14天chunk
- **大范围（1个月以上）**：使用14-30天chunk

### 2. 线程数设置
- **网络带宽充足**：3-5个线程
- **网络带宽有限**：1-2个线程
- **避免rate limiting**：1个线程

### 3. 时间选择
- **避开交易时间**：避免API响应慢
- **使用跳过周末**：减少无效请求
- **分批处理**：大范围数据分批处理

## 故障排除

### 问题1: Range API调用失败
**原因**：日期范围过大或API限制
**解决**：减小chunk大小或增加重试间隔

### 问题2: 数据分割错误
**原因**：日期格式不匹配
**解决**：检查API返回的日期格式

### 问题3: 内存不足
**原因**：单次获取数据过多
**解决**：减小chunk大小

## 配置说明

在`config/api_config.yaml`中，确保正确配置API的range支持：

```yaml
apis:
  daily_quotes:
    enabled: true
    method: "get_price_range"
    is_range: true  # 标记为支持range
    # ... 其他配置
``` 