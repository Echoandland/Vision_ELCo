import csv
import re

input_file = "/Users/yucheng/Desktop/ELCo/modified_train_with_emojis_final.csv"  
output_file = "/Users/yucheng/Desktop/ELCo/modified_train_with_emojis_final_transfered.csv"                  

with open(input_file, "r", encoding="utf-8") as f_in, open(output_file, "w", encoding="utf-8", newline="") as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out)
    
    writer.writerow(["unicode", "label"])
    
    for row in reader:
        
        if len(row) < 2:
            continue
        
        col_codepoints = row[-2]
        col_labels = row[-1]
        
        codepoints = re.findall(r"\{(.*?)\}", col_codepoints)
        
        labels = [lbl.strip() for lbl in col_labels.split(",")]
        
        for cp, lbl in zip(codepoints, labels):
            writer.writerow([cp, lbl])

print(f"提取完成！新的CSV已保存到 {output_file}")

