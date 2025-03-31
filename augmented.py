import pandas as pd
import random

# 读取原始 CSV 数据集
df = pd.read_csv("/Users/yucheng/Desktop/ELCo/benchmark_data/exp-entailment/output1.csv", escapechar='\\', engine='python')

# 检查必须存在的列
if 'sent1' not in df.columns or 'sent2' not in df.columns:
    raise ValueError("CSV 必须包含 'sent1' 和 'sent2' 列。")

# 创建新行的列表，新数据集的 label 全部设为 0
new_rows = []

# 遍历每一行，对于每个 sent1，对应有 5 行，我们需要排除这 5 行，再随机选择其他 sent1 对应的 sent2
for idx, row in df.iterrows():
    current_sent1 = row['sent1']
    
    # 筛选出 sent1 不同于当前 sent1 的所有行（排除当前 sent1 的5行）
    other_rows = df[df['sent1'] != current_sent1]
    
    # 如果没有其它行，则跳过（理论上不应发生）
    if other_rows.empty:
        continue
    
    # 随机选择一行，从其 sent2 中抽取
    random_sent2 = other_rows['sent2'].sample(n=1).values[0]
    
    # 将新的匹配记录加入列表，label 全部设为 0
    new_rows.append({
        'sent1': current_sent1,
        'sent2': random_sent2,
        'label': 0,
        'strategy': 1
    })

# 将新行转换为 DataFrame
df_new = pd.DataFrame(new_rows)

# 将原始数据集和新数据集拼接在一起
df_combined = pd.concat([df, df_new], ignore_index=True)

df_combined.to_csv("/Users/yucheng/Desktop/ELCo/benchmark_data/exp-entailment/output2.csv", index=False)