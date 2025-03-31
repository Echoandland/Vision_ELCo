import csv
import re

input_file = "/Users/yucheng/Desktop/ELCo/modified_train_with_emojis_final.csv"   # 你的原始CSV路径
output_file = "/Users/yucheng/Desktop/ELCo/modified_train_with_emojis_final_transfered.csv"                  # 生成新CSV的保存路径

with open(input_file, "r", encoding="utf-8") as f_in, open(output_file, "w", encoding="utf-8", newline="") as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out)
    
    # 如果需要表头，可以自行保留；若不需要，注释或删除下一行：
    writer.writerow(["unicode", "label"])
    
    for row in reader:
        # 确保倒数第二列和最后一列存在
        if len(row) < 2:
            continue
        
        # 倒数第二列含有形如 "This is {1F387} {1F52E}" 的文本
        col_codepoints = row[-2]
        # 最后一列含有形如 "sparkler, crystal_ball" 的标签（逗号分隔）
        col_labels = row[-1]
        
        # 正则提取花括号中的 Unicode 码
        codepoints = re.findall(r"\{(.*?)\}", col_codepoints)
        
        # 以逗号切分标签，并去除多余空格
        labels = [lbl.strip() for lbl in col_labels.split(",")]
        
        # 将两者一一对应写入新 CSV
        for cp, lbl in zip(codepoints, labels):
            writer.writerow([cp, lbl])

print(f"提取完成！新的CSV已保存到 {output_file}")

