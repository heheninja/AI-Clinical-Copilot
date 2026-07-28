from llm import ask_gemini


def detect_missing_information(medical_json):

    prompt = f"""
You are an AI Clinical Assistant.

Review the extracted patient information.

Identify important medical details that are still missing.

Return ONLY a bullet list.

Patient Data:

{medical_json}
"""

    return ask_gemini(prompt)