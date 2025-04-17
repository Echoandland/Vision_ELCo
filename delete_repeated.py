import csv

input_file = "/Users/yucheng/Desktop/ELCo/modified_train_with_emojis_final_transfered.csv"       
output_file = "/Users/yucheng/Desktop/ELCo/modified_train_with_emojis_final_transfered_final.csv"  

unique_rows = set()

with open(input_file, "r", encoding="utf-8") as f_in:
    reader = csv.reader(f_in)
    header = next(reader, None)  

    for row in reader:
        if len(row) < 2:
            continue
        unicode_str, label_str = row[0], row[1]
        unique_rows.add((unicode_str, label_str))

with open(output_file, "w", encoding="utf-8", newline="") as f_out:
    writer = csv.writer(f_out)
    writer.writerow(["unicode", "label"])
    
    for (cp, lbl) in unique_rows:
        writer.writerow([cp, lbl])

print(f"去重完成！新的CSV已保存到 {output_file}")
