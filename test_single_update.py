#!/usr/bin/env python3
"""
测试脚本：更新单条飞书记录
"""
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import BatchUpdateAppTableRecordRequest, BatchUpdateAppTableRecordRequestBody, AppTableRecord
from feishu_config import APP_ID, APP_SECRET, BASE_URL, TABLE_ID
from datetime import datetime, timezone, timedelta

def test_single_update():
    """测试更新单条记录"""
    
    # 配置
    user_access_token = "u-duMNU3i9FcGrxiU3yP9lc_gl06sw058hhgG010a80evD"
    app_token = BASE_URL.split('/')[-1]
    table_id = TABLE_ID
    
    print("🧪 测试单条记录更新")
    
    # 创建客户端
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .enable_set_token(True) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()
    
    option = lark.RequestOption.builder().user_access_token(user_access_token).build()
    
    try:
        # 准备更新数据 - 只更新Last Updated字段
        beijing_tz = timezone(timedelta(hours=8))
        beijing_time = datetime.now(beijing_tz)
        time_str = beijing_time.strftime('%Y-%m-%d %H:%M:%S CST')
        
        # 使用第一条记录的ID
        record_id = "rec25ORoaS06hp"  # 通富微电
        
        fields = {
            "Last Updated": time_str
        }
        
        print(f"更新记录: {record_id}")
        print(f"更新字段: {fields}")
        
        # 执行更新
        update_request = BatchUpdateAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .request_body(BatchUpdateAppTableRecordRequestBody.builder()
                .records([
                    AppTableRecord.builder()
                        .record_id(record_id)
                        .fields(fields)
                        .build()
                ])
                .build()) \
            .build()
        
        update_response = client.bitable.v1.app_table_record.batch_update(update_request, option)
        
        if update_response.success():
            print(f"✅ 更新成功!")
            print(f"响应: {update_response.data}")
        else:
            print(f"❌ 更新失败: {update_response.code} - {update_response.msg}")
            print(f"Raw response: {update_response.raw}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_update()