import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class ExcelToFeishuProcessor:
    """Excel数据处理器，负责将Excel数据转换为飞书API格式"""
    
    def __init__(self, excel_path: str):
        """
        初始化处理器
        
        Args:
            excel_path: Excel文件路径
        """
        self.excel_path = excel_path
        self.df: Optional[pd.DataFrame] = None
        
    def load_excel(self) -> pd.DataFrame:
        """
        加载Excel文件
        
        Returns:
            pd.DataFrame: 加载的数据框
            
        Raises:
            Exception: 当文件读取失败时
        """
        try:
            self.df = pd.read_excel(self.excel_path)
            print(f"成功加载Excel文件，共{len(self.df)}行数据")
            return self.df
        except Exception as e:
            raise Exception(f"加载Excel文件失败: {str(e)}")
    
    def clean_data(self) -> pd.DataFrame:
        """
        清理数据
        
        Returns:
            pd.DataFrame: 清理后的数据框
        """
        if self.df is None:
            raise Exception("请先加载Excel文件")
            
        # 创建数据副本
        cleaned_df = self.df.copy()
        
        # 处理NaN值
        cleaned_df = cleaned_df.fillna("")
        
        # 确保数值列的数据类型正确
        numeric_columns = [
            'Current Price', 'PE (2025E)', 'EPS (2025E)', 'Market Cap (CNY bn)',
            'Safe Buy Low', 'Safe Buy High', 'Extreme Safe', 'Target Low', 
            'Target High', 'Mid Target', 'Potential Upside %', 'Stop Loss'
        ]
        
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0)
        
        # 添加更新时间戳
        cleaned_df['Last Updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"数据清理完成，处理了{len(cleaned_df)}行数据")
        return cleaned_df
    
    def convert_to_feishu_records(self, cleaned_df: pd.DataFrame = None) -> List[Dict[str, Any]]:
        """
        将DataFrame转换为飞书API记录格式
        
        Args:
            cleaned_df: 清理后的数据框，如果为None则使用内部数据
            
        Returns:
            List[Dict[str, Any]]: 飞书API记录格式的数据列表
        """
        if cleaned_df is None:
            if self.df is None:
                raise Exception("请先加载Excel文件")
            cleaned_df = self.clean_data()
        
        records = []
        
        for index, row in cleaned_df.iterrows():
            # 构建飞书记录格式
            record = {
                "fields": {}
            }
            
            # 遍历所有列，转换为飞书字段格式
            for column in cleaned_df.columns:
                value = row[column]
                
                # 根据数据类型转换值
                if pd.isna(value) or value == "":
                    record["fields"][column] = ""
                elif isinstance(value, (int, np.integer)):
                    record["fields"][column] = int(value)
                elif isinstance(value, (float, np.floating)):
                    # 特殊处理百分比和小数
                    if column == 'Potential Upside %':
                        record["fields"][column] = round(float(value), 1)
                    else:
                        record["fields"][column] = round(float(value), 6) if value != 0 else 0
                else:
                    record["fields"][column] = str(value)
            
            records.append(record)
        
        print(f"成功转换{len(records)}条记录为飞书格式")
        return records
    
    def get_field_mapping(self) -> Dict[str, str]:
        """
        获取字段映射关系（Excel列名 -> 飞书字段名）
        可以根据需要自定义映射关系
        
        Returns:
            Dict[str, str]: 字段映射字典
        """
        # 默认情况下使用相同的字段名
        # 可以根据飞书表格的实际字段名进行调整
        if self.df is None:
            raise Exception("请先加载Excel文件")
            
        mapping = {}
        for col in self.df.columns:
            mapping[col] = col  # 默认使用相同名称
        
        # 如果需要自定义映射，可以在这里修改
        # 例如：
        # mapping['Ticker'] = '股票代码'
        # mapping['Name'] = '公司名称'
        
        return mapping
    
    def validate_data(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        验证数据完整性
        
        Args:
            records: 飞书格式的记录列表
            
        Returns:
            List[Dict[str, Any]]: 验证后的记录列表
        """
        validated_records = []
        
        for i, record in enumerate(records):
            # 检查必要字段
            required_fields = ['Ticker', 'Name']
            
            valid = True
            for field in required_fields:
                if field not in record['fields'] or not record['fields'][field]:
                    print(f"警告: 第{i+1}行缺少必要字段 {field}")
                    valid = False
            
            if valid:
                validated_records.append(record)
            else:
                print(f"跳过第{i+1}行数据（验证失败）")
        
        print(f"数据验证完成，有效记录{len(validated_records)}条")
        return validated_records
    
    def process_excel_to_feishu(self) -> List[Dict[str, Any]]:
        """
        完整的处理流程：Excel -> 飞书格式
        
        Returns:
            List[Dict[str, Any]]: 处理后的飞书格式数据
        """
        print("开始处理Excel文件...")
        
        # 1. 加载Excel
        self.load_excel()
        
        # 2. 清理数据
        cleaned_df = self.clean_data()
        
        # 3. 转换格式
        records = self.convert_to_feishu_records(cleaned_df)
        
        # 4. 验证数据
        validated_records = self.validate_data(records)
        
        print("Excel处理完成！")
        return validated_records
    
    def save_processed_data(self, records: List[Dict[str, Any]], output_path: str = None):
        """
        保存处理后的数据到JSON文件（用于调试）
        
        Args:
            records: 处理后的记录列表
            output_path: 输出文件路径
        """
        if output_path is None:
            output_path = self.excel_path.replace('.xlsx', '_feishu_format.json')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        print(f"处理后的数据已保存到: {output_path}")


if __name__ == "__main__":
    # 测试数据处理功能
    excel_path = "/Users/willmbp/Documents/2024/My_projects/Simple_YW/fromyouwei_updated.xlsx"
    
    try:
        processor = ExcelToFeishuProcessor(excel_path)
        records = processor.process_excel_to_feishu()
        
        print(f"\n=== 处理结果示例 ===")
        if records:
            print(f"第一条记录:")
            print(json.dumps(records[0], ensure_ascii=False, indent=2))
            
        # 保存处理结果用于调试
        processor.save_processed_data(records)
        
    except Exception as e:
        print(f"处理失败: {e}")