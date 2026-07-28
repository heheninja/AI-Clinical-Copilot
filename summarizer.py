from llm import ask_gemini


def generate_summary(medical_json):

    prompt = f"""
You are an experienced government hospital doctor.

Below is the extracted patient information.

Generate a short professional clinical summary.

The summary should contain:

1. Chief Complaint
2. Symptoms
3. Duration
4. Current Medication
5. Allergies
6. Medical History
7. Suggested Department

Keep it concise.

Patient Data:

{medical_json}
"""

    return ask_gemini(prompt)