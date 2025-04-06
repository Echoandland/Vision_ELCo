from dotenv import load_dotenv
import os
from pydantic import BaseModel
from openai import OpenAI
import base64
import json
import re
import model.emoji_datamodel_v2 as emoji_datamodel
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict


class EmojiDescriptions:
    visual_scene: str
    spatial_composition: str
    posture_expression: str
    color_palette: str
    comprehensive_description: str


class EmojiData:
    emoji_unicode: str
    aliases: List[str]
    description: EmojiDescriptions


load_dotenv()
openai_base_url = os.getenv('OPENAI_BASE_URL')
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)


def get_images_base64(folder_path: str) -> List[str]:
    image_extensions = ['png', 'jpg', 'jpeg']
    base64_images = []
    if not os.path.exists(folder_path):
        raise ValueError(
            f"The provided path '{folder_path}' is not a valid directory.")
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            extension = file.split('.')[-1]
            if extension in image_extensions:
                with open(file_path, "rb") as image_file:
                    base64_image = base64.b64encode(
                        image_file.read()).decode('utf-8')
                    base64_images.append(base64_image)

    return base64_images


def get_image_files(folder_path, extensions=None):
    if extensions is None:
        extensions = {'.png', '.jpg', '.jpeg',
                      '.gif', '.bmp', '.webp', '.tiff'}

    image_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if os.path.splitext(file)[1].lower() in extensions:
                image_files.append(os.path.join(root, file))

    return image_files


def perform_ocr_on_images(image_file_path: str, client) -> List[Dict]:
    model = "gpt-4o-2024-11-20"
    with open(image_file_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    unicode = re.findall(r'\{(.*?)\}', image_file_path)[0]
    image_data_url = f"data:image/png;base64,{base64_image}"
    message = [
        {
            "role": "system",
            "content": "You are an OCR expert that extracts emoji information from emoji images. Return JSON data that matches the requested schema exactly."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """
                    Please extract the emoji information from the image and return the data in this JSON schema:

                    {
                        "emoji_unicode": "string - Full Unicode representation (e.g., U+1F600)",
                        "aliases": ["string - Alternative names for the emoji"],
                        "description": {
                            "visual_scene": "string - Description of the visual scene",
                            "spatial_composition": "string - Description of the spatial composition",
                            "posture_expression": "string - Description of the posture or expression",
                            "color_palette": "string - Description of the color palette",
                            "comprehensive_description": "string - Comprehensive description of the emoji"
                        }
                    }
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data_url,
                        "detail": "high"
                    }
                }
            ]
        }
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=message,
            max_tokens=3000,
            temperature=0
        )

        if response.choices and len(response.choices) > 0:
            json_content = response.choices[0].message.content
            try:
                pattern = r'```json\s*(.*?)\s*```'
                emoji_json_content = re.search(
                    pattern, json_content, re.DOTALL)
                emoji_data_dict = emoji_json_content.group(1)
                emoji_data_dict = emoji_data_dict.replace(
                    '\n', '').replace("   ", '').replace('"{', '{').replace('}"', '}')
                emoji_as_json = json.loads(emoji_data_dict)
                emoji_as_json['unicode'] = unicode
            except Exception as e:
                with open("error.log", "a") as log_file:
                    log_file.write(f"[{unicode}] An error occurred: {e}\n")
                return None
    except Exception as e:
        with open("error.log", "a") as log_file:
            log_file.write(f"[{unicode}] An error occurred: {e}\n")
        return None
    return emoji_as_json


def main():
    folder_path = 'images/output_images'
    base64_image_files_path = get_image_files(folder_path)
    emoji_list = []
    for base64_image_file_path in base64_image_files_path:
        emoji_json = perform_ocr_on_images(base64_image_file_path, client)
        emoji_list.append(emoji_json)
    with open("images_output.json", "w", encoding="utf-8") as json_file:
        json.dump(emoji_list, json_file,
                  ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
