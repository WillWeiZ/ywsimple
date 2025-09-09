import requests
import json
import time
import os
from typing import Optional, Dict, Any
from feishu_config import APP_ID, APP_SECRET


class FeishuAuth:
    """飞书API认证类，负责token获取和管理"""
    
    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = app_id or APP_ID
        self.app_secret = app_secret or APP_SECRET
        self.tenant_access_token: Optional[str] = None
        self.token_expires_at: int = 0
        self.base_url = "https://open.feishu.cn/open-apis"
        
    def get_tenant_access_token(self, force_refresh: bool = False) -> str:
        """
        获取tenant_access_token
        
        Args:
            force_refresh: 是否强制刷新token
            
        Returns:
            str: tenant_access_token
            
        Raises:
            Exception: 当获取token失败时
        """
        # 检查token是否还有效（提前5分钟刷新）
        current_time = int(time.time())
        if (not force_refresh and 
            self.tenant_access_token and 
            current_time < self.token_expires_at - 300):
            return self.tenant_access_token
            
        # 请求新token
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('code') != 0:
                raise Exception(f"获取token失败: {result.get('msg', '未知错误')}")
                
            self.tenant_access_token = result['tenant_access_token']
            # token有效期为2小时，记录过期时间
            self.token_expires_at = current_time + result.get('expire', 7200)
            
            print(f"成功获取tenant_access_token，过期时间: {time.ctime(self.token_expires_at)}")
            return self.tenant_access_token
            
        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"响应解析失败: {str(e)}")
        except Exception as e:
            raise Exception(f"获取token时发生错误: {str(e)}")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        获取包含认证信息的请求头
        
        Returns:
            Dict[str, str]: 包含Authorization头的字典
        """
        token = self.get_tenant_access_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def is_token_valid(self) -> bool:
        """
        检查当前token是否有效
        
        Returns:
            bool: token是否有效
        """
        if not self.tenant_access_token:
            return False
            
        current_time = int(time.time())
        return current_time < self.token_expires_at - 300  # 提前5分钟判定过期
    
    def refresh_token(self) -> str:
        """
        强制刷新token
        
        Returns:
            str: 新的tenant_access_token
        """
        return self.get_tenant_access_token(force_refresh=True)


# 全局认证实例
feishu_auth = FeishuAuth()


def get_feishu_headers() -> Dict[str, str]:
    """
    便捷函数：获取飞书API请求头
    
    Returns:
        Dict[str, str]: 包含认证信息的请求头
    """
    return feishu_auth.get_auth_headers()


if __name__ == "__main__":
    # 测试认证功能
    auth = FeishuAuth()
    try:
        token = auth.get_tenant_access_token()
        print(f"获取到token: {token[:20]}...")
        
        headers = auth.get_auth_headers()
        print(f"认证头: Authorization: Bearer {headers['Authorization'][7:27]}...")
        
        print(f"Token有效性: {auth.is_token_valid()}")
        
    except Exception as e:
        print(f"认证测试失败: {e}")