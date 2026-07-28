from dotenv import dotenv_values
from google import genai

config = dotenv_values(".env")
client = genai.Client(api_key=config["GEMINI_API_KEY"])

for model in client.models.list():
    print(model.name)