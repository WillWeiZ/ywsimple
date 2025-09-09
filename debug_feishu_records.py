#!/usr/bin/env python3
"""
调试脚本：获取飞书表格的记录信息
"""
import os
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import ListAppTableRecordRequest
from feishu_config import APP_ID, APP_SECRET, BASE_URL, TABLE_ID

def debug_feishu_records():
    """获取并显示飞书表格的记录信息"""
    
    # 配置
    user_access_token = "u-duMNU3i9FcGrxiU3yP9lc_gl06sw058hhgG010a80evD"
    app_token = BASE_URL.split('/')[-1]
    table_id = TABLE_ID
    
    print("🔍 调试飞书表格记录信息")
    
    # 创建客户端
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .enable_set_token(True) \
        .build()
    
    option = lark.RequestOption.builder().user_access_token(user_access_token).build()
    
    try:
        # 获取记录
        list_request = ListAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .page_size(5) \
            .build()
            
        list_response = client.bitable.v1.app_table_record.list(list_request, option)
        
        if list_response.success():
            records = list_response.data.items or []
            print(f"\n📋 飞书表格记录 (显示前5条，共{len(records)}条):")
            
            for i, record in enumerate(records, 1):
                print(f"\n记录 {i}:")
                print(f"  Record ID: {record.record_id}")
                print(f"  字段内容:")
                
                for field_name, field_value in record.fields.items():
                    print(f"    {field_name}: {field_value}")
                    
        else:
            print(f"❌ 获取记录失败: {list_response.code} - {list_response.msg}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_feishu_records()