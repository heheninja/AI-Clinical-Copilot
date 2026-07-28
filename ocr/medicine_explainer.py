import json
from llm import ask_gemini


def explain_medicines(medicines):

    prompt = f"""
You are an experienced doctor.

Explain every medicine in SIMPLE language.

Medicines:

{json.dumps(medicines, indent=2)}

Return ONLY JSON.

[
    {{
        "medicine":"",
        "purpose":"",
        "when_to_take":"",
        "food_instruction":"",
        "side_effects":"",
        "simple_explanation":""
    }}
]
"""

    return json.loads(
        ask_gemini(prompt)
    )