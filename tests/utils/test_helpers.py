"""
测试辅助工具
"""

import pandas as pd
import tempfile
import shutil
import os
from pathlib import Path
from typing import Dict, Any

def create_temp_test_env():
    """创建临时测试环境"""
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, 'test_config.yaml')
    output_dir = os.path.join(temp_dir, 'output')
    
    return temp_dir, config_path, output_dir

def cleanup_temp_env(temp_dir: str):
    """清理临时测试环境"""
    shutil.rmtree(temp_dir, ignore_errors=True)

def create_sample_data(api_name: str) -> pd.DataFrame:
    """创建样本数据"""
    sample_data = {
        'daily_quotes': pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Code': ['7203', '6758'],
            'Open': [100.0, 200.0],
            'High': [110.0, 210.0],
            'Low': [95.0, 195.0],
            'Close': [105.0, 205.0],
            'Volume': [1000000, 2000000]
        }),
        'listed_info': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'CompanyName': ['トヨタ自動車株式会社'],
            'MarketCode': ['1']  # MarketCode是字符串格式
        }),
        'indices': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['TOPIX'],
            'Open': [100.0],
            'High': [110.0],
            'Low': [95.0],
            'Close': [105.0]
        }),
        'short_selling': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Sector33Code': ['0050'],
            'SellingExcludingShortSellingTurnoverValue': [1000000000]
        }),
        'breakdown': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'LongSellValue': [1000000000],
            'LongBuyValue': [2000000000]
        }),
        'prices_am': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'MorningOpen': [100.0],
            'MorningHigh': [110.0],
            'MorningLow': [95.0],
            'MorningClose': [105.0]
        }),
        'dividend': pd.DataFrame({
            'AnnouncementDate': ['2024-01-01'],
            'Code': ['7203'],
            'ReferenceNumber': ['2024-001']
        }),
        'futures': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['NK225'],
            'WholeDayOpen': [100.0],
            'WholeDayHigh': [110.0],
            'WholeDayLow': [95.0],
            'WholeDayClose': [105.0]
        }),
        'options': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['NK225C'],
            'WholeDayOpen': [100.0],
            'WholeDayHigh': [110.0],
            'WholeDayLow': [95.0],
            'WholeDayClose': [105.0]
        }),
        'market_segments': pd.DataFrame({
            'MarketCode': ['1', '2'],
            'MarketCodeName': ['プライム', 'スタンダード']
        }),
        'sectors_17': pd.DataFrame({
            'Sector17Code': ['0050'],
            'Sector17CodeName': ['建設業']
        }),
        'sectors_33': pd.DataFrame({
            'Sector33Code': ['0050'],
            'Sector33CodeName': ['建設業']
        }),
        'statements': pd.DataFrame({
            'DisclosedDate': ['2024-01-01'],
            'LocalCode': ['7203'],
            'TypeOfDocument': ['120']
        }),
        'announcement': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'CompanyName': ['トヨタ自動車株式会社']
        }),
        'trades_spec': pd.DataFrame({
            'PublishedDate': ['2024-01-01'],
            'StartDate': ['2024-01-01'],
            'EndDate': ['2024-01-01'],
            'Section': ['1']
        }),
        'topix': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Open': [100.0],
            'High': [110.0],
            'Low': [95.0],
            'Close': [105.0]
        }),
        'index_option': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['NK225'],
            'WholeDayOpen': [100.0],
            'WholeDayHigh': [110.0],
            'WholeDayLow': [95.0],
            'WholeDayClose': [105.0]
        }),
        'weekly_margin_interest': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'ShortMarginTradeVolume': [1000000],
            'LongMarginTradeVolume': [2000000]
        }),
        'short_selling_positions': pd.DataFrame({
            'DisclosedDate': ['2024-01-01'],
            'CalculatedDate': ['2024-01-01'],
            'Code': ['7203'],
            'ShortSellerName': ['テスト証券']
        }),
        'fs_details': pd.DataFrame({
            'DisclosedDate': ['2024-01-01'],
            'LocalCode': ['7203'],
            'TypeOfDocument': ['120']
        }),
        'listed_companies': pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'CompanyName': ['トヨタ自動車株式会社']
        })
    }
    
    return sample_data.get(api_name, pd.DataFrame())

