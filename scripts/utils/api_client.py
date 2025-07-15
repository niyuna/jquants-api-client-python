"""
J-Quants API客户端封装
"""

from datetime import datetime
from typing import Optional, Union
import pandas as pd
from jquantsapi import Client

class JQuantsAPIClient:
    def __init__(self):
        self.client = Client()
    
    def call_range_method(self, method_name: str, start_date: str, end_date: str) -> pd.DataFrame:
        """调用范围查询方法"""
        method = getattr(self.client, method_name)
        
        # 转换日期格式
        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)
        
        return method(start_dt=start_dt, end_dt=end_dt)
    
    def call_single_method(self, method_name: str, target_date: str) -> pd.DataFrame:
        """调用单日查询方法"""
        method = getattr(self.client, method_name)
        
        # 转换日期格式
        date_obj = self._parse_date(target_date)
        
        # 根据方法名调用不同的参数
        if method_name == 'get_listed_info':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_fins_announcement':
            return method()  # 公告API不需要日期参数
        elif method_name == 'get_markets_trades_spec':
            return method(from_yyyymmdd=target_date, to_yyyymmdd=target_date)
        elif method_name == 'get_indices':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_indices_topix':
            return method(from_yyyymmdd=target_date, to_yyyymmdd=target_date)
        elif method_name == 'get_option_index_option':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_markets_weekly_margin_interest':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_markets_short_selling':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_markets_breakdown':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_prices_prices_am':
            return method()  # 前场行情API不需要日期参数
        elif method_name == 'get_fins_dividend':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_fins_statements':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_fins_fs_details':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_derivatives_futures':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_derivatives_options':
            return method(date_yyyymmdd=target_date)
        elif method_name == 'get_markets_short_selling_positions':
            return method(calculated_date=target_date)
        else:
            return method(date_yyyymmdd=target_date)
    
    def call_static_method(self, method_name: str) -> pd.DataFrame:
        """调用静态数据方法"""
        method = getattr(self.client, method_name)
        return method()
    
    def _parse_date(self, date_str: str) -> Union[datetime, str]:
        """解析日期字符串"""
        try:
            # 确保返回pd.Timestamp类型
            return pd.to_datetime(date_str, format='%Y%m%d')
        except ValueError:
            return date_str 