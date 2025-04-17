import json
import csv

with open('emoji.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

with open('output.csv', 'w', encoding='utf-8', newline='') as csv_file:
    fieldnames = ['sent1', 'sent2', 'label', 'strategy']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for emoji in data:
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
        for key in keys_order:
            sent2 = description.get(key, "")
            writer.writerow({
                'sent1': sent1,
                'sent2': sent2,
                'label': 1,
                'strategy': 1
            })
