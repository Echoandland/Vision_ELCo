import os
import re
import pandas as pd
from PIL import Image

# 创建用于保存合并后图片的文件夹
output_folder = "/Users/bmyzyt1314/Desktop/CS4248/nlp_project/merged_images_test"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 读取CSV文件
df = pd.read_csv("/Users/bmyzyt1314/Desktop/CS4248/nlp_project/data/test_with_emojis_final.csv")

# 遍历每一行
for index, row in df.iterrows():
    # 使用正则表达式提取所有被大括号包围的emoji unicode
    emoji_codes = re.findall(r'\{(.*?)\}', row["sent1_emoji_unicode"])
    
    images = []
    # 对每个emoji code尝试读取对应的png图片
    for code in emoji_codes:
        image_path = os.path.join("output_images", f"{{{code}}}.png")
        if os.path.exists(image_path):
            img = Image.open(image_path)
            images.append(img)
        else:
            print(f"警告: 找不到图片 {image_path}")
    
    # 如果这一行至少存在一张图片，则将图片按顺序横向拼接
    if images:
        # 计算合并后图片的总宽度和最大高度
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)
        
        # 创建一个新图片（背景设为透明）
        merged_image = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))
        
        # 依次将图片粘贴到新图片上
        x_offset = 0
        for img in images:
            merged_image.paste(img, (x_offset, 0))
            x_offset += img.width
        
        # 保存合并后的图片
        merged_image.save(os.path.join(output_folder, f"merged_{index}.png"))