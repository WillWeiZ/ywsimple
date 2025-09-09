import akshare as ak
import pandas as pd
import os
import time

def get_eps_data_with_retry(stock_code, max_retries=3, delay=1):
    """
    带重试机制的EPS数据获取
    
    Args:
        stock_code: 股票代码
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
    
    Returns:
        DataFrame: EPS预测数据
    """
    for attempt in range(max_retries):
        try:
            stock_df = ak.stock_profit_forecast_ths(symbol=stock_code, indicator="预测年报每股收益")
            stock_df['股票代码'] = stock_code
            return stock_df
        
        except Exception as e:
            print(f"股票 {stock_code} 第{attempt + 1}次获取失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 1.5  # 轻微的指数退避
            else:
                print(f"股票 {stock_code} 所有重试都失败了")
                return pd.DataFrame()  # 返回空DataFrame而不是抛出异常

def main():
    stock_list = ['002156', '002837', '300229', '600249', '002230', '688111', '603019', '300496', '600519']
    
    # 创建一个空的DataFrame来存储所有股票的结果
    all_stocks_esp_df = pd.DataFrame()
    
    successful_count = 0
    
    # 遍历股票列表
    for i, stock_code in enumerate(stock_list):
        print(f"正在处理股票 {stock_code} ({i+1}/{len(stock_list)})...")
        
        try:
            # 获取单个股票的预测年报每股收益数据
            stock_data = get_eps_data_with_retry(stock_code)
            
            if not stock_data.empty:
                # 将结果添加到总的DataFrame中
                all_stocks_esp_df = pd.concat([all_stocks_esp_df, stock_data], ignore_index=True)
                successful_count += 1
                print(f"✅ 成功获取股票 {stock_code} 的预测每股收益数据")
            else:
                print(f"⚠️ 股票 {stock_code} 数据获取失败，跳过")
            
            # 添加小延迟避免请求过快
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ 获取股票 {stock_code} 数据时出现异常: {e}")
    
    # 确保data文件夹存在
    os.makedirs('data', exist_ok=True)
    
    # 保存结果到CSV文件
    if not all_stocks_esp_df.empty:
        output_path = 'data/股票代码_EPS.csv'
        all_stocks_esp_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✅ 所有股票的预测每股收益数据已保存到: {output_path}")
        print(f"📊 共处理了 {len(stock_list)} 只股票，成功获取 {successful_count} 只股票的数据，总计 {len(all_stocks_esp_df)} 条记录")
    else:
        print("❌ 没有获取到任何EPS数据")
        raise Exception("EPS数据获取完全失败")

if __name__ == "__main__":
    main()