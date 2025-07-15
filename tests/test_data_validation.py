"""
数据验证测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from utils.data_validator import DataValidator

class TestDataValidator:
    def setup_method(self):
        self.validator = DataValidator()
    
    def test_daily_quotes_validation(self):
        """测试股票日行情数据验证"""
        # 有效数据
        valid_data = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Code': ['7203', '6758'],
            'Open': [100.0, 200.0],
            'High': [110.0, 210.0],
            'Low': [95.0, 195.0],
            'Close': [105.0, 205.0],
            'Volume': [1000000, 2000000]
        })
        
        is_valid, errors = self.validator.validate_api_data('daily_quotes', valid_data)
        assert is_valid, f"有效数据验证失败: {errors}"
        
        # 无效数据 - OHLC关系错误
        invalid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'Open': [100.0],
            'High': [90.0],  # High < Open
            'Low': [95.0],
            'Close': [105.0],
            'Volume': [1000000]
        })
        
        is_valid, errors = self.validator.validate_api_data('daily_quotes', invalid_data)
        assert not is_valid, "无效数据应该验证失败"
        assert any("不是最高价" in error for error in errors)
    
    def test_listed_info_validation(self):
        """测试上市公司信息数据验证"""
        valid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'CompanyName': ['トヨタ自動車株式会社'],
            'MarketCode': ['1']  # MarketCode是字符串格式
        })
        
        is_valid, errors = self.validator.validate_api_data('listed_info', valid_data)
        assert is_valid, f"有效数据验证失败: {errors}"
        
        # 无效数据 - 代码格式错误
        invalid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['ABC'],  # 不是4-5位数字
            'CompanyName': ['テスト会社'],
            'MarketCode': ['1']
        })
        
        is_valid, errors = self.validator.validate_api_data('listed_info', invalid_data)
        assert not is_valid, "无效数据应该验证失败"
        assert any("格式不正确的代码" in error for error in errors)
    
    def test_indices_validation(self):
        """测试指数数据验证"""
        valid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['TOPIX'],
            'Open': [100.0],
            'High': [110.0],
            'Low': [95.0],
            'Close': [105.0]
        })
        
        is_valid, errors = self.validator.validate_api_data('indices', valid_data)
        assert is_valid, f"有效数据验证失败: {errors}"
    
    def test_short_selling_validation(self):
        """测试卖空数据验证"""
        valid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Sector33Code': ['0050'],
            'SellingExcludingShortSellingTurnoverValue': [1000000000]
        })
        
        is_valid, errors = self.validator.validate_api_data('short_selling', valid_data)
        assert is_valid, f"有效数据验证失败: {errors}"
        
        # 无效数据 - 负值
        invalid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Sector33Code': ['0050'],
            'SellingExcludingShortSellingTurnoverValue': [-1000000]  # 负值
        })
        
        is_valid, errors = self.validator.validate_api_data('short_selling', invalid_data)
        assert not is_valid, "无效数据应该验证失败"
        assert any("包含负值" in error for error in errors)
    
    def test_breakdown_validation(self):
        """测试买卖明细数据验证"""
        valid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'LongSellValue': [1000000000],
            'LongBuyValue': [2000000000]
        })
        
        is_valid, errors = self.validator.validate_api_data('breakdown', valid_data)
        assert is_valid, f"有效数据验证失败: {errors}"
    
    def test_prices_am_validation(self):
        """测试前场行情数据验证"""
        valid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'MorningOpen': [100.0],
            'MorningHigh': [110.0],
            'MorningLow': [95.0],
            'MorningClose': [105.0]
        })
        
        is_valid, errors = self.validator.validate_api_data('prices_am', valid_data)
        assert is_valid, f"有效数据验证失败: {errors}"
    
    def test_dividend_validation(self):
        """测试分红数据验证"""
        valid_data = pd.DataFrame({
            'AnnouncementDate': ['2024-01-01'],
            'Code': ['7203'],
            'ReferenceNumber': ['2024-001']
        })
        
        is_valid, errors = self.validator.validate_api_data('dividend', valid_data)
        assert is_valid, f"有效数据验证失败: {errors}"
    
    def test_futures_validation(self):
        """测试期货数据验证"""
        valid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['NK225'],
            'WholeDayOpen': [100.0],
            'WholeDayHigh': [110.0],
            'WholeDayLow': [95.0],
            'WholeDayClose': [105.0]
        })
        
        is_valid, errors = self.validator.validate_api_data('futures', valid_data)
        assert is_valid, f"有效数据验证失败: {errors}"
    
    def test_options_validation(self):
        """测试期权数据验证"""
        valid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['NK225C'],
            'WholeDayOpen': [100.0],
            'WholeDayHigh': [110.0],
            'WholeDayLow': [95.0],
            'WholeDayClose': [105.0]
        })
        
        is_valid, errors = self.validator.validate_api_data('options', valid_data)
        assert is_valid, f"有效数据验证失败: {errors}"
    
    def test_static_data_validation(self):
        """测试静态数据验证"""
        # 市场区分
        market_data = pd.DataFrame({
            'MarketCode': ['1', '2'],
            'MarketCodeName': ['プライム', 'スタンダード']
        })
        
        is_valid, errors = self.validator.validate_api_data('market_segments', market_data)
        assert is_valid, f"市场区分数据验证失败: {errors}"
        
        # 业种分类
        sector_data = pd.DataFrame({
            'Sector17Code': ['0050'],
            'Sector17CodeName': ['建設業']
        })
        
        is_valid, errors = self.validator.validate_api_data('sectors_17', sector_data)
        assert is_valid, f"业种分类数据验证失败: {errors}"
    
    def test_empty_data_validation(self):
        """测试空数据验证"""
        empty_data = pd.DataFrame()
        is_valid, errors = self.validator.validate_api_data('daily_quotes', empty_data)
        assert not is_valid
        assert "数据为空" in errors[0]
    
    def test_missing_columns_validation(self):
        """测试缺少必需列验证"""
        incomplete_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203']
            # 缺少 Open, High, Low, Close, Volume
        })
        
        is_valid, errors = self.validator.validate_api_data('daily_quotes', incomplete_data)
        assert not is_valid
        assert any("缺少必需列" in error for error in errors)
    
    def test_date_format_validation(self):
        """测试日期格式验证"""
        invalid_date_data = pd.DataFrame({
            'Date': ['2024/01/01'],  # 错误格式
            'Code': ['7203'],
            'Open': [100.0],
            'High': [110.0],
            'Low': [95.0],
            'Close': [105.0],
            'Volume': [1000000]
        })
        
        is_valid, errors = self.validator.validate_api_data('daily_quotes', invalid_date_data)
        assert not is_valid
        assert any("日期格式不正确" in error for error in errors)
    
    def test_duplicate_records_validation(self):
        """测试重复记录验证"""
        duplicate_data = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-01'],
            'Code': ['7203', '7203'],
            'Open': [100.0, 100.0],
            'High': [110.0, 110.0],
            'Low': [95.0, 95.0],
            'Close': [105.0, 105.0],
            'Volume': [1000000, 1000000]
        })
        
        is_valid, errors = self.validator.validate_api_data('daily_quotes', duplicate_data)
        assert not is_valid
        assert any("重复记录" in error for error in errors) 