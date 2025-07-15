#!/usr/bin/env python3
"""
J-Quants API 数据持久化脚本
支持指定日期拉取、配置化API选择、断点续传
"""

import argparse
import logging
from datetime import datetime, date
from pathlib import Path
import yaml

from utils.data_persister import DataPersister
from utils.logger import setup_logger

def parse_args():
    parser = argparse.ArgumentParser(description='J-Quants API 数据持久化')
    parser.add_argument(
        '--date', 
        type=str, 
        default=date.today().strftime('%Y%m%d'),
        help='拉取数据的日期 (YYYYMMDD格式，默认今天)'
    )
    parser.add_argument(
        '--config', 
        type=str, 
        default='config/api_config.yaml',
        help='API配置文件路径'
    )
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='persistdata',
        help='输出目录'
    )
    parser.add_argument(
        '--retry-failed', 
        action='store_true',
        help='重试之前失败的API'
    )
    parser.add_argument(
        '--update-static',
        action='store_true',
        help='更新静态数据（市场区分、业种分类等）'
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    # 设置日志
    logger = setup_logger()
    logger.info(f"开始持久化数据，日期: {args.date}")
    
    # 创建持久化器
    persister = DataPersister(
        config_path=args.config,
        output_dir=args.output_dir,
        logger=logger
    )
    
    # 执行持久化
    try:
        persister.persist_data_for_date(args.date, retry_failed=args.retry_failed)
        
        # 更新静态数据
        if args.update_static:
            persister.persist_static_data()
            
        logger.info("数据持久化完成")
    except Exception as e:
        logger.error(f"数据持久化失败: {e}")
        raise

if __name__ == "__main__":
    main() 