import csv

input_file = '/Users/yucheng/Desktop/ELCo/benchmark_data/exp-entailment/output.csv'
output_file = '/Users/yucheng/Desktop/ELCo/benchmark_data/exp-entailment/output1.csv'

with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8', newline='') as f_out:
    reader = csv.DictReader(f_in)
    fieldnames = reader.fieldnames
    # 关闭自动引号功能，设置 escapechar 以避免因分隔符或换行符问题导致异常
    writer = csv.DictWriter(f_out, fieldnames=fieldnames, quoting=csv.QUOTE_NONE, escapechar='\\')
    writer.writeheader()
    for row in reader:
        if 'sent2' in row:
            # 移除字段内部的双引号
            row['sent2'] = row['sent2'].replace('"', '')
        writer.writerow(row)