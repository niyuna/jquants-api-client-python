"""
数据持久化核心逻辑
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import yaml
import time

from .api_client import JQuantsAPIClient
from .data_validator import DataValidator

class DataPersister:
    def __init__(self, config_path: str, output_dir: str, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.output_dir = Path(output_dir)
        self.api_client = JQuantsAPIClient()
        self.validator = DataValidator(logger)
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def persist_data_for_date(self, target_date: str, retry_failed: bool = False) -> Dict[str, Any]:
        """为指定日期持久化所有API数据"""
        self.logger.info(f"开始持久化 {target_date} 的数据")
        
        results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'total_apis': 0
        }
        
        # 获取启用的API
        enabled_apis = self._get_enabled_apis()
        results['total_apis'] = len(enabled_apis)
        
        for api_name, api_config in enabled_apis.items():
            try:
                result = self._persist_single_api(api_name, api_config, target_date)
                if result['success']:
                    results['success'].append(api_name)
                else:
                    results['failed'].append({
                        'api': api_name,
                        'error': result['error']
                    })
            except Exception as e:
                self.logger.error(f"API {api_name} 处理失败: {str(e)}")
                results['failed'].append({
                    'api': api_name,
                    'error': str(e)
                })
        
        # 重试失败的API
        if retry_failed and results['failed']:
            self.logger.info("重试失败的API...")
            failed_apis = results['failed'].copy()
            results['failed'] = []
            
            for failed_item in failed_apis:
                api_name = failed_item['api']
                api_config = enabled_apis[api_name]
                
                try:
                    result = self._persist_single_api(api_name, api_config, target_date)
                    if result['success']:
                        results['success'].append(api_name)
                    else:
                        results['failed'].append(failed_item)
                except Exception as e:
                    self.logger.error(f"API {api_name} 重试失败: {str(e)}")
                    results['failed'].append(failed_item)
        
        self.logger.info(f"持久化完成: 成功 {len(results['success'])}/{results['total_apis']}, "
                        f"失败 {len(results['failed'])}")
        
        return results
    
    def _get_enabled_apis(self) -> Dict[str, Any]:
        """获取启用的API配置"""
        enabled_apis = {}
        for api_name, api_config in self.config['apis'].items():
            if api_config.get('enabled', True):
                enabled_apis[api_name] = api_config
        return enabled_apis
    
    def _persist_single_api(self, api_name: str, api_config: Dict[str, Any], target_date: str) -> Dict[str, Any]:
        """持久化单个API数据"""
        self.logger.info(f"处理API: {api_name}")
        
        # 检查文件是否已存在
        output_file = self._get_output_file_path(api_name, api_config, target_date)
        if output_file.exists():
            self.logger.info(f"文件已存在，跳过: {output_file}")
            return {'success': True, 'skipped': True}
        
        # 获取数据
        data = self._fetch_api_data(api_name, api_config, target_date)
        
        if data is None or data.empty:
            self.logger.warning(f"API {api_name} 返回空数据")
            return {'success': True, 'skipped': True, 'reason': 'empty_data'}
        
        # 验证数据
        is_valid, errors = self.validator.validate_api_data(api_name, data)
        if not is_valid:
            self.logger.error(f"API {api_name} 数据验证失败: {errors}")
            return {'success': False, 'error': f"数据验证失败: {errors}"}
        
        # 保存数据
        try:
            self._save_data(data, output_file, api_config)
            self.logger.info(f"API {api_name} 数据保存成功: {len(data)} 条记录")
            return {'success': True, 'records': len(data)}
        except Exception as e:
            self.logger.error(f"API {api_name} 数据保存失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _fetch_api_data(self, api_name: str, api_config: Dict[str, Any], target_date: str) -> pd.DataFrame:
        """获取API数据"""
        method_name = api_config['method']

        if api_config.get('is_static', False):
            return self.api_client.call_static_method(method_name)
        elif api_config.get('is_range', False):
            # 只传递 start_dt, end_dt
            return self.api_client.call_range_method(method_name, target_date, target_date)
        else:
            # 使用封装的方法，它会处理特殊API的参数
            return self.api_client.call_single_method(method_name, target_date)
    
    def _get_output_file_path(self, api_name: str, api_config: Dict[str, Any], target_date: str) -> Path:
        """获取输出文件路径"""
        output_dir = self.output_dir / api_config['output_dir']
        output_dir.mkdir(parents=True, exist_ok=True)
        
        file_pattern = api_config['file_pattern']
        filename = file_pattern.format(date=target_date)
        
        return output_dir / filename
    
    def _save_data(self, data: pd.DataFrame, output_file: Path, api_config: Dict[str, Any]):
        """保存数据到文件"""
        # 确保目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 数据预处理：处理数据类型兼容性问题
        processed_data = self._preprocess_data_for_save(data)
        
        # 根据文件扩展名选择保存格式
        if output_file.suffix.lower() == '.parquet':
            processed_data.to_parquet(output_file, index=False)
        elif output_file.suffix.lower() == '.csv':
            processed_data.to_csv(output_file, index=False, encoding='utf-8')
        else:
            # 默认保存为parquet
            output_file = output_file.with_suffix('.parquet')
            processed_data.to_parquet(output_file, index=False)
    
    def _preprocess_data_for_save(self, data: pd.DataFrame) -> pd.DataFrame:
        """预处理数据以确保保存兼容性"""
        if data.empty:
            return data
        
        # 复制数据避免修改原始数据
        processed_data = data.copy()
        
        # 处理浮点数列中的 NaN 值
        float_columns = processed_data.select_dtypes(include=['float64', 'float32']).columns
        for col in float_columns:
            processed_data[col] = processed_data[col].fillna(0.0)
        
        # 处理对象类型列中的 NaN 值
        object_columns = processed_data.select_dtypes(include=['object']).columns
        for col in object_columns:
            processed_data[col] = processed_data[col].fillna('')
        
        # 处理整数列中的 NaN 值
        int_columns = processed_data.select_dtypes(include=['int64', 'int32']).columns
        for col in int_columns:
            processed_data[col] = processed_data[col].fillna(0)
        
        # 处理布尔列中的 NaN 值
        bool_columns = processed_data.select_dtypes(include=['bool']).columns
        for col in bool_columns:
            processed_data[col] = processed_data[col].fillna(False)
        
        # 确保所有字符串列都是字符串类型
        for col in processed_data.columns:
            if processed_data[col].dtype == 'object':
                processed_data[col] = processed_data[col].astype(str)
        
        return processed_data
    
    def persist_static_data(self) -> Dict[str, Any]:
        """持久化静态数据"""
        self.logger.info("开始持久化静态数据")
        
        results = {
            'success': [],
            'failed': [],
            'total_static_apis': 0
        }
        
        # 获取静态API
        static_apis = {name: config for name, config in self.config['apis'].items() 
                      if config.get('is_static', False) and config.get('enabled', True)}
        
        results['total_static_apis'] = len(static_apis)
        
        for api_name, api_config in static_apis.items():
            try:
                result = self._persist_static_api(api_name, api_config)
                if result['success']:
                    results['success'].append(api_name)
                else:
                    results['failed'].append({
                        'api': api_name,
                        'error': result['error']
                    })
            except Exception as e:
                self.logger.error(f"静态API {api_name} 处理失败: {str(e)}")
                results['failed'].append({
                    'api': api_name,
                    'error': str(e)
                })
        
        self.logger.info(f"静态数据持久化完成: 成功 {len(results['success'])}/{results['total_static_apis']}")
        
        return results
    
    def _persist_static_api(self, api_name: str, api_config: Dict[str, Any]) -> Dict[str, Any]:
        """持久化单个静态API数据"""
        self.logger.info(f"处理静态API: {api_name}")
        
        # 获取数据
        data = self.api_client.call_static_method(api_config['method'])
        
        if data is None or data.empty:
            self.logger.warning(f"静态API {api_name} 返回空数据")
            return {'success': False, 'error': '空数据'}
        
        # 验证数据
        is_valid, errors = self.validator.validate_api_data(api_name, data)
        if not is_valid:
            self.logger.error(f"静态API {api_name} 数据验证失败: {errors}")
            return {'success': False, 'error': f"数据验证失败: {errors}"}
        
        # 保存数据
        try:
            output_file = self._get_static_output_file_path(api_name, api_config)
            self._save_data(data, output_file, api_config)
            self.logger.info(f"静态API {api_name} 数据保存成功: {len(data)} 条记录")
            return {'success': True, 'records': len(data)}
        except Exception as e:
            self.logger.error(f"静态API {api_name} 数据保存失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_static_output_file_path(self, api_name: str, api_config: Dict[str, Any]) -> Path:
        """获取静态数据输出文件路径"""
        output_dir = self.output_dir / api_config['output_dir']
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 静态数据使用当前日期作为文件名
        current_date = datetime.now().strftime('%Y%m%d')
        file_pattern = api_config.get('file_pattern', '{date}.parquet')
        filename = file_pattern.format(date=current_date)
        
        return output_dir / filename 