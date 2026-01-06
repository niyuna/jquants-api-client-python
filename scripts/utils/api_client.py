"""
J-Quants API客户端封装
"""

import warnings
from datetime import datetime
from typing import Optional, Union
import pandas as pd
from jquantsapi import Client

class JQuantsAPIClient:
    def __init__(self):
        self.client = Client()
    
    def call_range_method(self, method_name: str, start_date: str, end_date: str) -> pd.DataFrame:
        """调用范围查询方法"""
        print(f"[{method_name}] 开始调用范围查询方法，日期范围: {start_date} - {end_date}")
        
        method = getattr(self.client, method_name)
        
        # 转换日期格式
        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)
        
        # 抑制pandas FutureWarning
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning, 
                                  message=".*DataFrame concatenation with empty or all-NA entries.*")
            result = method(start_dt=start_dt, end_dt=end_dt)
            
        # 处理API返回字符串错误的情况
        if isinstance(result, str):
            print(f"[{method_name}] 警告: API返回错误消息: {result}")
            return pd.DataFrame()
        
        print(f"[{method_name}] 范围查询完成，返回数据行数: {len(result)}")
        return result
    
    def call_single_method(self, method_name: str, target_date: str) -> pd.DataFrame:
        """调用单日查询方法"""
        print(f"[{method_name}] 开始调用单日查询方法，目标日期: {target_date}")
        
        method = getattr(self.client, method_name)
        
        # 转换日期格式
        date_obj = self._parse_date(target_date)
        
        # 根据方法名调用不同的参数
        if method_name == 'get_listed_info':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_fins_announcement':
            result = method()  # 公告API不需要日期参数
        elif method_name == 'get_markets_trades_spec':
            result = method(from_yyyymmdd=target_date, to_yyyymmdd=target_date)
        elif method_name == 'get_indices':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_indices_topix':
            result = method(from_yyyymmdd=target_date, to_yyyymmdd=target_date)
        elif method_name == 'get_option_index_option':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_markets_weekly_margin_interest':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_markets_short_selling':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_markets_breakdown':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_prices_prices_am':
            result = method()  # 前场行情API不需要日期参数
        elif method_name == 'get_fins_dividend':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_fins_statements':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_fins_fs_details':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_derivatives_futures':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_derivatives_options':
            result = method(date_yyyymmdd=target_date)
        elif method_name == 'get_markets_short_selling_positions':
            result = method(calculated_date=target_date)
        else:
            result = method(date_yyyymmdd=target_date)
        
        # 处理API返回字符串错误的情况
        if isinstance(result, str):
            print(f"[{method_name}] 警告: API返回错误消息: {result}")
            return pd.DataFrame()
        
        print(f"[{method_name}] 单日查询完成，返回数据行数: {len(result)}")
        return result
    
    def call_static_method(self, method_name: str) -> pd.DataFrame:
        """调用静态数据方法"""
        print(f"[{method_name}] 开始调用静态数据方法")
        
        method = getattr(self.client, method_name)
        result = method()
        
        # 处理API返回字符串错误的情况
        if isinstance(result, str):
            print(f"[{method_name}] 警告: API返回错误消息: {result}")
            return pd.DataFrame()
        
        print(f"[{method_name}] 静态数据查询完成，返回数据行数: {len(result)}")
        return result
    
    def _parse_date(self, date_str: str) -> Union[datetime, str]:
        """解析日期字符串"""
        try:
            # 确保返回pd.Timestamp类型
            return pd.to_datetime(date_str, format='%Y%m%d')
        except ValueError:
            return date_str 