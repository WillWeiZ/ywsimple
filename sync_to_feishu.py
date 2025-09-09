#!/usr/bin/env python3
"""
修复版飞书同步脚本
解决字段名和数据类型问题
"""
import json
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
from data_processor import ExcelToFeishuProcessor
from feishu_config import APP_ID, APP_SECRET, BASE_URL, TABLE_ID


def fix_field_mapping(excel_fields):
    """修复字段映射和数据类型"""
    fixed_fields = {}
    
    # 字段名映射 (Excel -> 飞书)
    field_mapping = {
        'Sector/Theme': 'Sector|Theme',  # 关键修复
    }
    
    # 数字字段列表（字段类型2，需要保持数字类型）
    number_fields = {
        'Current Price', 'Market Cap (CNY bn)', 'Safe Buy Low', 'Safe Buy High', 
        'Extreme Safe', 'Target Low', 'Target High', 'Mid Target', 
        'Potential Upside %', 'Stop Loss'
    }
    
    # 文本字段（字段类型1，包括看起来像数字的PE和EPS字段）
    text_fields = {
        'Ticker', 'Name', 'Sector|Theme', 'PE (2025E)', 'EPS (2025E)', 
        'Source | Link', 'Notes', 'Last Updated'
    }
    
    for field_name, value in excel_fields.items():
        # 映射字段名
        feishu_field_name = field_mapping.get(field_name, field_name)
        
        # 处理空值
        if value is None or (isinstance(value, float) and str(value).lower() == 'nan'):
            if feishu_field_name in number_fields:
                fixed_value = 0  # 数字字段用0
            else:
                fixed_value = ""  # 文本字段用空字符串
        
        # 根据字段类型处理数据
        elif feishu_field_name in number_fields:
            # 数字字段：保持数字类型
            try:
                if isinstance(value, str):
                    fixed_value = float(value) if '.' in value else int(value)
                else:
                    fixed_value = float(value)
            except (ValueError, TypeError):
                fixed_value = 0
                
        elif feishu_field_name in text_fields:
            # 文本字段：转为字符串
            fixed_value = str(value)
        else:
            # 未知字段，默认转字符串
            fixed_value = str(value)
        
        fixed_fields[feishu_field_name] = fixed_value
    
    return fixed_fields


def sync_to_feishu_fixed():
    """修复版同步函数"""
    
    # 配置信息
    app_token = BASE_URL.split('/')[-1]
    table_id = TABLE_ID
    user_access_token = "u-duMNU3i9FcGrxiU3yP9lc_gl06sw058hhgG010a80evD"
    excel_path = "/Users/willmbp/Documents/2024/My_projects/Simple_YW/fromyouwei_updated.xlsx"
    
    print("🚀 开始修复版同步")
    
    # 创建客户端
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .enable_set_token(True) \
        .log_level(lark.LogLevel.INFO) \
        .build()
    
    option = lark.RequestOption.builder().user_access_token(user_access_token).build()
    
    try:
        # 1. 处理Excel数据
        print("\n📊 步骤1: 处理Excel数据")
        processor = ExcelToFeishuProcessor(excel_path)
        excel_records = processor.process_excel_to_feishu()
        print(f"   ✅ 原始记录: {len(excel_records)} 条")
        
        # 修复字段映射
        fixed_records = []
        for record in excel_records:
            original_fields = record.get('fields', {})
            fixed_fields = fix_field_mapping(original_fields)
            fixed_records.append({'fields': fixed_fields})
            
        print(f"   ✅ 修复后记录: {len(fixed_records)} 条")
        
        # 显示第一条记录的修复前后对比
        if excel_records:
            print("\n🔧 字段修复示例:")
            original = excel_records[0]['fields']
            fixed = fixed_records[0]['fields']
            
            print("   修复前 -> 修复后:")
            for key in ['Ticker', 'Name', 'Sector/Theme', 'PE (2025E)', 'Current Price']:
                if key in original:
                    mapped_key = 'Sector|Theme' if key == 'Sector/Theme' else key
                    print(f"   {key}: {original[key]} ({type(original[key])}) -> {mapped_key}: {fixed.get(mapped_key)} ({type(fixed.get(mapped_key))})")
        
        # 2. 获取现有记录
        print("\n📋 步骤2: 获取现有记录")
        list_request = ListAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .page_size(500) \
            .build()
            
        list_response = client.bitable.v1.app_table_record.list(list_request, option)
        
        if not list_response.success():
            print(f"   ❌ 获取失败: {list_response.code}, {list_response.msg}")
            return False
            
        existing_records = list_response.data.items or []
        print(f"   ✅ 获取到: {len(existing_records)} 条")
        
        # 3. 创建映射
        print("\n🗂️ 步骤3: 创建映射")
        existing_map = {}
        for record in existing_records:
            ticker = record.fields.get('Ticker')
            if ticker:
                existing_map[str(ticker)] = record.record_id
                
        print(f"   ✅ 映射: {len(existing_map)} 条")
        
        # 4. 更新记录
        print(f"\n🔄 步骤4: 更新记录")
        success_count = 0
        fail_count = 0
        
        for i, record in enumerate(fixed_records, 1):
            fixed_fields = record['fields']
            ticker = fixed_fields.get('Ticker', '')
            name = fixed_fields.get('Name', '未知')
            
            print(f"\n   处理 {i}/{len(fixed_records)}: {ticker} ({name})")
            
            if ticker in existing_map:
                record_id = existing_map[ticker]
                
                # 使用批量更新API
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
                    print(f"   ✅ 更新成功")
                else:
                    fail_count += 1
                    print(f"   ❌ 更新失败: {update_response.code} - {update_response.msg}")
                    
                    # 显示详细错误
                    if hasattr(update_response, 'raw') and update_response.raw:
                        try:
                            error_detail = json.loads(update_response.raw.content)
                            print(f"   🔍 错误详情: {error_detail.get('error', {}).get('message', '无详情')}")
                        except:
                            pass
            else:
                print(f"   ⚠️ 跳过: Ticker {ticker} 在飞书表格中不存在")
        
        # 5. 结果报告
        print(f"\n🎉 同步完成!")
        print(f"   ✅ 成功: {success_count} 条")
        print(f"   ❌ 失败: {fail_count} 条")
        print(f"   📊 总计: {len(fixed_records)} 条")
        
        return success_count > 0
        
    except Exception as e:
        print(f"\n❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = sync_to_feishu_fixed()
    if success:
        print("\n🎊 数据同步成功!")
    else:
        print("\n💥 数据同步失败!")