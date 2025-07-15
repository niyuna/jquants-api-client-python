"""
集成测试
"""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path
import sys
import os
from unittest.mock import Mock, patch

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from utils.data_persister import DataPersister
from utils.data_validator import DataValidator
from utils.api_client import JQuantsAPIClient

class TestIntegration:
    def setup_method(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.yaml')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        
        # 创建测试配置
        self._create_test_config()
        
        # Mock API客户端
        with patch('utils.api_client.Client'):
            self.api_client = JQuantsAPIClient()
        
        # Mock DataPersister中的JQuantsAPIClient初始化
        with patch('utils.data_persister.JQuantsAPIClient') as mock_api_client_class:
            mock_api_client = Mock()
            mock_api_client_class.return_value = mock_api_client
            self.persister = DataPersister(self.config_path, self.output_dir)
    
    def teardown_method(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_config(self):
        """创建测试配置文件"""
        config = {
            'apis': {
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
                'indices': {
                    'enabled': True,
                    'method': 'get_indices',
                    'output_dir': 'indices',
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
                'breakdown': {
                    'enabled': True,
                    'method': 'get_markets_breakdown',
                    'output_dir': 'breakdown',
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
                }
            }
        }
        
        import yaml
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    def _create_mock_data(self, api_name: str) -> pd.DataFrame:
        """创建Mock数据"""
        if api_name == 'daily_quotes':
            return pd.DataFrame({
                'Date': ['2024-01-01', '2024-01-01'],
                'Code': ['7203', '6758'],
                'Open': [100.0, 200.0],
                'High': [110.0, 210.0],
                'Low': [95.0, 195.0],
                'Close': [105.0, 205.0],
                'Volume': [1000000, 2000000]
            })
        elif api_name == 'listed_info':
            return pd.DataFrame({
                'Date': ['2024-01-01'],
                'Code': ['7203'],
                'CompanyName': ['トヨタ自動車株式会社'],
                'MarketCode': ['1']  # MarketCode是字符串格式
            })
        elif api_name == 'indices':
            return pd.DataFrame({
                'Date': ['2024-01-01'],
                'Code': ['TOPIX'],
                'Open': [100.0],
                'High': [110.0],
                'Low': [95.0],
                'Close': [105.0]
            })
        elif api_name == 'short_selling':
            return pd.DataFrame({
                'Date': ['2024-01-01'],
                'Sector33Code': ['0050'],
                'SellingExcludingShortSellingTurnoverValue': [1000000000]
            })
        elif api_name == 'breakdown':
            return pd.DataFrame({
                'Date': ['2024-01-01'],
                'Code': ['7203'],
                'LongSellValue': [1000000000],
                'LongBuyValue': [2000000000]
            })
        elif api_name == 'market_segments':
            return pd.DataFrame({
                'MarketCode': ['1', '2'],
                'MarketCodeName': ['プライム', 'スタンダード']
            })
        else:
            return pd.DataFrame()
    
    def test_complete_persist_flow(self):
        """测试完整的数据持久化流程"""
        target_date = '20240101'
        
        # Mock API客户端方法
        with patch.object(self.persister.api_client, 'call_single_method') as mock_single, \
             patch.object(self.persister.api_client, 'call_static_method') as mock_static:
            
            # 设置Mock返回值 - 为每个API返回正确的数据
            def mock_single_side_effect(method_name, date):
                if 'get_price_range' in method_name:
                    return self._create_mock_data('daily_quotes')
                elif 'get_listed_info' in method_name:
                    return self._create_mock_data('listed_info')
                elif 'get_indices' in method_name:
                    return self._create_mock_data('indices')
                elif 'get_markets_short_selling' in method_name:
                    return self._create_mock_data('short_selling')
                elif 'get_markets_breakdown' in method_name:
                    return self._create_mock_data('breakdown')
                else:
                    return pd.DataFrame()
            
            def mock_static_side_effect(method_name):
                return self._create_mock_data('market_segments')
            
            mock_single.side_effect = mock_single_side_effect
            mock_static.side_effect = mock_static_side_effect
            
            # 执行持久化
            results = self.persister.persist_data_for_date(target_date)
            
            # 验证结果
            assert results['total_apis'] == 6  # 配置中的API数量
            assert len(results['success']) == 6  # 所有API都应该成功
            assert len(results['failed']) == 0  # 没有失败的API
            
            # 验证文件是否创建
            expected_files = [
                'daily_quotes/20240101.parquet',
                'listed_info/20240101.parquet',
                'indices/20240101.parquet',
                'short_selling/20240101.parquet',
                'breakdown/20240101.parquet'
            ]
            
            for file_path in expected_files:
                full_path = os.path.join(self.output_dir, file_path)
                assert os.path.exists(full_path), f"文件不存在: {full_path}"
                
                # 验证文件内容
                df = pd.read_parquet(full_path)
                assert not df.empty, f"文件为空: {full_path}"
    
    def test_static_data_persist(self):
        """测试静态数据持久化"""
        with patch.object(self.persister.api_client, 'call_static_method') as mock_static:
            mock_static.return_value = self._create_mock_data('market_segments')
            
            results = self.persister.persist_static_data()
            
            assert results['total_static_apis'] == 1
            assert len(results['success']) == 1
            assert len(results['failed']) == 0
            
            # 验证静态数据文件
            static_files = list(Path(self.output_dir).glob('market_segments/*.parquet'))
            assert len(static_files) == 1
    
    def test_data_validation_integration(self):
        """测试数据验证集成"""
        # 创建无效数据
        invalid_data = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Code': ['7203'],
            'Open': [100.0],
            'High': [90.0],  # High < Open
            'Low': [95.0],
            'Close': [105.0],
            'Volume': [1000000]
        })
        
        # Mock API返回无效数据，只对daily_quotes返回无效数据
        with patch.object(self.persister.api_client, 'call_single_method') as mock_single:
            def mock_side_effect(method_name, date):
                if 'get_price_range' in method_name:
                    return invalid_data
                else:
                    return pd.DataFrame()  # 其他API返回空数据
            
            mock_single.side_effect = mock_side_effect
            
            results = self.persister.persist_data_for_date('20240101')
            
            # 验证数据验证失败
            assert len(results['failed']) == 1
            assert '数据验证失败' in results['failed'][0]['error']
    
    def test_retry_failed_apis(self):
        """测试重试失败的API"""
        target_date = '20240101'
        
        # Mock API第一次失败，第二次成功，只对daily_quotes
        call_count = 0
        
        def mock_single_side_effect(method_name, date):
            nonlocal call_count
            if 'get_price_range' in method_name:
                call_count += 1
                if call_count == 1:
                    raise Exception("API调用失败")
                else:
                    return self._create_mock_data('daily_quotes')
            else:
                return pd.DataFrame()  # 其他API返回空数据
        
        with patch.object(self.persister.api_client, 'call_single_method') as mock_single:
            mock_single.side_effect = mock_single_side_effect
            
            results = self.persister.persist_data_for_date(target_date, retry_failed=True)
            
            # 验证重试成功
            assert len(results['success']) == 1
            assert len(results['failed']) == 0
    
    def test_file_already_exists_skip(self):
        """测试文件已存在时跳过"""
        target_date = '20240101'
        
        # 创建已存在的文件
        output_file = Path(self.output_dir) / 'daily_quotes' / f'{target_date}.parquet'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建测试数据
        test_data = self._create_mock_data('daily_quotes')
        test_data.to_parquet(output_file)
        
        # Mock API调用，只对daily_quotes
        with patch.object(self.persister.api_client, 'call_single_method') as mock_single:
            def mock_side_effect(method_name, date):
                if 'get_price_range' in method_name:
                    return self._create_mock_data('daily_quotes')
                else:
                    return pd.DataFrame()  # 其他API返回空数据
            
            mock_single.side_effect = mock_side_effect
            
            results = self.persister.persist_data_for_date(target_date)
            
            # 验证API没有被调用（因为文件已存在）
            mock_single.assert_not_called()
            assert len(results['success']) == 1
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        with patch.object(self.persister.api_client, 'call_single_method') as mock_single:
            def mock_side_effect(method_name, date):
                if 'get_price_range' in method_name:
                    return pd.DataFrame()  # 只有daily_quotes返回空数据
                else:
                    return pd.DataFrame()  # 其他API也返回空数据
            
            mock_single.side_effect = mock_side_effect
            
            results = self.persister.persist_data_for_date('20240101')
            
            # 验证空数据被正确处理
            assert len(results['success']) == 1  # 空数据不算失败，只是跳过
    
    def test_error_handling(self):
        """测试错误处理"""
        with patch.object(self.persister.api_client, 'call_single_method') as mock_single:
            def mock_side_effect(method_name, date):
                if 'get_price_range' in method_name:
                    raise Exception("网络错误")  # 只有daily_quotes抛出异常
                else:
                    return pd.DataFrame()  # 其他API返回空数据
            
            mock_single.side_effect = mock_side_effect
            
            results = self.persister.persist_data_for_date('20240101')
            
            # 验证错误被正确捕获
            assert len(results['failed']) == 1
            assert '网络错误' in results['failed'][0]['error'] 