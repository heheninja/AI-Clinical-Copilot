from dotenv import dotenv_values
from google import genai
from google.genai import types

config = dotenv_values(".env")

API_KEY = config["GEMINI_API_KEY"]

print("=" * 60)
print("Loaded API Key:", API_KEY[:12] + "...")
print("=" * 60)

MODEL_NAME = "gemini-3.6-flash"

client = genai.Client(api_key=API_KEY)


def ask_gemini(prompt: str) -> str:

    print(f"\n🧠 Using Model: {MODEL_NAME}")

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                top_p=0.8,
                response_mime_type="application/json"
            )
        )

        return response.text

    except Exception as e:
        print("\n========== GEMINI ERROR ==========")
        print(e)
        raise