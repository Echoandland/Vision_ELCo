import csv

input_file = "/Users/yucheng/Desktop/ELCo/modified_train_with_emojis_final_transfered.csv"       # 你的去重前的 CSV 文件路径
output_file = "/Users/yucheng/Desktop/ELCo/modified_train_with_emojis_final_transfered_final.csv"  # 去重后生成的 CSV 文件路径

unique_rows = set()

with open(input_file, "r", encoding="utf-8") as f_in:
    reader = csv.reader(f_in)
    # 如果你的CSV第一行为表头，可以先读一行丢弃或存储:
    header = next(reader, None)  # header用于后面写表头，若不需要写表头可不存

    for row in reader:
        # row[0], row[1] 分别是 unicode, label
        if len(row) < 2:
            continue
        unicode_str, label_str = row[0], row[1]
        unique_rows.add((unicode_str, label_str))

# 将去重后的结果写回新的CSV
with open(output_file, "w", encoding="utf-8", newline="") as f_out:
    writer = csv.writer(f_out)
    # 如果需要表头，在这里写一次
    writer.writerow(["unicode", "label"])
    
    for (cp, lbl) in unique_rows:
        writer.writerow([cp, lbl])

print(f"去重完成！新的CSV已保存到 {output_file}")
