import json

from llm import ask_gemini
from prompts import EXTRACTION_PROMPT


def extract_medical_information(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    conversation = data["conversation"]

    prompt = EXTRACTION_PROMPT.format(
        conversation=conversation
    )

    response = ask_gemini(prompt)

    # Remove markdown if Gemini returns ```json
    response = response.replace("```json", "").replace("```", "").strip()

    return json.loads(response)