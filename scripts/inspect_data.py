#!/usr/bin/env python3
"""
J-Quants API 数据检查工具
用于读取和检查本地存储的parquet文件
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime, date
import pandas as pd
import yaml
from typing import Optional, List, Dict, Any

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from scripts.utils.logger import setup_logger

class DataInspector:
    def __init__(self, data_dir: str = "persistdata", config_path: str = "config/api_config.yaml"):
        self.data_dir = Path(data_dir)
        self.config = self._load_config(config_path)
        self.logger = setup_logger()
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"数据目录不存在: {self.data_dir}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"配置文件未找到: {config_path}，使用默认配置")
            return {}
    
    def list_available_apis(self) -> List[str]:
        """列出可用的API目录"""
        api_dirs = []
        for item in self.data_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                api_dirs.append(item.name)
        return sorted(api_dirs)
    
    def list_available_dates(self, api_name: str) -> List[str]:
        """列出指定API的可用日期"""
        api_dir = self.data_dir / api_name
        if not api_dir.exists():
            return []
        
        dates = []
        for file_path in api_dir.glob("*.parquet"):
            date_str = file_path.stem
            if date_str.isdigit() and len(date_str) == 8:
                dates.append(date_str)
        
        return sorted(dates, reverse=True)
    
    def get_file_info(self, api_name: str, date_str: str) -> Dict[str, Any]:
        """获取文件信息"""
        file_path = self.data_dir / api_name / f"{date_str}.parquet"
        
        if not file_path.exists():
            return {"error": f"文件不存在: {file_path}"}
        
        try:
            # 获取文件大小
            file_size = file_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            # 读取parquet文件元数据（不加载全部数据）
            parquet_file = pd.read_parquet(file_path, engine='pyarrow')
            
            info = {
                "file_path": str(file_path),
                "file_size_mb": round(file_size_mb, 2),
                "file_size_bytes": file_size,
                "rows": len(parquet_file),
                "columns": list(parquet_file.columns),
                "dtypes": parquet_file.dtypes.to_dict(),
                "memory_usage_mb": round(parquet_file.memory_usage(deep=True).sum() / (1024 * 1024), 2),
                "shape": parquet_file.shape
            }
            
            # 添加配置信息
            if api_name in self.config.get('apis', {}):
                api_config = self.config['apis'][api_name]
                info['api_config'] = {
                    'method': api_config.get('method', 'N/A'),
                    'is_range': api_config.get('is_range', False),
                    'plan_required': api_config.get('plan_required', 'N/A')
                }
            
            return info
            
        except Exception as e:
            return {"error": f"读取文件失败: {str(e)}"}
    
    def read_data(self, api_name: str, date_str: str, 
                  head_rows: Optional[int] = None, 
                  tail_rows: Optional[int] = None,
                  sample_rows: Optional[int] = None,
                  columns: Optional[List[str]] = None) -> pd.DataFrame:
        """读取数据"""
        file_path = self.data_dir / api_name / f"{date_str}.parquet"
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            # 读取数据
            if columns:
                df = pd.read_parquet(file_path, columns=columns)
            else:
                df = pd.read_parquet(file_path)
            
            # 应用行数限制
            if head_rows is not None:
                df = df.head(head_rows)
            elif tail_rows is not None:
                df = df.tail(tail_rows)
            elif sample_rows is not None:
                df = df.sample(n=min(sample_rows, len(df)), random_state=42)
            
            return df
            
        except Exception as e:
            raise Exception(f"读取文件失败: {str(e)}")
    
    def search_data(self, api_name: str, date_str: str, 
                   search_term: str, search_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """搜索数据"""
        df = self.read_data(api_name, date_str)
        
        if search_columns:
            # 在指定列中搜索
            mask = df[search_columns].astype(str).apply(
                lambda x: x.str.contains(search_term, case=False, na=False)
            ).any(axis=1)
        else:
            # 在所有列中搜索
            mask = df.astype(str).apply(
                lambda x: x.str.contains(search_term, case=False, na=False)
            ).any(axis=1)
        
        return df[mask]
    
    def get_summary_stats(self, api_name: str, date_str: str) -> Dict[str, Any]:
        """获取数据摘要统计"""
        df = self.read_data(api_name, date_str)
        
        if df.empty:
            return {"error": "数据为空"}
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=['number']).columns
        numeric_stats = {}
        for col in numeric_cols:
            numeric_stats[col] = {
                'count': df[col].count(),
                'mean': df[col].mean(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'null_count': df[col].isnull().sum()
            }
        
        # 分类列统计
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        categorical_stats = {}
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            categorical_stats[col] = {
                'unique_count': df[col].nunique(),
                'null_count': df[col].isnull().sum(),
                'top_values': value_counts.head(5).to_dict()
            }
        
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': numeric_stats,
            'categorical_columns': categorical_stats,
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        }

def format_file_info(info: Dict[str, Any]) -> str:
    """格式化文件信息输出"""
    if 'error' in info:
        return f"❌ {info['error']}"
    
    output = []
    output.append(f"📁 文件路径: {info['file_path']}")
    output.append(f"📊 文件大小: {info['file_size_mb']} MB")
    output.append(f"📈 数据行数: {info['rows']:,}")
    output.append(f"🔢 数据列数: {info['shape'][1]}")
    output.append(f"💾 内存占用: {info['memory_usage_mb']} MB")
    
    if 'api_config' in info:
        config = info['api_config']
        output.append(f"🔧 API方法: {config['method']}")
        output.append(f"📅 支持Range: {'是' if config['is_range'] else '否'}")
        output.append(f"📋 计划要求: {config['plan_required']}")
    
    output.append(f"📋 列名: {', '.join(info['columns'][:10])}")
    if len(info['columns']) > 10:
        output.append(f"    ... 还有 {len(info['columns']) - 10} 列")
    
    return '\n'.join(output)

def format_summary_stats(stats: Dict[str, Any]) -> str:
    """格式化摘要统计输出"""
    if 'error' in stats:
        return f"❌ {stats['error']}"
    
    output = []
    output.append(f"📊 数据摘要统计")
    output.append(f"总行数: {stats['total_rows']:,}")
    output.append(f"总列数: {stats['total_columns']}")
    output.append(f"内存占用: {stats['memory_usage_mb']} MB")
    
    if stats['numeric_columns']:
        output.append(f"\n🔢 数值列统计 ({len(stats['numeric_columns'])} 列):")
        for col, col_stats in list(stats['numeric_columns'].items())[:5]:
            output.append(f"  {col}:")
            output.append(f"    平均值: {col_stats['mean']:.2f}")
            output.append(f"    标准差: {col_stats['std']:.2f}")
            output.append(f"    范围: [{col_stats['min']:.2f}, {col_stats['max']:.2f}]")
            output.append(f"    空值: {col_stats['null_count']}")
    
    if stats['categorical_columns']:
        output.append(f"\n📝 分类列统计 ({len(stats['categorical_columns'])} 列):")
        for col, col_stats in list(stats['categorical_columns'].items())[:5]:
            output.append(f"  {col}:")
            output.append(f"    唯一值: {col_stats['unique_count']}")
            output.append(f"    空值: {col_stats['null_count']}")
            output.append(f"    前5个值: {dict(list(col_stats['top_values'].items())[:5])}")
    
    return '\n'.join(output)

def main():
    parser = argparse.ArgumentParser(
        description='J-Quants API 数据检查工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
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
  
  # 指定数据目录和配置文件
  python scripts/inspect_data.py --data-dir /path/to/data --config /path/to/config.yaml --list-apis
        """
    )
    
    # 基本参数
    parser.add_argument('--data-dir', type=str, default='persistdata',
                       help='数据目录路径 (默认: persistdata)')
    parser.add_argument('--config', type=str, default='config/api_config.yaml',
                       help='配置文件路径 (默认: config/api_config.yaml)')
    
    # 操作模式
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list-apis', action='store_true',
                      help='列出所有可用的API')
    group.add_argument('--list-dates', type=str, metavar='API_NAME',
                      help='列出指定API的可用日期')
    group.add_argument('--info', nargs=2, metavar=('API_NAME', 'DATE'),
                      help='显示指定API和日期的文件信息')
    group.add_argument('--read', nargs=2, metavar=('API_NAME', 'DATE'),
                      help='读取指定API和日期的数据')
    group.add_argument('--search', nargs=3, metavar=('API_NAME', 'DATE', 'SEARCH_TERM'),
                      help='搜索指定API和日期的数据')
    group.add_argument('--stats', nargs=2, metavar=('API_NAME', 'DATE'),
                      help='获取指定API和日期的摘要统计')
    
    # 读取选项
    parser.add_argument('--head', type=int, metavar='ROWS',
                       help='读取前N行数据')
    parser.add_argument('--tail', type=int, metavar='ROWS',
                       help='读取后N行数据')
    parser.add_argument('--sample', type=int, metavar='ROWS',
                       help='随机采样N行数据')
    parser.add_argument('--columns', nargs='+', metavar='COLUMN',
                       help='指定要读取的列名')
    
    # 搜索选项
    parser.add_argument('--search-columns', nargs='+', metavar='COLUMN',
                       help='指定要搜索的列名')
    
    # 输出选项
    parser.add_argument('--output', type=str, metavar='FILE',
                       help='将结果输出到文件 (CSV格式)')
    parser.add_argument('--no-format', action='store_true',
                       help='禁用格式化输出，显示原始数据')
    
    args = parser.parse_args()
    
    try:
        # 创建检查器
        inspector = DataInspector(args.data_dir, args.config)
        
        # 执行相应操作
        if args.list_apis:
            apis = inspector.list_available_apis()
            print(f"📋 可用的API ({len(apis)} 个):")
            for api in apis:
                print(f"  • {api}")
        
        elif args.list_dates:
            dates = inspector.list_available_dates(args.list_dates)
            if dates:
                print(f"📅 {args.list_dates} 的可用日期 ({len(dates)} 个):")
                for date_str in dates[:20]:  # 只显示前20个
                    print(f"  • {date_str}")
                if len(dates) > 20:
                    print(f"  ... 还有 {len(dates) - 20} 个日期")
            else:
                print(f"❌ 未找到 {args.list_dates} 的数据")
        
        elif args.info:
            api_name, date_str = args.info
            info = inspector.get_file_info(api_name, date_str)
            print(format_file_info(info))
        
        elif args.read:
            api_name, date_str = args.read
            df = inspector.read_data(
                api_name, date_str,
                head_rows=args.head,
                tail_rows=args.tail,
                sample_rows=args.sample,
                columns=args.columns
            )
            
            if args.output:
                df.to_csv(args.output, index=False, encoding='utf-8')
                print(f"💾 数据已保存到: {args.output}")
            else:
                if args.no_format:
                    print(df.to_string())
                else:
                    print(f"📊 {api_name} ({date_str}) 数据预览:")
                    print(f"形状: {df.shape}")
                    print(f"列名: {list(df.columns)}")
                    print("\n数据预览:")
                    print(df.to_string(max_rows=20, max_cols=10))
        
        elif args.search:
            api_name, date_str, search_term = args.search
            df = inspector.search_data(
                api_name, date_str, search_term, args.search_columns
            )
            
            if args.output:
                df.to_csv(args.output, index=False, encoding='utf-8')
                print(f"💾 搜索结果已保存到: {args.output}")
            else:
                print(f"🔍 在 {api_name} ({date_str}) 中搜索 '{search_term}' 的结果:")
                print(f"找到 {len(df)} 行数据")
                if not df.empty:
                    print("\n搜索结果:")
                    print(df.to_string(max_rows=20, max_cols=10))
        
        elif args.stats:
            api_name, date_str = args.stats
            stats = inspector.get_summary_stats(api_name, date_str)
            print(format_summary_stats(stats))
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 