#!/usr/bin/env python3
"""
完整的股票数据同步脚本 - 单文件版本
包含：数据获取 -> 数据处理 -> 飞书同步
直接调用函数，避免subprocess的网络问题
"""

import akshare as ak
import pandas as pd
import numpy as np
import requests
import json
import time
import os
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('complete_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 飞书应用配置
APP_ID = "cli_a8351c888cac9013"
APP_SECRET = "gIcB8ViEFF478MsW0cJQ2efsLUtNrzZa"
BASE_URL = "https://ydetzdeqyc.feishu.cn/base/U3iYbe8cGaBrLEso6jMctMVgnVb"
TABLE_ID = "tbl29O0osz3dn74L"

# 文件路径配置
EXCEL_FILE = 'fromyouwei.xlsx'
UPDATED_EXCEL_FILE = 'fromyouwei_updated.xlsx'
PRICE_DATA_FILE = 'data/all_stock_price.csv'
EPS_DATA_FILE = 'data/股票代码_EPS.csv'


class FeishuAuth:
    """飞书API认证类，负责token获取和管理"""
    
    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = app_id or APP_ID
        self.app_secret = app_secret or APP_SECRET
        self.tenant_access_token: Optional[str] = None
        self.token_expires_at: int = 0
        self.base_url = "https://open.feishu.cn/open-apis"
        
    def get_tenant_access_token(self, force_refresh: bool = False) -> str:
        """获取tenant_access_token"""
        current_time = int(time.time())
        if (not force_refresh and 
            self.tenant_access_token and 
            current_time < self.token_expires_at - 300):
            return self.tenant_access_token
            
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"获取token失败: {result.get('msg', 'Unknown error')}")
            
            self.tenant_access_token = result["tenant_access_token"]
            expires_in = result.get("expire", 7200)
            self.token_expires_at = current_time + expires_in
            
            logger.info(f"✅ 成功获取token，有效期: {expires_in}秒")
            return self.tenant_access_token
            
        except Exception as e:
            logger.error(f"❌ 获取token失败: {str(e)}")
            raise


