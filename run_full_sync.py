#!/usr/bin/env python3
"""
完整的股票数据同步脚本
执行顺序：数据获取 -> 数据处理 -> 飞书同步
"""
import sys
import subprocess
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('full_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_command(command, description, cwd=None):
    """
    执行shell命令
    
    Args:
        command: 要执行的命令
        description: 命令描述
        cwd: 工作目录
        
    Returns:
        bool: 是否成功
    """
    logger.info(f"开始执行: {description}")
    logger.info(f"命令: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} 成功")
            if result.stdout:
                logger.info(f"输出: {result.stdout}")
            return True
        else:
            logger.error(f"❌ {description} 失败")
            logger.error(f"错误: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {description} 超时")
        return False
    except Exception as e:
        logger.error(f"❌ {description} 异常: {str(e)}")
        return False


def check_dependencies():
    """检查Python依赖"""
    logger.info("检查Python依赖...")
    
    required_packages = ['pandas', 'numpy', 'requests', 'openpyxl', 'akshare']
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} 已安装")
        except ImportError:
            logger.error(f"❌ {package} 未安装")
            logger.info(f"请运行: pip install {package}")
            return False
    
    return True


def main():
    """主执行流程"""
    start_time = datetime.now()
    logger.info("=" * 50)
    logger.info("开始完整的股票数据同步流程")
    logger.info(f"开始时间: {start_time}")
    logger.info("=" * 50)
    
    success_steps = 0
    total_steps = 5
    
    try:
        # 步骤1: 检查依赖
        if check_dependencies():
            success_steps += 1
        else:
            logger.error("依赖检查失败，退出")
            return False
        
        # 步骤2: 获取股票价格数据
        if run_command("python get_price.py", "获取股票价格数据", cwd="get_data"):
            success_steps += 1
        else:
            logger.error("获取价格数据失败")
            return False
        
        # 步骤3: 获取EPS数据
        if run_command("python get_EPS.py", "获取EPS预测数据", cwd="get_data"):
            success_steps += 1
        else:
            logger.error("获取EPS数据失败")
            return False
        
        # 步骤4: 处理Excel数据
        if run_command("python fill_excel_data.py", "处理Excel数据"):
            success_steps += 1
        else:
            logger.error("处理Excel数据失败")
            return False
        
        # 步骤5: 同步到飞书
        if run_command("python sync_to_feishu.py", "同步数据到飞书"):
            success_steps += 1
        else:
            logger.error("同步到飞书失败")
            return False
            
        # 完成
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("=" * 50)
        logger.info("🎉 完整的数据同步流程执行成功！")
        logger.info(f"成功步骤: {success_steps}/{total_steps}")
        logger.info(f"总用时: {duration.total_seconds():.2f}秒")
        logger.info("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"执行过程中发生异常: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)