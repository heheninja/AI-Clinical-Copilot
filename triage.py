from llm import ask_gemini


def generate_triage(medical_json):

    prompt = f"""
You are an AI Clinical Triage Assistant.

Based ONLY on the patient information below, generate a JSON object.

Return ONLY valid JSON.

Format:

{{
    "urgency": "",
    "reason": "",
    "suggested_department": "",
    "suggested_tests": [],
    "follow_up_questions": []
}}

Rules:
- urgency must be one of: Low, Medium, High
- Do NOT diagnose diseases.
- Suggest only reasonable departments and common initial tests.
- If information is missing, include follow-up questions.

Patient Data:

{medical_json}
"""

    response = ask_gemini(prompt)

    response = response.replace("```json", "").replace("```", "").strip()

    return response