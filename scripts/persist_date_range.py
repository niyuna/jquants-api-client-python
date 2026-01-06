#!/usr/bin/env python3
"""
日期范围数据持久化脚本（优化版）
支持指定日期范围，批量执行数据持久化，使用range调用减少API次数
"""

import warnings
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Tuple

# 抑制pandas FutureWarning关于DataFrame连接的警告
warnings.filterwarnings("ignore", category=FutureWarning, 
                       message=".*DataFrame concatenation with empty or all-NA entries.*")

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from scripts.utils.logger import setup_logger
from scripts.persist_data import main as persist_single_date


def persist_date_range_worker(args: Tuple[str, str, dict]) -> Tuple[str, str, bool, str]:
    """日期范围持久化工作函数"""
    start_date, end_date, config = args
    
    try:
        # 设置日志
        logger = logging.getLogger(f"persist_{start_date}_{end_date}")
        
        # 直接导入并使用DataPersister，避免修改sys.argv
        from scripts.utils.data_persister import DataPersister
        from scripts.utils.logger import setup_logger
        
        # 创建持久化器
        persister = DataPersister(
            config_path=config['config_path'],
            output_dir=config['output_dir'],
            logger=logger
        )
        
        # 执行批量持久化
        results = persister.persist_data_for_date_range(start_date, end_date, retry_failed=False)
        
        # 检查结果
        if results['failed']:
            error_msg = f"部分API失败: {len(results['failed'])} 个失败"
            return start_date, end_date, False, error_msg
        else:
            success_msg = f"成功处理 {len(results['success'])} 个API，跳过 {len(results['skipped'])} 个"
            if results['api_calls_saved'] > 0:
                success_msg += f"，节省 {results['api_calls_saved']} 次API调用"
            return start_date, end_date, True, success_msg
        
    except Exception as e:
        return start_date, end_date, False, str(e)


def chunk_date_range(start_date: str, end_date: str, chunk_size: int = 7) -> List[Tuple[str, str]]:
    """将日期范围分割成小块，避免单次请求过大"""
    try:
        start = datetime.strptime(start_date, '%Y%m%d')
        end = datetime.strptime(end_date, '%Y%m%d')
        
        chunks = []
        current_start = start
        
        while current_start <= end:
            current_end = min(current_start + timedelta(days=chunk_size-1), end)
            chunks.append((
                current_start.strftime('%Y%m%d'),
                current_end.strftime('%Y%m%d')
            ))
            current_start = current_end + timedelta(days=1)
        
        return chunks
    except ValueError as e:
        raise ValueError(f"日期格式错误: {e}")


def main():
    parser = argparse.ArgumentParser(description='日期范围数据持久化（优化版）')
    parser.add_argument(
        '--start-date',
        type=str,
        required=True,
        help='开始日期 (YYYYMMDD格式)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        required=True,
        help='结束日期 (YYYYMMDD格式)'
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
        '--max-workers',
        type=int,
        default=3,
        help='最大并行工作线程数 (默认: 3)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=7,
        help='每个chunk的日期数量 (默认: 7天)'
    )
    parser.add_argument(
        '--retry-failed',
        action='store_true',
        help='重试失败的日期范围'
    )
    parser.add_argument(
        '--skip-weekends',
        action='store_true',
        help='跳过周末 (周六和周日)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式，只显示将要处理的日期范围，不实际执行'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logger()
    logger.info(f"开始优化版日期范围持久化: {args.start_date} 到 {args.end_date}")
    
    try:
        # 生成日期范围chunks
        date_chunks = chunk_date_range(args.start_date, args.end_date, args.chunk_size)
        
        # 跳过周末
        if args.skip_weekends:
            filtered_chunks = []
            for start_date, end_date in date_chunks:
                # 检查chunk中是否包含工作日
                has_workday = False
                start = datetime.strptime(start_date, '%Y%m%d')
                end = datetime.strptime(end_date, '%Y%m%d')
                current = start
                while current <= end:
                    if current.weekday() < 5:  # 0-4 是周一到周五
                        has_workday = True
                        break
                    current += timedelta(days=1)
                
                if has_workday:
                    filtered_chunks.append((start_date, end_date))
            
            date_chunks = filtered_chunks
            logger.info(f"跳过纯周末chunks后，剩余 {len(date_chunks)} 个chunks")
        
        logger.info(f"总共需要处理 {len(date_chunks)} 个日期范围chunks")
        
        # 试运行模式
        if args.dry_run:
            logger.info("试运行模式 - 将要处理的日期范围:")
            for start_date, end_date in date_chunks:
                logger.info(f"  {start_date} - {end_date}")
            return
        
        # 准备配置
        config = {
            'config_path': args.config,
            'output_dir': args.output_dir
        }
        
        # 执行持久化
        success_count = 0
        failed_chunks = []
        total_api_calls_saved = 0
        
        if args.max_workers == 1:
            # 单线程执行
            logger.info("使用单线程模式执行")
            for start_date, end_date in date_chunks:
                logger.info(f"处理日期范围: {start_date} - {end_date}")
                start, end, success, message = persist_date_range_worker((start_date, end_date, config))
                if success:
                    success_count += 1
                    logger.info(f"日期范围 {start_date} - {end_date} 处理成功: {message}")
                else:
                    failed_chunks.append(((start_date, end_date), message))
                    logger.error(f"日期范围 {start_date} - {end_date} 处理失败: {message}")
        else:
            # 多线程执行
            logger.info(f"使用多线程模式执行，最大线程数: {args.max_workers}")
            
            with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
                # 提交所有任务
                future_to_chunk = {
                    executor.submit(persist_date_range_worker, (start_date, end_date, config)): (start_date, end_date)
                    for start_date, end_date in date_chunks
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_chunk):
                    start_date, end_date, success, message = future.result()
                    if success:
                        success_count += 1
                        logger.info(f"日期范围 {start_date} - {end_date} 处理成功: {message}")
                    else:
                        failed_chunks.append(((start_date, end_date), message))
                        logger.error(f"日期范围 {start_date} - {end_date} 处理失败: {message}")
        
        # 输出结果统计
        total_chunks = len(date_chunks)
        logger.info(f"日期范围持久化完成:")
        logger.info(f"  总chunks数: {total_chunks}")
        logger.info(f"  成功: {success_count}")
        logger.info(f"  失败: {len(failed_chunks)}")
        logger.info(f"  成功率: {success_count/total_chunks*100:.1f}%")
        
        if failed_chunks:
            logger.info("失败的日期范围:")
            for (start_date, end_date), error in failed_chunks:
                logger.info(f"  {start_date} - {end_date}: {error}")
            
            # 如果启用重试，重新处理失败的chunks
            if args.retry_failed and failed_chunks:
                logger.info("开始重试失败的日期范围...")
                retry_chunks = [(start_date, end_date) for (start_date, end_date), _ in failed_chunks]
                
                with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
                    future_to_chunk = {
                        executor.submit(persist_date_range_worker, (start_date, end_date, config)): (start_date, end_date)
                        for start_date, end_date in retry_chunks
                    }
                    
                    retry_success = 0
                    for future in as_completed(future_to_chunk):
                        start_date, end_date, success, message = future.result()
                        if success:
                            retry_success += 1
                            logger.info(f"重试成功: {start_date} - {end_date}")
                        else:
                            logger.error(f"重试失败: {start_date} - {end_date}: {message}")
                
                logger.info(f"重试结果: {retry_success}/{len(retry_chunks)} 成功")
        
    except Exception as e:
        logger.error(f"日期范围持久化失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 