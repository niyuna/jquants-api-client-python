# J-Quants API 数据检查工具使用说明

## 概述

`inspect_data.py` 是一个命令行工具，用于读取和检查本地存储的J-Quants API数据文件（parquet格式）。它提供了多种功能来帮助你快速了解和分析已持久化的数据。

## 主要功能

### 1. 数据探索
- **列出可用API**: 查看所有可用的数据API目录
- **列出可用日期**: 查看指定API的可用数据日期
- **文件信息**: 显示文件的详细信息（大小、行数、列数等）

### 2. 数据读取
- **读取数据**: 支持读取前N行、后N行或随机采样
- **列选择**: 可以指定要读取的特定列
- **输出格式**: 支持控制台显示或保存为CSV文件

### 3. 数据搜索
- **关键词搜索**: 在所有列或指定列中搜索特定内容
- **灵活匹配**: 支持部分匹配和大小写不敏感搜索

### 4. 数据统计
- **摘要统计**: 提供数据的整体概览
- **数值列统计**: 均值、标准差、范围、空值数量等
- **分类列统计**: 唯一值数量、空值数量、前5个值等

## 安装要求

确保已安装以下Python包：
```bash
pip install pandas pyarrow pyyaml
```

## 使用方法

### 1. Python脚本方式

#### 基本用法
```bash
# 列出所有可用的API
python scripts/inspect_data.py --list-apis

# 列出指定API的可用日期
python scripts/inspect_data.py --list-dates daily_quotes

# 查看文件信息
python scripts/inspect_data.py --info daily_quotes 20240501

# 读取数据（前10行）
python scripts/inspect_data.py --read daily_quotes 20240501 --head 10

# 读取数据（后5行）
python scripts/inspect_data.py --read daily_quotes 20240501 --tail 5

# 随机采样数据
python scripts/inspect_data.py --read daily_quotes 20240501 --sample 20

# 搜索数据
python scripts/inspect_data.py --search daily_quotes 20240501 "7203" --columns Code

# 获取摘要统计
python scripts/inspect_data.py --stats daily_quotes 20240501
```

#### 高级选项
```bash
# 指定数据目录和配置文件
python scripts/inspect_data.py --data-dir /path/to/data --config /path/to/config.yaml --list-apis

# 读取特定列
python scripts/inspect_data.py --read daily_quotes 20240501 --head 10 --columns Code Name Price

# 搜索特定列
python scripts/inspect_data.py --search daily_quotes 20240501 "7203" --search-columns Code Name

# 保存结果到文件
python scripts/inspect_data.py --read daily_quotes 20240501 --head 100 --output daily_quotes_sample.csv

# 禁用格式化输出
python scripts/inspect_data.py --read daily_quotes 20240501 --head 10 --no-format
```

### 2. Windows批处理方式

#### 基本用法
```cmd
# 查看帮助
scripts\inspect_data.bat

# 列出所有可用的API
scripts\inspect_data.bat list-apis

# 列出指定API的可用日期
scripts\inspect_data.bat list-dates daily_quotes

# 查看文件信息
scripts\inspect_data.bat info daily_quotes 20240501

# 读取数据（前10行）
scripts\inspect_data.bat read daily_quotes 20240501 --head 10

# 搜索数据
scripts\inspect_data.bat search daily_quotes 20240501 "7203"

# 获取摘要统计
scripts\inspect_data.bat stats daily_quotes 20240501
```

## 参数说明

### 基本参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--data-dir` | 数据目录路径 | `persistdata` |
| `--config` | 配置文件路径 | `config/api_config.yaml` |

### 操作模式（必需选择一个）
| 参数 | 说明 | 示例 |
|------|------|------|
| `--list-apis` | 列出所有可用的API | `--list-apis` |
| `--list-dates` | 列出指定API的可用日期 | `--list-dates daily_quotes` |
| `--info` | 显示文件信息 | `--info daily_quotes 20240501` |
| `--read` | 读取数据 | `--read daily_quotes 20240501` |
| `--search` | 搜索数据 | `--search daily_quotes 20240501 "7203"` |
| `--stats` | 获取摘要统计 | `--stats daily_quotes 20240501` |

### 读取选项
| 参数 | 说明 | 示例 |
|------|------|------|
| `--head` | 读取前N行数据 | `--head 10` |
| `--tail` | 读取后N行数据 | `--tail 5` |
| `--sample` | 随机采样N行数据 | `--sample 20` |
| `--columns` | 指定要读取的列名 | `--columns Code Name Price` |

### 搜索选项
| 参数 | 说明 | 示例 |
|------|------|------|
| `--search-columns` | 指定要搜索的列名 | `--search-columns Code Name` |

### 输出选项
| 参数 | 说明 | 示例 |
|------|------|------|
| `--output` | 将结果输出到文件 | `--output result.csv` |
| `--no-format` | 禁用格式化输出 | `--no-format` |

## 使用示例

