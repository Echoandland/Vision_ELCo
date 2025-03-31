import json
import csv

# 打开并读取 JSON 文件
with open('emoji.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# 打开 CSV 文件并写入数据
with open('output.csv', 'w', encoding='utf-8', newline='') as csv_file:
    fieldnames = ['sent1', 'sent2', 'label', 'strategy']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # 遍历 JSON 文件中的每个对象
    for emoji in data:
        # 如果 aliases 为空，则跳过这一条数据
        aliases = emoji.get('aliases', [])
        if not aliases:
            continue
        
        first_alias = aliases[0]
        sent1 = f"{first_alias} [EM]"
        
        description = emoji.get('description', {})
        keys_order = [
            'visual_scene',
            'spatial_composition',
            'posture_expression',
            'color_palette',
            'comprehensive_description'
        ]
        # 按顺序写入每一行数据
        for key in keys_order:
            sent2 = description.get(key, "")
            writer.writerow({
                'sent1': sent1,
                'sent2': sent2,
                'label': 1,
                'strategy': 1
            })