def create_test_config(apis_to_include: list = None) -> Dict[str, Any]:
    """创建测试配置"""
    if apis_to_include is None:
        apis_to_include = ['daily_quotes', 'listed_info', 'indices', 'short_selling', 'breakdown', 'market_segments']
    
    all_apis = {
        'daily_quotes': {
            'enabled': True,
            'method': 'get_price_range',
            'output_dir': 'daily_quotes',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'free'
        },
        'listed_info': {
            'enabled': True,
            'method': 'get_listed_info',
            'output_dir': 'listed_info',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'free'
        },
        'statements': {
            'enabled': True,
            'method': 'get_fins_statements',
            'output_dir': 'statements',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'free'
        },
        'announcement': {
            'enabled': True,
            'method': 'get_fins_announcement',
            'output_dir': 'announcement',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'free'
        },
        'trades_spec': {
            'enabled': True,
            'method': 'get_markets_trades_spec',
            'output_dir': 'trades_spec',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'light'
        },
        'topix': {
            'enabled': True,
            'method': 'get_indices_topix',
            'output_dir': 'topix',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'light'
        },
        'index_option': {
            'enabled': True,
            'method': 'get_option_index_option',
            'output_dir': 'index_option',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'standard'
        },
        'weekly_margin_interest': {
            'enabled': True,
            'method': 'get_markets_weekly_margin_interest',
            'output_dir': 'weekly_margin_interest',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'standard'
        },
        'short_selling': {
            'enabled': True,
            'method': 'get_markets_short_selling',
            'output_dir': 'short_selling',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'standard'
        },
        'indices': {
            'enabled': True,
            'method': 'get_indices',
            'output_dir': 'indices',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'standard'
        },
        'short_selling_positions': {
            'enabled': True,
            'method': 'get_markets_short_selling_positions',
            'output_dir': 'short_selling_positions',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'standard'
        },
        'breakdown': {
            'enabled': True,
            'method': 'get_markets_breakdown',
            'output_dir': 'breakdown',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'premium'
        },
        'prices_am': {
            'enabled': True,
            'method': 'get_prices_prices_am',
            'output_dir': 'prices_am',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'premium'
        },
        'dividend': {
            'enabled': True,
            'method': 'get_fins_dividend',
            'output_dir': 'dividend',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'premium'
        },
        'fs_details': {
            'enabled': True,
            'method': 'get_fins_fs_details',
            'output_dir': 'fs_details',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'premium'
        },
        'futures': {
            'enabled': True,
            'method': 'get_derivatives_futures',
            'output_dir': 'futures',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'premium'
        },
        'options': {
            'enabled': True,
            'method': 'get_derivatives_options',
            'output_dir': 'options',
            'file_pattern': '{date}.parquet',
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'premium'
        },
        'market_segments': {
            'enabled': True,
            'method': 'get_markets_market_segments',
            'output_dir': 'market_segments',
            'file_pattern': '{date}.parquet',
            'is_static': True,
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'free'
        },
        'sectors_17': {
            'enabled': True,
            'method': 'get_markets_sectors_17',
            'output_dir': 'sectors_17',
            'file_pattern': '{date}.parquet',
            'is_static': True,
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'free'
        },
        'sectors_33': {
            'enabled': True,
            'method': 'get_markets_sectors_33',
            'output_dir': 'sectors_33',
            'file_pattern': '{date}.parquet',
            'is_static': True,
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'free'
        },
        'listed_companies': {
            'enabled': True,
            'method': 'get_listed_companies',
            'output_dir': 'listed_companies',
            'file_pattern': '{date}.parquet',
            'is_static': True,
            'retry_count': 3,
            'retry_delay': 5,
            'plan_required': 'free'
        }
    }
    
    # 只包含指定的API
    selected_apis = {name: config for name, config in all_apis.items() if name in apis_to_include}
    
    return {'apis': selected_apis}

def assert_dataframe_structure(df: pd.DataFrame, expected_columns: list):
    """断言DataFrame结构"""
    assert isinstance(df, pd.DataFrame), "数据不是DataFrame类型"
    assert not df.empty, "DataFrame为空"
    assert list(df.columns) == expected_columns, f"列不匹配: 期望 {expected_columns}, 实际 {list(df.columns)}"

def assert_file_exists_and_valid(file_path: str):
    """断言文件存在且有效"""
    assert os.path.exists(file_path), f"文件不存在: {file_path}"
    
    # 尝试读取parquet文件
    if file_path.endswith('.parquet'):
        df = pd.read_parquet(file_path)
        assert not df.empty, f"文件为空: {file_path}"
    
    # 检查文件大小
    file_size = os.path.getsize(file_path)
    assert file_size > 0, f"文件大小为0: {file_path}" 