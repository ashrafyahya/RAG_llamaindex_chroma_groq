from json import loads
import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.environ.get("groq_api_key")
client = Groq(
    api_key=groq_api_key,
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)