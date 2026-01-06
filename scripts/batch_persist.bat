@echo off
REM 日期范围数据持久化批处理脚本（优化版）
REM 用法: batch_persist.bat [开始日期] [结束日期] [线程数] [chunk大小]

setlocal enabledelayedexpansion

REM 检查参数
if "%~1"=="" (
    echo 用法: batch_persist.bat [开始日期] [结束日期] [线程数] [chunk大小]
    echo 示例: batch_persist.bat 20240501 20240531 3 7
    echo 示例: batch_persist.bat 20240501 20240531 1 7 --skip-weekends
    exit /b 1
)

set START_DATE=%~1
set END_DATE=%~2
set MAX_WORKERS=%~3
set CHUNK_SIZE=%~4

REM 设置默认值
if "%MAX_WORKERS%"=="" set MAX_WORKERS=3
if "%CHUNK_SIZE%"=="" set CHUNK_SIZE=7

echo 开始优化版日期范围持久化
echo 开始日期: %START_DATE%
echo 结束日期: %END_DATE%
echo 最大线程数: %MAX_WORKERS%
echo Chunk大小: %CHUNK_SIZE%

REM 执行Python脚本
python scripts/persist_date_range.py --start-date %START_DATE% --end-date %END_DATE% --max-workers %MAX_WORKERS% --chunk-size %CHUNK_SIZE% %5 %6 %7 %8 %9

if %ERRORLEVEL% neq 0 (
    echo 执行失败，错误代码: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo 执行完成
pause 