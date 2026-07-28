import os
import json

from fastapi import FastAPI
from pydantic import BaseModel

from copilot import ClinicalCopilot
from report_generator import ReportGenerator

app = FastAPI(
    title="AI Clinical Copilot",
    version="1.0.0",
    description="SIH Healthcare AI Backend"
)


class ConversationRequest(BaseModel):
    conversation: str


copilot = ClinicalCopilot()
report_generator = ReportGenerator()


@app.get("/")
def home():
    return {
        "message": "AI Clinical Copilot API is Running 🚀"
    }


@app.post("/analyze")
def analyze(request: ConversationRequest):

    result = copilot.analyze(request.conversation)

    os.makedirs("outputs", exist_ok=True)

    with open("outputs/extracted.json", "w") as f:
        json.dump(result, f, indent=4)

    report_generator.generate_pdf(
        result,
        "outputs/clinical_report.pdf"
    )

    return result