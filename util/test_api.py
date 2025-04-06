import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai_base_url = os.getenv('OPENAI_BASE_URL')
openai_api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=openai_api_key)
prompt = "Write a short story about a cat in Queenstown."

try:
    response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    print(response.choices[0].message.content)
except Exception as e:
    print(f"An error occurred: {e}")
