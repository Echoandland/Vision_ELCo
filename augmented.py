import pandas as pd
import random

df = pd.read_csv("/Users/yucheng/Desktop/ELCo/benchmark_data/exp-entailment/output1.csv", escapechar='\\', engine='python')

if 'sent1' not in df.columns or 'sent2' not in df.columns:
    raise ValueError("CSV 必须包含 'sent1' 和 'sent2' 列。")

new_rows = []

for idx, row in df.iterrows():
    current_sent1 = row['sent1']
    
    other_rows = df[df['sent1'] != current_sent1]
    
    if other_rows.empty:
        continue
    
    random_sent2 = other_rows['sent2'].sample(n=1).values[0]
    
    new_rows.append({
        'sent1': current_sent1,
        'sent2': random_sent2,
        'label': 0,
        'strategy': 1
    })

df_new = pd.DataFrame(new_rows)

df_combined = pd.concat([df, df_new], ignore_index=True)

df_combined.to_csv("/Users/yucheng/Desktop/ELCo/benchmark_data/exp-entailment/output2.csv", index=False)
