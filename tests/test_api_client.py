"""
API客户端测试
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from utils.api_client import JQuantsAPIClient

class TestJQuantsAPIClient:
    def setup_method(self):
        with patch('utils.api_client.Client'):
            self.api_client = JQuantsAPIClient()
    
    def test_call_range_method(self):
        """测试范围查询方法"""
        # Mock数据
        mock_data = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Code': ['7203', '6758'],
            'Open': [100.0, 200.0],
            'High': [110.0, 210.0],
            'Low': [95.0, 195.0],
            'Close': [105.0, 205.0],
            'Volume': [1000000, 2000000]
        })
        
        # Mock client方法
        self.api_client.client.get_price_range = Mock(return_value=mock_data)
        
        # 测试调用
        result = self.api_client.call_range_method('get_price_range', '20240101', '20240102')
        
        # 验证结果
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ['Date', 'Code', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        # 验证方法调用
        self.api_client.client.get_price_range.assert_called_once()
    
    def test_call_single_method_daily_quotes(self):
        """测试单日查询方法 - 股票日行情"""
        mock_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'Open': [100.0],
            'High': [110.0],
            'Low': [95.0],
            'Close': [105.0],
            'Volume': [1000000]
        })
        
        self.api_client.client.get_price_range = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_price_range', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
    
    def test_call_single_method_listed_info(self):
        """测试单日查询方法 - 上市公司信息"""
        mock_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'CompanyName': ['トヨタ自動車株式会社'],
            'MarketCode': ['1']
        })
        
        self.api_client.client.get_listed_info = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_listed_info', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        self.api_client.client.get_listed_info.assert_called_once_with(date_yyyymmdd='20240101')
    
    def test_call_single_method_announcement(self):
        """测试单日查询方法 - 公告"""
        mock_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'CompanyName': ['トヨタ自動車株式会社']
        })
        
        self.api_client.client.get_fins_announcement = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_fins_announcement', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        self.api_client.client.get_fins_announcement.assert_called_once()
    
    def test_call_single_method_trades_spec(self):
        """测试单日查询方法 - 交易规格"""
        mock_data = pd.DataFrame({
            'PublishedDate': ['2024-01-01'],
            'StartDate': ['2024-01-01'],
            'EndDate': ['2024-01-01'],
            'Section': ['1']
        })
        
        self.api_client.client.get_markets_trades_spec = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_markets_trades_spec', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        self.api_client.client.get_markets_trades_spec.assert_called_once_with(
            from_yyyymmdd='20240101', to_yyyymmdd='20240101'
        )
    
    def test_call_single_method_indices(self):
        """测试单日查询方法 - 指数"""
        mock_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['TOPIX'],
            'Open': [100.0],
            'High': [110.0],
            'Low': [95.0],
            'Close': [105.0]
        })
        
        self.api_client.client.get_indices = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_indices', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        self.api_client.client.get_indices.assert_called_once_with(date_yyyymmdd='20240101')
    
    def test_call_single_method_short_selling(self):
        """测试单日查询方法 - 卖空"""
        mock_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Sector33Code': ['0050'],
            'SellingExcludingShortSellingTurnoverValue': [1000000000]
        })
        
        self.api_client.client.get_markets_short_selling = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_markets_short_selling', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        self.api_client.client.get_markets_short_selling.assert_called_once_with(date_yyyymmdd='20240101')
    
    def test_call_single_method_breakdown(self):
        """测试单日查询方法 - 买卖明细"""
        mock_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'LongSellValue': [1000000000],
            'LongBuyValue': [2000000000]
        })
        
        self.api_client.client.get_markets_breakdown = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_markets_breakdown', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        self.api_client.client.get_markets_breakdown.assert_called_once_with(date_yyyymmdd='20240101')
    
    def test_call_single_method_prices_am(self):
        """测试单日查询方法 - 前场行情"""
        mock_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'MorningOpen': [100.0],
            'MorningHigh': [110.0],
            'MorningLow': [95.0],
            'MorningClose': [105.0]
        })
        
        self.api_client.client.get_prices_prices_am = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_prices_prices_am', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        self.api_client.client.get_prices_prices_am.assert_called_once()
    
    def test_call_single_method_dividend(self):
        """测试单日查询方法 - 分红"""
        mock_data = pd.DataFrame({
            'AnnouncementDate': ['2024-01-01'],
            'Code': ['7203'],
            'ReferenceNumber': ['2024-001']
        })
        
        self.api_client.client.get_fins_dividend = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_fins_dividend', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        self.api_client.client.get_fins_dividend.assert_called_once_with(date_yyyymmdd='20240101')
    
    def test_call_single_method_futures(self):
        """测试单日查询方法 - 期货"""
        mock_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['NK225'],
            'WholeDayOpen': [100.0],
            'WholeDayHigh': [110.0],
            'WholeDayLow': [95.0],
            'WholeDayClose': [105.0]
        })
        
        self.api_client.client.get_derivatives_futures = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_derivatives_futures', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        self.api_client.client.get_derivatives_futures.assert_called_once_with(date_yyyymmdd='20240101')
    
    def test_call_single_method_options(self):
        """测试单日查询方法 - 期权"""
        mock_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['NK225C'],
            'WholeDayOpen': [100.0],
            'WholeDayHigh': [110.0],
            'WholeDayLow': [95.0],
            'WholeDayClose': [105.0]
        })
        
        self.api_client.client.get_derivatives_options = Mock(return_value=mock_data)
        
        result = self.api_client.call_single_method('get_derivatives_options', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        self.api_client.client.get_derivatives_options.assert_called_once_with(date_yyyymmdd='20240101')
    
    def test_call_static_method(self):
        """测试静态数据方法"""
        mock_data = pd.DataFrame({
            'MarketCode': ['1', '2'],
            'MarketCodeName': ['プライム', 'スタンダード']
        })
        
        self.api_client.client.get_markets_market_segments = Mock(return_value=mock_data)
        
        result = self.api_client.call_static_method('get_markets_market_segments')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        self.api_client.client.get_markets_market_segments.assert_called_once()
    
    def test_parse_date(self):
        """测试日期解析"""
        # 测试有效日期
        result = self.api_client._parse_date('20240101')
        # datetime和pd.Timestamp都是有效的时间类型
        assert isinstance(result, (pd.Timestamp, datetime)), f"Expected Timestamp or datetime, got {type(result)}"
        assert result.strftime('%Y%m%d') == '20240101'
        
        # 测试无效日期
        result = self.api_client._parse_date('invalid_date')
        assert result == 'invalid_date' 