"""
数据验证模块
验证API返回数据的格式、完整性、一致性
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
import logging

class DataValidator:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """加载数据验证规则"""
        return {
            # Free plan APIs
            'daily_quotes': {
                'required_columns': ['Date', 'Code', 'Open', 'High', 'Low', 'Close', 'Volume'],
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['Open', 'High', 'Low', 'Close', 'Volume'],
                'positive_columns': ['Volume'],
                'price_range': (0, 1000000),
                'volume_range': (0, 1000000000),
                'ohlc_validation': True,
            },
            'listed_info': {
                'required_columns': ['Date', 'Code', 'CompanyName', 'MarketCode'],
                'date_format': '%Y-%m-%d',
                'string_columns': ['CompanyName', 'MarketCode'],
                # 去掉code_format验证
            },
            'statements': {
                'required_columns': ['DisclosedDate', 'LocalCode', 'TypeOfDocument'],
                'date_format': '%Y-%m-%d',
                'code_format': r'^[A-Z0-9]{4,5}$',
            },
            'announcement': {
                'required_columns': ['Date', 'Code', 'CompanyName'],
                'date_format': '%Y-%m-%d',
                'string_columns': ['CompanyName'],
                'code_format': r'^[A-Z0-9]{4,5}$',
            },
            
            # Light plan APIs
            'trades_spec': {
                'required_columns': ['PublishedDate', 'StartDate', 'EndDate', 'Section'],
                'date_format': '%Y-%m-%d',
                'string_columns': ['Section'],
            },
            'topix': {
                'required_columns': ['Date', 'Open', 'High', 'Low', 'Close'],
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['Open', 'High', 'Low', 'Close'],
                'positive_columns': ['Open', 'High', 'Low', 'Close'],
                'ohlc_validation': True,
            },
            
            # Standard plan APIs
            'index_option': {
                'required_columns': ['Date', 'Code', 'WholeDayOpen', 'WholeDayHigh', 'WholeDayLow', 'WholeDayClose'],
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['WholeDayOpen', 'WholeDayHigh', 'WholeDayLow', 'WholeDayClose'],
                'positive_columns': ['WholeDayOpen', 'WholeDayHigh', 'WholeDayLow', 'WholeDayClose'],
                'ohlc_validation': True,
            },
            'weekly_margin_interest': {
                'required_columns': ['Date', 'Code', 'ShortMarginTradeVolume', 'LongMarginTradeVolume'],
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['ShortMarginTradeVolume', 'LongMarginTradeVolume'],
                'positive_columns': ['ShortMarginTradeVolume', 'LongMarginTradeVolume'],
            },
            'short_selling': {
                'required_columns': ['Date', 'Sector33Code', 'SellingExcludingShortSellingTurnoverValue'],
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['SellingExcludingShortSellingTurnoverValue'],
                'positive_columns': ['SellingExcludingShortSellingTurnoverValue'],
            },
            'indices': {
                'required_columns': ['Date', 'Code', 'Open', 'High', 'Low', 'Close'],
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['Open', 'High', 'Low', 'Close'],
                'positive_columns': ['Open', 'High', 'Low', 'Close'],
                'ohlc_validation': True,
            },
            'short_selling_positions': {
                'required_columns': ['DisclosedDate', 'CalculatedDate', 'Code', 'ShortSellerName'],
                'date_format': '%Y-%m-%d',
                'string_columns': ['ShortSellerName'],
                'code_format': r'^[A-Z0-9]{4,5}$',
            },
            
            # Premium plan APIs
            'breakdown': {
                'required_columns': ['Date', 'Code', 'LongSellValue', 'LongBuyValue'],
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['LongSellValue', 'LongBuyValue'],
                'positive_columns': ['LongSellValue', 'LongBuyValue'],
            },
            'prices_am': {
                'required_columns': ['Date', 'Code', 'MorningOpen', 'MorningHigh', 'MorningLow', 'MorningClose'],
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['MorningOpen', 'MorningHigh', 'MorningLow', 'MorningClose'],
                'positive_columns': ['MorningOpen', 'MorningHigh', 'MorningLow', 'MorningClose'],
                'ohlc_validation': True,
            },
            'dividend': {
                'required_columns': ['AnnouncementDate', 'Code', 'ReferenceNumber'],
                'date_format': '%Y-%m-%d',
                'string_columns': ['ReferenceNumber'],
                'code_format': r'^[A-Z0-9]{4,5}$',
            },
            'fs_details': {
                'required_columns': ['DisclosedDate', 'LocalCode', 'TypeOfDocument'],
                'date_format': '%Y-%m-%d',
                'code_format': r'^[A-Z0-9]{4,5}$',
            },
            'futures': {
                'required_columns': ['Date', 'Code', 'WholeDayOpen', 'WholeDayHigh', 'WholeDayLow', 'WholeDayClose'],
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['WholeDayOpen', 'WholeDayHigh', 'WholeDayLow', 'WholeDayClose'],
                'positive_columns': ['WholeDayOpen', 'WholeDayHigh', 'WholeDayLow', 'WholeDayClose'],
                'ohlc_validation': True,
            },
            'options': {
                'required_columns': ['Date', 'Code', 'WholeDayOpen', 'WholeDayHigh', 'WholeDayLow', 'WholeDayClose'],
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['WholeDayOpen', 'WholeDayHigh', 'WholeDayLow', 'WholeDayClose'],
                'positive_columns': ['WholeDayOpen', 'WholeDayHigh', 'WholeDayLow', 'WholeDayClose'],
                'ohlc_validation': True,
            },
            
            # Static data APIs
            'market_segments': {
                'required_columns': ['MarketCode', 'MarketCodeName'],
                'string_columns': ['MarketCode', 'MarketCodeName'],
            },
            'sectors_17': {
                'required_columns': ['Sector17Code', 'Sector17CodeName'],
                'string_columns': ['Sector17Code', 'Sector17CodeName'],
            },
            'sectors_33': {
                'required_columns': ['Sector33Code', 'Sector33CodeName'],
                'string_columns': ['Sector33Code', 'Sector33CodeName'],
            },
            'listed_companies': {
                'required_columns': ['Date', 'Code', 'CompanyName'],
                'date_format': '%Y-%m-%d',
                'string_columns': ['CompanyName'],
                'code_format': r'^[A-Z0-9]{4,5}$',
            },
        }
    
    def validate_api_data(self, api_name: str, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """验证API数据"""
        if data is None or data.empty:
            return False, ["数据为空"]
        
        errors = []
        
        # 获取验证规则
        rules = self.validation_rules.get(api_name, {})
        if not rules:
            self.logger.warning(f"未找到API {api_name} 的验证规则")
            return True, []
        
        # 1. 必需列检查
        required_cols = rules.get('required_columns', [])
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            errors.append(f"缺少必需列: {missing_cols}")
        
        # 2. 数据类型检查
        errors.extend(self._validate_data_types(data, rules))
        
        # 3. 数值范围检查
        errors.extend(self._validate_numeric_ranges(data, rules))
        
        # 4. 日期格式检查
        errors.extend(self._validate_date_format(data, rules))
        
        # 5. OHLC关系检查
        if rules.get('ohlc_validation', False):
            errors.extend(self._validate_ohlc_relationships(data))
        
        # 6. 代码格式检查
        if 'code_format' in rules:
            errors.extend(self._validate_code_format(data, rules['code_format']))
        
        # 7. 数据完整性检查
        errors.extend(self._validate_data_completeness(data, api_name))
        
        # 8. 数据一致性检查
        errors.extend(self._validate_data_consistency(data, api_name))
        
        is_valid = len(errors) == 0
        if not is_valid:
            self.logger.error(f"API {api_name} 数据验证失败: {errors}")
        
        return is_valid, errors
    
    def _validate_data_types(self, data: pd.DataFrame, rules: Dict[str, Any]) -> List[str]:
        """验证数据类型"""
        errors = []
        
        # 数值列检查
        numeric_cols = rules.get('numeric_columns', [])
        for col in numeric_cols:
            if col in data.columns:
                if not pd.api.types.is_numeric_dtype(data[col]):
                    errors.append(f"列 {col} 应为数值类型")
        
        # 字符串列检查
        string_cols = rules.get('string_columns', [])
        for col in string_cols:
            if col in data.columns:
                if not pd.api.types.is_string_dtype(data[col]):
                    errors.append(f"列 {col} 应为字符串类型")
        
        return errors
    
    def _validate_numeric_ranges(self, data: pd.DataFrame, rules: Dict[str, Any]) -> List[str]:
        """验证数值范围"""
        errors = []
        
        # 正数列检查
        positive_cols = rules.get('positive_columns', [])
        for col in positive_cols:
            if col in data.columns:
                if (data[col] < 0).any():
                    errors.append(f"列 {col} 包含负值")
        
        # 价格范围检查
        price_range = rules.get('price_range')
        if price_range:
            price_cols = ['Open', 'High', 'Low', 'Close']
            for col in price_cols:
                if col in data.columns:
                    invalid_prices = data[
                        (data[col] < price_range[0]) | (data[col] > price_range[1])
                    ]
                    if not invalid_prices.empty:
                        errors.append(f"列 {col} 包含超出范围的值: {price_range}")
        
        return errors
    
    def _validate_date_format(self, data: pd.DataFrame, rules: Dict[str, Any]) -> List[str]:
        """验证日期格式"""
        errors = []
        date_format = rules.get('date_format')
        if not date_format:
            return errors
        
        # 排除包含 "date" 但不是日期字段的列名（如 consolidated, updated, dated 等）
        exclude_keywords = ['consolidated', 'updated', 'modified', 'created', 'published', 'dated']
        date_cols = []
        for col in data.columns:
            col_lower = col.lower()
            if col == 'Date' or ('date' in col_lower and not any(keyword in col_lower for keyword in exclude_keywords)):
                date_cols.append(col)
        
        for col in date_cols:
            if col in data.columns:
                # 特殊处理 PayableDate，允许 "-" 和空字符串
                if col == 'PayableDate':
                    # 过滤掉 "-" 和空字符串，只验证其他值
                    valid_data = data[col].dropna()
                    valid_data = valid_data[valid_data != '-']
                    valid_data = valid_data[valid_data != '']
                    
                    if not valid_data.empty:
                        try:
                            pd.to_datetime(valid_data, format=date_format)
                        except ValueError:
                            errors.append(f"列 {col} 日期格式不正确，应为 {date_format}")
                else:
                    try:
                        pd.to_datetime(data[col], format=date_format)
                    except ValueError:
                        errors.append(f"列 {col} 日期格式不正确，应为 {date_format}")
        
        return errors
    
    def _validate_ohlc_relationships(self, data: pd.DataFrame) -> List[str]:
        """验证OHLC关系"""
        errors = []
        
        # 检查是否有OHLC列
        ohlc_patterns = [
            ['Open', 'High', 'Low', 'Close'],
            ['MorningOpen', 'MorningHigh', 'MorningLow', 'MorningClose'],
            ['WholeDayOpen', 'WholeDayHigh', 'WholeDayLow', 'WholeDayClose']
        ]
        
        for pattern in ohlc_patterns:
            if all(col in data.columns for col in pattern):
                open_col, high_col, low_col, close_col = pattern
                
                # 检查 High >= Low
                invalid_hl = data[data[high_col] < data[low_col]]
                if not invalid_hl.empty:
                    errors.append(f"发现 {len(invalid_hl)} 条记录 {high_col} < {low_col}")
                
                # 检查 High >= Open, Close
                invalid_high = data[
                    (data[high_col] < data[open_col]) | (data[high_col] < data[close_col])
                ]
                if not invalid_high.empty:
                    errors.append(f"发现 {len(invalid_high)} 条记录 {high_col} 不是最高价")
                
                # 检查 Low <= Open, Close
                invalid_low = data[
                    (data[low_col] > data[open_col]) | (data[low_col] > data[close_col])
                ]
                if not invalid_low.empty:
                    errors.append(f"发现 {len(invalid_low)} 条记录 {low_col} 不是最低价")
        
        return errors
    
    def _validate_code_format(self, data: pd.DataFrame, pattern: str) -> List[str]:
        """验证代码格式"""
        errors = []
        
        # 只验证Code字段，不验证其他code字段
        if 'Code' in data.columns:
            invalid_codes = data[~data['Code'].astype(str).str.match(pattern)]
            if not invalid_codes.empty:
                errors.append(f"列 Code 包含格式不正确的代码")
        
        return errors
    
    def _validate_data_completeness(self, data: pd.DataFrame, api_name: str) -> List[str]:
        """验证数据完整性"""
        errors = []
        
        # 去掉空值验证
        
        # 检查重复记录
        if 'Date' in data.columns and 'Code' in data.columns:
            duplicates = data.duplicated(subset=['Date', 'Code']).sum()
            if duplicates > 0:
                errors.append(f"发现 {duplicates} 条重复记录")
        
        return errors
    
    def _validate_data_consistency(self, data: pd.DataFrame, api_name: str) -> List[str]:
        """验证数据一致性"""
        errors = []
        
        # 检查日期范围合理性
        if 'Date' in data.columns:
            dates = pd.to_datetime(data['Date'])
            date_range = dates.max() - dates.min()
            if date_range.days > 365:  # 单次查询不应超过一年
                errors.append("数据日期范围过大，可能包含历史数据")
        
        # 去掉数据量验证
        
        return errors 