from llm import ask_gemini
import json


def explain_medicines(ocr_data):

    medicines = ocr_data["medicines"]

    prompt = f"""
You are a medical assistant.

Explain these medicines in SIMPLE language.

Medicines:

{json.dumps(medicines, indent=2)}

Return JSON.

[
 {{
   "medicine":"",
   "purpose":"",
   "when_to_take":"",
   "side_effects":"",
   "food_instruction":"",
   "simple_explanation":""
 }}
]
"""

    return json.loads(ask_gemini(prompt))