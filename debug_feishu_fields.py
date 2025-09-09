#!/usr/bin/env python3
"""
调试脚本：获取飞书表格的字段信息
"""
import os
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import ListAppTableFieldRequest
from feishu_config import APP_ID, APP_SECRET, BASE_URL, TABLE_ID

def debug_feishu_fields():
    """获取并显示飞书表格的字段信息"""
    
    # 配置
    user_access_token = "u-duMNU3i9FcGrxiU3yP9lc_gl06sw058hhgG010a80evD"
    app_token = BASE_URL.split('/')[-1]
    table_id = TABLE_ID
    
    print("🔍 调试飞书表格字段信息")
    print(f"App Token: {app_token}")
    print(f"Table ID: {table_id}")
    
    # 创建客户端
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .enable_set_token(True) \
        .build()
    
    option = lark.RequestOption.builder().user_access_token(user_access_token).build()
    
    try:
        # 获取字段信息
        field_request = ListAppTableFieldRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .build()
        
        field_response = client.bitable.v1.app_table_field.list(field_request, option)
        
        if field_response.success():
            fields = field_response.data.items or []
            print(f"\n📋 飞书表格字段 (共{len(fields)}个):")
            for i, field in enumerate(fields, 1):
                print(f"{i:2d}. 字段名: '{field.field_name}' | 字段ID: {field.field_id} | 类型: {field.type}")
        else:
            print(f"❌ 获取字段失败: {field_response.code} - {field_response.msg}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_feishu_fields()