### 示例1: 探索数据结构
```bash
# 1. 查看有哪些API可用
python scripts/inspect_data.py --list-apis

# 2. 查看daily_quotes有哪些日期
python scripts/inspect_data.py --list-dates daily_quotes

# 3. 查看某个日期的文件信息
python scripts/inspect_data.py --info daily_quotes 20240501

# 4. 获取数据摘要统计
python scripts/inspect_data.py --stats daily_quotes 20240501
```

### 示例2: 读取和分析数据
```bash
# 1. 读取前10行数据了解结构
python scripts/inspect_data.py --read daily_quotes 20240501 --head 10

# 2. 读取特定列
python scripts/inspect_data.py --read daily_quotes 20240501 --head 20 --columns Code Name Price

# 3. 随机采样100行进行快速分析
python scripts/inspect_data.py --read daily_quotes 20240501 --sample 100

# 4. 保存样本数据到CSV文件
python scripts/inspect_data.py --read daily_quotes 20240501 --sample 100 --output sample_data.csv
```

### 示例3: 搜索特定数据
```bash
# 1. 搜索特定股票代码
python scripts/inspect_data.py --search daily_quotes 20240501 "7203"

# 2. 在特定列中搜索
python scripts/inspect_data.py --search daily_quotes 20240501 "7203" --search-columns Code

# 3. 搜索公司名称（部分匹配）
python scripts/inspect_data.py --search daily_quotes 20240501 "トヨタ" --search-columns Name

# 4. 保存搜索结果
python scripts/inspect_data.py --search daily_quotes 20240501 "7203" --output toyota_data.csv
```

### 示例4: 批量分析多个API
```bash
# 1. 查看所有API的可用日期
for api in daily_quotes statements listed_info; do
    echo "=== $api ==="
    python scripts/inspect_data.py --list-dates $api | head -5
done

# 2. 比较不同日期的数据量
for api in daily_quotes statements; do
    echo "=== $api ==="
    python scripts/inspect_data.py --info $api 20240501
    python scripts/inspect_data.py --info $api 20240502
done
```

## 输出格式

### 1. 文件信息输出
```
📁 文件路径: persistdata/daily_quotes/20240501.parquet
📊 文件大小: 0.68 MB
📈 数据行数: 2,581
🔢 数据列数: 15
💾 内存占用: 0.32 MB
🔧 API方法: get_price_range
📅 支持Range: 是
📋 计划要求: free
📋 列名: Date, Code, Name, Market, Sector33Code, Sector33Name, Sector17Code, Sector17Name, ScaleCode, ScaleName, Open, High, Low, Close, Volume
```

### 2. 摘要统计输出
```
📊 数据摘要统计
总行数: 2,581
总列数: 15
内存占用: 0.32 MB

🔢 数值列统计 (5 列):
  Open:
    平均值: 2847.23
    标准差: 1234.56
    范围: [100.00, 15000.00]
    空值: 0
  High:
    平均值: 2890.45
    标准差: 1256.78
    范围: [105.00, 15200.00]
    空值: 0

📝 分类列统计 (10 列):
  Code:
    唯一值: 2,581
    空值: 0
    前5个值: {'1301': 1, '1302': 1, '1303': 1, '1304': 1, '1305': 1}
```

## 性能优化建议

### 1. 列选择
- 使用 `--columns` 参数只读取需要的列，可以显著减少内存使用和读取时间
- 对于大型文件，建议先读取少量行了解结构，再决定需要哪些列

### 2. 行数限制
- 使用 `--head`, `--tail`, 或 `--sample` 参数限制读取的行数
- 对于探索性分析，使用 `--sample` 比读取全部数据更高效

### 3. 搜索优化
- 使用 `--search-columns` 在特定列中搜索，比全列搜索更快
- 对于精确匹配，考虑使用更具体的搜索词

## 故障排除

### 问题1: 文件不存在
**错误**: `FileNotFoundError: 文件不存在: ...`
**解决**: 检查API名称和日期是否正确，使用 `--list-dates` 查看可用日期

### 问题2: 内存不足
**错误**: 读取大文件时内存不足
**解决**: 使用 `--head`, `--tail`, 或 `--sample` 限制行数，使用 `--columns` 限制列数

### 问题3: 配置文件错误
**错误**: 配置文件相关错误
**解决**: 检查配置文件路径和格式，或使用默认配置

### 问题4: 编码问题
**错误**: 输出文件编码问题
**解决**: 输出文件默认使用UTF-8编码，确保系统支持

## 扩展功能

### 1. 自定义输出格式
可以修改脚本来支持其他输出格式（如JSON、Excel等）

### 2. 数据验证
可以添加数据质量检查功能，如检查空值、异常值等

### 3. 数据比较
可以添加功能来比较不同日期的数据差异

### 4. 数据导出
可以添加功能来导出特定条件的数据子集

## 总结

`inspect_data.py` 工具提供了强大的功能来探索和分析J-Quants API的持久化数据。通过合理使用各种参数，你可以快速了解数据结构、读取特定数据、搜索感兴趣的内容，并获得数据的统计摘要。这对于数据分析、数据质量检查、问题排查等场景都非常有用。 