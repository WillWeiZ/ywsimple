import akshare as ak
import time
import os

def get_stock_price_data_with_retry(max_retries=3, delay=2):
    """
    带重试机制的股票价格数据获取
    
    Args:
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
    
    Returns:
        DataFrame: 股票价格数据
    """
    for attempt in range(max_retries):
        try:
            print(f"尝试获取股票数据 (第{attempt + 1}/{max_retries}次)...")
            stock_df = ak.stock_zh_a_spot_em()
            print(f"成功获取{len(stock_df)}条股票数据")
            return stock_df
        
        except Exception as e:
            print(f"第{attempt + 1}次获取失败: {str(e)}")
            if attempt < max_retries - 1:
                print(f"等待{delay}秒后重试...")
                time.sleep(delay)
                delay *= 2  # 指数退避
            else:
                print("所有重试都失败了")
                raise e

def main():
    try:
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        
        # 获取数据
        stock_zh_a_spot_em_df = get_stock_price_data_with_retry()
        
        # 保存数据
        output_path = 'data/all_stock_price.csv'
        stock_zh_a_spot_em_df.to_csv(output_path, index=False)
        print(f"股票价格数据已保存到: {output_path}")
        
    except Exception as e:
        print(f"获取股票价格数据失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()


