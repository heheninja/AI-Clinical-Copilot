import json
from PIL import Image

from llm import client, MODEL_NAME
from google.genai import types


def extract_prescription(image_path):
    """
    Extracts medicines, doctor notes and tests from
    a handwritten prescription using Gemini Vision.
    """

    image = Image.open(image_path)

    prompt = """
You are an expert medical OCR assistant.

Read the prescription carefully.

Extract ALL handwritten information.

Return ONLY valid JSON.

{
    "diagnosis":"",
    "doctor_notes":"",
    "medicines":[
        {
            "name":"",
            "strength":"",
            "dose":"",
            "frequency":"",
            "duration":"",
            "instructions":""
        }
    ],
    "tests":[],
    "follow_up":"",
    "other_notes":""
}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            image,
            prompt
        ],
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)