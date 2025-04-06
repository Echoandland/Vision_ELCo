from dotenv import load_dotenv
import os
from pydantic import BaseModel
from openai import OpenAI, AzureOpenAI

import base64
import json
import pandas as pd
import re
import model.emoji_datamodel_v2 as emoji_datamodel
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict

load_dotenv()
openai_base_url = os.getenv('OPENAI_BASE_URL')
openai_api_key = os.getenv('OPENAI_API_KEY')
open_ai_client = OpenAI(api_key=openai_api_key)

azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
azure_openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
azure_openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION')
azure_openai_api_deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
azure_openai_client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=azure_openai_api_key,
    api_version=azure_openai_api_version
)

mode = os.getenv('MODE')
if mode == 'openai':
    client = open_ai_client
    model = 'gpt-4o-2024-11-20'
elif mode == 'azure':
    client = azure_openai_client
    model = azure_openai_api_deployment_name


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


def curate_benchmark_data():
    benchmark_data_category = ['test', 'train', 'val']
    all_dfs = []
    for category in benchmark_data_category:
        elco_dataset = pd.read_csv(
            f"benchmark_data/exp-entailment/{category}.csv")
        elco_curated_dataset = elco_dataset.copy()
        elco_curated_dataset['image_path'] = None
        elco_curated_dataset['image_base64'] = None

        for index, row in elco_dataset.iterrows():
            image_path = 'images/merged_images/merged_images_' + \
                category + '/merged_' + str(index) + '.png'
            if os.path.exists(image_path):
                elco_curated_dataset.at[index, 'image_path'] = image_path
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(
                        image_file.read()).decode('utf-8')
                    elco_curated_dataset.at[index,
                                            'image_base64'] = base64_image

        all_dfs.append(elco_curated_dataset)

    combined_df = pd.concat(all_dfs, ignore_index=True)

    return combined_df


def emote_predict(df: pd.DataFrame) -> pd.DataFrame:
    """
    Predicts the emoji data using the specified model.
    Args:
        df (pd.DataFrame): DataFrame containing the emoji data.
        model_name (str): Name of the model to use for prediction.
    Returns:
        pd.DataFrame: DataFrame with the predicted emoji data.
    """
    result = df.copy()
    result['predicted_label'] = None
    result['entailment_relationship'] = None
    result['confidence_score'] = None
    result['explanation'] = None
    for index, row in result.iterrows():
        print(f"Processing index: {index}")
        image_data_url = f"data:image/png;base64,{row['image_base64']}"
        sentence = row['sent2'].replace("This is ", "").replace(".", "")
        message = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
                        Please predict whether the emoji attached entails the below sentence. 
                        {sentence}.

                        You should provide a binary response (1 for true, 0 for false).
                        Please also indicate the entailment relationship among the below 6 relationship:
                        1. Direct: a straightforward approach to map word in English to one or few emojis.
                        2. Metaphorical: emoji combine together embody the metaphorical meaning of the phrase.
                        3. Semantic List: a list of related emojis is used to imply the concept's meaning.
                        4. Reduplication: accentuate the intensity of an adjective
                        5. Single: solitary emoji captures the essence of the concept.

                        Please return the data in this JSON schema:
                        {{
                            "predicted_label": "int - 1 for true, 0 for false",
                            "entailment_relationship": 
                                {{
                                    "relationship": "string - The relationship type",
                                    "confidence_score": "string - High, Medium, Low",
                                    "explanation": "string - Short explanation of the relationship"
                                }}
                        }}
                        """.format(sentence=sentence)
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
                    emote_json_content = re.search(
                        pattern, json_content, re.DOTALL)
                    emote_data_dict = emote_json_content.group(1)
                    emote_data_dict = emote_data_dict.replace(
                        '\n', '').replace("   ", '').replace('"{', '{').replace('}"', '}')
                    emote_prediction = json.loads(emote_data_dict)
                    result.at[index, 'predicted_label'] = int(
                        emote_prediction['predicted_label'])
                    result.at[index, 'entailment_relationship'] = emote_prediction['entailment_relationship']['relationship']
                    result.at[index, 'confidence_score'] = emote_prediction['entailment_relationship']['confidence_score']
                    result.at[index, 'explanation'] = emote_prediction['entailment_relationship']['explanation']
                except Exception as e:
                    with open("error.log", "a") as log_file:
                        log_file.write(
                            f"index [{index}] An error occurred: {e}\n")
        except Exception as e:
            with open("error.log", "a") as log_file:
                log_file.write(f"index [{index}] An error occurred: {e}\n")
    result = result.drop(columns=['image_path', 'image_base64'])
    result.to_csv(
        'benchmark_data/exp-entailment/emote_prediction.csv', index=False)
    return result
