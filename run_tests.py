#!/usr/bin/env python3
"""
测试运行脚本
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """运行所有测试"""
    # 添加scripts目录到路径
    scripts_dir = Path(__file__).parent / 'scripts'
    sys.path.insert(0, str(scripts_dir))
    
    # 运行测试
    test_dir = Path(__file__).parent / 'tests'
    
    # 运行pytest
    cmd = [
        sys.executable, '-m', 'pytest',
        str(test_dir),
        '-v',
        '--tb=short',
        '--cov=scripts',
        '--cov-report=html:htmlcov',
        '--cov-report=term-missing'
    ]
    
    print("运行测试...")
    print(f"命令: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)

if __name__ == '__main__':
    run_tests() 