def get_stock_price_data_with_retry(max_retries=3, delay=2):
    """带重试机制的股票价格数据获取"""
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试获取股票数据 (第{attempt + 1}/{max_retries}次)...")
            stock_df = ak.stock_zh_a_spot_em()
            logger.info(f"成功获取{len(stock_df)}条股票数据")
            return stock_df
        
        except Exception as e:
            logger.error(f"第{attempt + 1}次获取失败: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"等待{delay}秒后重试...")
                time.sleep(delay)
                delay *= 2
            else:
                logger.error("所有重试都失败了")
                raise e


def get_eps_data_with_retry(stock_code, max_retries=3, delay=1):
    """带重试机制的EPS数据获取"""
    for attempt in range(max_retries):
        try:
            stock_df = ak.stock_profit_forecast_ths(symbol=stock_code, indicator="预测年报每股收益")
            stock_df['股票代码'] = stock_code
            return stock_df
        
        except Exception as e:
            logger.warning(f"股票 {stock_code} 第{attempt + 1}次获取失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 1.5
            else:
                logger.warning(f"股票 {stock_code} 所有重试都失败了")
                return pd.DataFrame()


def step1_get_stock_price():
    """步骤1: 获取股票价格数据"""
    logger.info("=" * 50)
    logger.info("步骤1: 获取股票价格数据")
    logger.info("=" * 50)
    
    # 检查是否已有数据文件
    if os.path.exists(PRICE_DATA_FILE):
        logger.info(f"✅ 发现已存在的价格数据文件: {PRICE_DATA_FILE}")
        try:
            df_check = pd.read_csv(PRICE_DATA_FILE)
            logger.info(f"✅ 使用现有价格数据 ({len(df_check)} 条记录)")
            return True
        except Exception as e:
            logger.warning(f"⚠️ 现有数据文件损坏，重新获取: {e}")
    
    try:
        os.makedirs('data', exist_ok=True)
        stock_zh_a_spot_em_df = get_stock_price_data_with_retry()
        stock_zh_a_spot_em_df.to_csv(PRICE_DATA_FILE, index=False)
        logger.info(f"✅ 股票价格数据已保存到: {PRICE_DATA_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 获取股票价格数据失败: {str(e)}")
        return False


def step2_get_eps_data():
    """步骤2: 获取EPS数据"""
    logger.info("=" * 50)
    logger.info("步骤2: 获取EPS预测数据")
    logger.info("=" * 50)
    
    # 检查是否已有EPS数据文件
    if os.path.exists(EPS_DATA_FILE):
        logger.info(f"✅ 发现已存在的EPS数据文件: {EPS_DATA_FILE}")
        try:
            df_check = pd.read_csv(EPS_DATA_FILE)
            logger.info(f"✅ 使用现有EPS数据 ({len(df_check)} 条记录)")
            return True
        except Exception as e:
            logger.warning(f"⚠️ 现有EPS数据文件损坏，重新获取: {e}")
    
    stock_list = ['002156', '002837', '300229', '600249', '002230', '688111', '603019', '300496', '600519']
    
    all_stocks_esp_df = pd.DataFrame()
    successful_count = 0
    
    for i, stock_code in enumerate(stock_list):
        logger.info(f"正在处理股票 {stock_code} ({i+1}/{len(stock_list)})...")
        
        try:
            stock_data = get_eps_data_with_retry(stock_code)
            
            if not stock_data.empty:
                all_stocks_esp_df = pd.concat([all_stocks_esp_df, stock_data], ignore_index=True)
                successful_count += 1
                logger.info(f"✅ 成功获取股票 {stock_code} 的预测每股收益数据")
            else:
                logger.warning(f"⚠️ 股票 {stock_code} 数据获取失败，跳过")
            
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"❌ 获取股票 {stock_code} 数据时出现异常: {e}")
    
    if not all_stocks_esp_df.empty:
        all_stocks_esp_df.to_csv(EPS_DATA_FILE, index=False, encoding='utf-8-sig')
        logger.info(f"✅ EPS数据已保存到: {EPS_DATA_FILE}")
        logger.info(f"📊 共处理了 {len(stock_list)} 只股票，成功获取 {successful_count} 只股票的数据，总计 {len(all_stocks_esp_df)} 条记录")
        return True
    else:
        logger.error("❌ 没有获取到任何EPS数据")
        return False


def step3_process_excel_data():
    """步骤3: 处理Excel数据"""
    logger.info("=" * 50)
    logger.info("步骤3: 处理Excel数据，计算财务指标")
    logger.info("=" * 50)
    
    try:
        # 读取Excel文件
        df_excel = pd.read_excel(EXCEL_FILE)
        logger.info(f"读取Excel文件: {len(df_excel)} 行数据")
        
        # 读取股票价格数据
        df_price = pd.read_csv(PRICE_DATA_FILE)
        df_price['代码'] = df_price['代码'].astype(str).str.zfill(6)
        
        # 读取EPS数据
        df_eps = pd.read_csv(EPS_DATA_FILE)
        df_eps_2025 = df_eps[df_eps['年度'] == 2025].copy()
        df_eps_2025['股票代码'] = df_eps_2025['股票代码'].astype(str).str.zfill(6)
        
        # 创建查找字典
        price_dict = dict(zip(df_price['代码'], df_price['最新价']))
        market_cap_dict = dict(zip(df_price['代码'], df_price['总市值']))
        eps_dict = dict(zip(df_eps_2025['股票代码'], df_eps_2025['均值']))
        
        # 处理每一行
        def process_row(row):
            ticker = str(row['Ticker'])[:6]
            
            # 获取数据
            current_price = price_dict.get(ticker, np.nan)
            eps_mean = eps_dict.get(ticker, np.nan)
            
            # 计算指标
            pe_2025e = current_price / eps_mean if eps_mean and eps_mean != 0 and not np.isnan(eps_mean) else np.nan
            market_cap = market_cap_dict.get(ticker, np.nan)
            market_cap_bn = market_cap / 100000000 if not np.isnan(market_cap) else np.nan
            
            target_low = row['Target Low']
            target_high = row['Target High']
            mid_target = (target_low + target_high) / 2 if not np.isnan(target_low) and not np.isnan(target_high) else np.nan
            potential_upside = round((mid_target / current_price - 1) * 100, 1) if not np.isnan(current_price) and not np.isnan(mid_target) and current_price != 0 else np.nan
            
            # 更新行数据
            row['Current Price'] = current_price
            row['EPS (2025E)'] = eps_mean
            row['PE (2025E)'] = pe_2025e
            row['Market Cap (CNY bn)'] = market_cap_bn
            row['Mid Target'] = mid_target
            row['Potential Upside %'] = potential_upside
            # 添加Last Updated字段 - 使用北京时间
            from datetime import timezone, timedelta
            beijing_tz = timezone(timedelta(hours=8))
            beijing_time = datetime.now(beijing_tz)
            row['Last Updated'] = beijing_time.strftime('%Y-%m-%d %H:%M:%S CST')
            
            return row
        
        # 应用处理函数
        df_excel = df_excel.apply(process_row, axis=1)
        
        # 保存更新后的Excel文件
        df_excel.to_excel(UPDATED_EXCEL_FILE, index=False)
        logger.info(f"✅ Excel文件已成功更新并保存到: {UPDATED_EXCEL_FILE}")
        logger.info(f"处理了 {len(df_excel)} 行数据")
        return True
        
    except Exception as e:
        logger.error(f"❌ 处理Excel数据失败: {str(e)}")
        return False


def step4_sync_to_feishu():
    """步骤4: 同步到飞书"""
    logger.info("=" * 50)
    logger.info("步骤4: 同步数据到飞书")
    logger.info("=" * 50)
    
    try:
        # 检查是否有user_access_token环境变量
        user_access_token = os.getenv('FEISHU_USER_TOKEN')
        if not user_access_token:
            logger.warning("⚠️ 未设置FEISHU_USER_TOKEN环境变量，跳过飞书同步")
            logger.info("💡 要启用飞书同步，请设置环境变量: export FEISHU_USER_TOKEN=your_token")
            return True
        
        # 导入飞书API
        try:
            import lark_oapi as lark
            from lark_oapi.api.bitable.v1 import (
                ListAppTableRecordRequest, BatchUpdateAppTableRecordRequest,
                BatchUpdateAppTableRecordRequestBody, AppTableRecord
            )
        except ImportError:
            logger.error("❌ 缺少lark_oapi依赖，请运行: pip install lark_oapi")
            return False
        
        # 读取处理后的Excel数据
        df = pd.read_excel(UPDATED_EXCEL_FILE)
        logger.info(f"读取更新后的Excel数据: {len(df)} 行")
        
        # 飞书配置
        app_token = BASE_URL.split('/')[-1]
        table_id = TABLE_ID
        
        logger.info("🔗 创建飞书客户端")
        client = lark.Client.builder() \
            .app_id(APP_ID) \
            .app_secret(APP_SECRET) \
            .enable_set_token(True) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        
        option = lark.RequestOption.builder().user_access_token(user_access_token).build()
        
        # 数据处理函数
        def fix_field_mapping(excel_fields):
            """修复字段映射和数据类型"""
            fixed_fields = {}
            
            field_mapping = {
                'Sector/Theme': 'Sector|Theme',
                'Source / Link': 'Source | Link',
            }
            
            number_fields = {
                'Current Price', 'Market Cap (CNY bn)', 'Safe Buy Low', 'Safe Buy High', 
                'Extreme Safe', 'Target Low', 'Target High', 'Mid Target', 
                'Potential Upside %', 'Stop Loss'
            }
            
            text_fields = {
                'Ticker', 'Name', 'Sector|Theme', 'PE (2025E)', 'EPS (2025E)', 
                'Source | Link', 'Notes', 'Last Updated'
            }
            
            for field_name, value in excel_fields.items():
                feishu_field_name = field_mapping.get(field_name, field_name)
                
                if value is None or (isinstance(value, float) and str(value).lower() == 'nan'):
                    if feishu_field_name in number_fields:
                        fixed_value = 0
                    else:
                        fixed_value = ""
                elif feishu_field_name in number_fields:
                    try:
                        if isinstance(value, str):
                            fixed_value = float(value) if '.' in value else int(value)
                        else:
                            fixed_value = float(value)
                    except (ValueError, TypeError):
                        fixed_value = 0
                elif feishu_field_name in text_fields:
                    fixed_value = str(value)
                else:
                    fixed_value = str(value)
                
                fixed_fields[feishu_field_name] = fixed_value
            
            return fixed_fields
        
        # 转换Excel数据为飞书格式
        excel_records = []
        for _, row in df.iterrows():
            fields = {}
            for col in df.columns:
                value = row[col]
                # 处理NaN和None值
                if pd.isna(value) or value is None:
                    fields[col] = ""
                elif isinstance(value, float) and str(value).lower() == 'nan':
                    fields[col] = ""
                else:
                    fields[col] = value
            excel_records.append({'fields': fields})
        
        # 修复字段映射
        fixed_records = []
        for record in excel_records:
            original_fields = record.get('fields', {})
            fixed_fields = fix_field_mapping(original_fields)
            fixed_records.append({'fields': fixed_fields})
        
        logger.info(f"📝 处理了 {len(fixed_records)} 条记录")
        
        # 获取现有记录
        logger.info("📋 获取现有飞书记录")
        list_request = ListAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .page_size(500) \
            .build()
            
        list_response = client.bitable.v1.app_table_record.list(list_request, option)
        
        if not list_response.success():
            logger.error(f"❌ 获取飞书记录失败: {list_response.code}, {list_response.msg}")
            return False
            
        existing_records = list_response.data.items or []
        logger.info(f"📋 获取到飞书记录: {len(existing_records)} 条")
        
        # 创建映射
        existing_map = {}
        for record in existing_records:
            ticker = record.fields.get('Ticker')
            if ticker:
                existing_map[str(ticker)] = record.record_id
        
        logger.info(f"🗂️ 创建映射: {len(existing_map)} 条")
        
        # 更新记录
        logger.info("🔄 开始更新记录")
        success_count = 0
        fail_count = 0
        
        for i, record in enumerate(fixed_records, 1):
            fixed_fields = record['fields']
            ticker = fixed_fields.get('Ticker', '')
            name = fixed_fields.get('Name', '未知')
            
            logger.info(f"处理 {i}/{len(fixed_records)}: {ticker} ({name})")
            
            if ticker in existing_map:
                record_id = existing_map[ticker]
                
                update_request = BatchUpdateAppTableRecordRequest.builder() \
                    .app_token(app_token) \
                    .table_id(table_id) \
                    .request_body(BatchUpdateAppTableRecordRequestBody.builder()
                        .records([
                            AppTableRecord.builder()
                                .record_id(record_id)
                                .fields(fixed_fields)
                                .build()
                        ])
                        .build()) \
                    .build()
                
                update_response = client.bitable.v1.app_table_record.batch_update(update_request, option)
                
                if update_response.success():
                    success_count += 1
                    logger.info(f"  ✅ 更新成功")
                else:
                    fail_count += 1
                    logger.error(f"  ❌ 更新失败: {update_response.code} - {update_response.msg}")
            else:
                logger.warning(f"  ⚠️ 跳过: Ticker {ticker} 在飞书表格中不存在")
        
        # 结果报告
        logger.info("🎉 飞书同步完成!")
        logger.info(f"✅ 成功: {success_count} 条")
        logger.info(f"❌ 失败: {fail_count} 条")
        logger.info(f"📊 总计: {len(fixed_records)} 条")
        
        return success_count > 0
        
    except Exception as e:
        logger.error(f"❌ 同步到飞书失败: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False


def main():
    """主执行流程"""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("🚀 开始完整的股票数据同步流程")
    logger.info(f"开始时间: {start_time}")
    logger.info("=" * 60)
    
    success_steps = 0
    total_steps = 4
    
    try:
        # 步骤1: 获取股票价格数据
        if step1_get_stock_price():
            success_steps += 1
        else:
            logger.error("获取价格数据失败，终止流程")
            return False
        
        # 步骤2: 获取EPS数据
        if step2_get_eps_data():
            success_steps += 1
        else:
            logger.error("获取EPS数据失败，终止流程")
            return False
        
        # 步骤3: 处理Excel数据
        if step3_process_excel_data():
            success_steps += 1
        else:
            logger.error("处理Excel数据失败，终止流程")
            return False
        
        # 步骤4: 同步到飞书
        if step4_sync_to_feishu():
            success_steps += 1
        else:
            logger.error("同步到飞书失败，终止流程")
            return False
        
        # 完成
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("=" * 60)
        logger.info("🎉 完整的数据同步流程执行成功！")
        logger.info(f"成功步骤: {success_steps}/{total_steps}")
        logger.info(f"总用时: {duration.total_seconds():.2f}秒")
        logger.info(f"结束时间: {end_time}")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"执行过程中发生异常: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)