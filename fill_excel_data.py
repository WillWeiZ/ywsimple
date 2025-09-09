import pandas as pd
import numpy as np

# 定义文件路径
fromyouwei_path = '/Users/willmbp/Documents/2024/My_projects/Simple_YW/fromyouwei.xlsx'
stock_price_path = '/Users/willmbp/Documents/2024/My_projects/Simple_YW/data/all_stock_price.csv'
eps_path = '/Users/willmbp/Documents/2024/My_projects/Simple_YW/data/股票代码_EPS.csv'

# 读取Excel文件
df_excel = pd.read_excel(fromyouwei_path)

# 读取股票价格数据
df_price = pd.read_csv(stock_price_path)
# 确保股票代码列是字符串类型
df_price['代码'] = df_price['代码'].astype(str).str.zfill(6)

# 读取EPS数据
df_eps = pd.read_csv(eps_path)
# 筛选2025年的EPS数据
df_eps_2025 = df_eps[df_eps['年度'] == 2025].copy()
# 确保股票代码列是字符串类型
df_eps_2025['股票代码'] = df_eps_2025['股票代码'].astype(str).str.zfill(6)

# 创建字典用于快速查找
def create_lookup_dict(df, key_col, value_col):
    return dict(zip(df[key_col], df[value_col]))

# 创建价格和市值的查找字典
price_dict = create_lookup_dict(df_price, '代码', '最新价')
market_cap_dict = create_lookup_dict(df_price, '代码', '总市值')

# 创建EPS查找字典
eps_dict = create_lookup_dict(df_eps_2025, '股票代码', '均值')

# 处理Excel中的每一行
def process_row(row):
    # 提取股票代码（前6位）
    ticker = str(row['Ticker'])[:6]
    
    # 获取最新价
    current_price = price_dict.get(ticker, np.nan)
    
    # 获取EPS均值
    eps_mean = eps_dict.get(ticker, np.nan)
    
    # 计算PE (2025E)
    pe_2025e = current_price / eps_mean if eps_mean and eps_mean != 0 and not np.isnan(eps_mean) else np.nan
    
    # 获取总市值并转换为亿元
    market_cap = market_cap_dict.get(ticker, np.nan)
    market_cap_bn = market_cap / 100000000 if not np.isnan(market_cap) else np.nan
    
    # 计算Mid Target ((Target Low + Target High) / 2)
    target_low = row['Target Low']
    target_high = row['Target High']
    mid_target = (target_low + target_high) / 2 if not np.isnan(target_low) and not np.isnan(target_high) else np.nan
    
    # 计算Potential Upside% (Mid Target / Current Price - 1)，保留小数点后1位
    potential_upside = round((mid_target / current_price - 1) * 100, 1) if not np.isnan(current_price) and not np.isnan(mid_target) and current_price != 0 else np.nan
    
    # 更新行数据
    row['Current Price'] = current_price
    row['EPS (2025E)'] = eps_mean
    row['PE (2025E)'] = pe_2025e
    row['Market Cap (CNY bn)'] = market_cap_bn
    row['Mid Target'] = mid_target
    row['Potential Upside %'] = potential_upside
    
    return row

# 应用处理函数
df_excel = df_excel.apply(process_row, axis=1)

# 保存更新后的Excel文件
output_path = '/Users/willmbp/Documents/2024/My_projects/Simple_YW/fromyouwei_updated.xlsx'
df_excel.to_excel(output_path, index=False)

print(f"Excel文件已成功更新并保存到: {output_path}")
print(f"处理了 {len(df_excel)} 行数据")