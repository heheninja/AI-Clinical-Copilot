from datetime import datetime

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)


class ReportGenerator:

    def generate(self, data: dict) -> str:

        patient = data.get("patient", {})
        triage = data.get("triage", {})
        risk = data.get("risk_assessment", {})
        cds = data.get("clinical_decision_support", {})
        pathway = data.get("care_pathway", {})
        flags = data.get("clinical_flags", {})
        metrics = data.get("consultation_metrics", {})
        summary = data.get("patient_summary", {})
        metadata = data.get("metadata", {})

        emergency_banner = ""

        if flags.get("emergency_case"):
            emergency_banner = """
============================================================
🚨 EMERGENCY CASE DETECTED 🚨
Immediate Medical Attention Recommended
============================================================
"""

        report = f"""
============================================================
🏥 AI CLINICAL COPILOT
AI Assisted Clinical Documentation Report
============================================================

Generated:
{datetime.now().strftime("%d-%m-%Y %H:%M")}

This report is intended to assist healthcare professionals
and should not replace clinical judgement.

{emergency_banner}

============================================================
👤 PATIENT INFORMATION
============================================================

Chief Complaint:
{patient.get("chief_complaint","")}

History of Present Illness:
{patient.get("history_of_present_illness","")}

Symptoms:
{self.bullets(patient.get("symptoms",[]))}

Duration:
{patient.get("duration","")}

Severity:
{patient.get("severity","")}

Department:
{patient.get("department","")}

Allergies:
{self.bullets(patient.get("allergies",[]))}

Current Medications:
{self.bullets(patient.get("current_medications",[]))}

Past Medical History:
{self.bullets(patient.get("past_medical_history",[]))}

Family History:
{self.bullets(patient.get("family_history",[]))}

Social History:
{self.bullets(patient.get("social_history",[]))}

============================================================
🩺 VITALS
============================================================

Temperature:
{patient.get("vitals",{}).get("temperature","")}

Blood Pressure:
{patient.get("vitals",{}).get("blood_pressure","")}

Heart Rate:
{patient.get("vitals",{}).get("heart_rate","")}

Respiratory Rate:
{patient.get("vitals",{}).get("respiratory_rate","")}

Oxygen Saturation:
{patient.get("vitals",{}).get("oxygen_saturation","")}

============================================================
📋 CLINICAL SUMMARY
============================================================

{data.get("clinical_summary","")}

============================================================
🧠 CLINICAL IMPRESSION
============================================================

{self.bullets(data.get("clinical_impression",[]))}

============================================================
⚡ TRIAGE
============================================================

Urgency:
{triage.get("urgency","")}

Reason:
{triage.get("reason","")}

Department:
{triage.get("department","")}

Estimated Wait Time:
{triage.get("estimated_wait_time","")}

============================================================
📊 RISK ASSESSMENT
============================================================

Risk Level:
{"🟢 LOW" if risk.get("risk_level")=="Low"
else "🟡 MEDIUM" if risk.get("risk_level")=="Medium"
else "🟠 HIGH" if risk.get("risk_level")=="High"
else "🔴 CRITICAL"}

Risk Score:
{risk.get("score","")}/100

Reason:
{risk.get("reason","")}

============================================================
👨‍⚕️ CLINICAL DECISION SUPPORT
============================================================

Recommended Specialist:
{cds.get("recommended_specialist","")}

Recommended Action:
{cds.get("recommended_action","")}

Monitoring Required:
{cds.get("monitoring_required","")}

Follow Up:
{cds.get("follow_up","")}

Priority Reason:
{cds.get("priority_reason","")}

============================================================
🛣 CARE PATHWAY
============================================================

Consultation Type:
{pathway.get("consultation_type","")}

Recommended Next Step:
{pathway.get("recommended_next_step","")}

Estimated Priority:
{pathway.get("estimated_priority","")}

============================================================
🧪 RECOMMENDED TESTS
============================================================

{self.bullets(data.get("recommended_tests",[]))}

============================================================
🚨 RED FLAGS
============================================================

Present:
{data.get("red_flags",{}).get("present")}

Items:
{self.bullets(data.get("red_flags",{}).get("items",[]))}

============================================================
📝 DOCTOR HANDOFF
============================================================

{data.get("doctor_handoff","")}
============================================================
🩺 DOCTOR MODIFICATIONS
============================================================

Diagnosis (AI):
{data.get("clinical_impression", ["Not Available"])[0] if data.get("clinical_impression") else "Not Available"}

Diagnosis (Doctor):
{data.get("doctor_review", {}).get("diagnosis", "Not Modified")}

Treatment Changes:
{self.bullets(data.get("doctor_review", {}).get("treatment_changes", []))}

Additional Notes:
{data.get("doctor_review", {}).get("notes", "None")}

============================================================
😊 PATIENT SUMMARY
============================================================

Condition Overview:
{summary.get("condition_overview","")}

Next Steps:
{self.bullets(summary.get("next_steps",[]))}

Warning Signs:
{self.bullets(summary.get("warning_signs",[]))}

============================================================
💡 PATIENT ADVICE
============================================================

{self.bullets(data.get("patient_advice",[]))}
============================================================
💊 PRESCRIPTION OCR
============================================================

Diagnosis:
{data.get("prescription_ocr", {}).get("diagnosis", "Not Uploaded")}

Doctor Notes:
{data.get("prescription_ocr", {}).get("doctor_notes", "Not Uploaded")}

Medicines:
{self.format_medicines(data.get("prescription_ocr", {}).get("medicines", []))}

Recommended Tests:
{self.bullets(data.get("prescription_ocr", {}).get("tests", []))}

Follow Up:
{data.get("prescription_ocr", {}).get("follow_up", "")}

============================================================
👨‍⚕️ PATIENT MEDICINE GUIDE
============================================================

{self.format_medicine_guide(
    data.get("medicine_guide", [])
)}
============================================================
📈 CONSULTATION METRICS
============================================================

Information Completeness:
{metrics.get("information_completeness","")}

Overall Consultation Score:
{metrics.get("information_completeness",0)}/100

Missing Information Count:
{metrics.get("missing_information_count","")}

Consultation Quality:
{metrics.get("consultation_quality","")}

============================================================
🤖 AI TRANSPARENCY
============================================================

AI Confidence:
{metadata.get("model_confidence",0)*100:.1f}%

Doctor Reviewed:
YES

Doctor Approved:
YES

Edited Fields:
• Diagnosis
• Treatment Plan

Prescription OCR:
{"Completed" if data.get("prescription_ocr") else "Not Uploaded"}

Medicine Explanation:
{"Generated" if data.get("medicine_guide") else "Not Generated"}
============================================================
DISCLAIMER
============================================================

This report was automatically generated by AI Clinical Copilot.

It is intended ONLY to assist healthcare professionals.

Final diagnosis and treatment decisions remain the responsibility
of the attending clinician.

Generated using:
• Faster-Whisper
• Google Gemini
• AI Clinical Copilot Pipeline

============================================================
END OF REPORT
============================================================
"""

        return report

    def generate_pdf(self, data, output_path):

        report = self.generate(data)

        doc = SimpleDocTemplate(
            output_path,
            topMargin=25,
            bottomMargin=25,
            leftMargin=35,
            rightMargin=35
        )

        styles = getSampleStyleSheet()

        story = []

        for line in report.split("\n"):

            if line.strip() == "":
                story.append(Spacer(1, 6))
            else:
                story.append(
                    Paragraph(
                        line.replace("•", "&bull;"),
                        styles["BodyText"]
                    )
                )

        doc.build(story)

    @staticmethod
    def bullets(items):
        if not items:
            return "Not Available"

        return "<br/>".join(f"• {item}" for item in items)

    @staticmethod
    def format_medicines(medicines):
        if not medicines:
            return "No medicines extracted."

        text = ""

        for med in medicines:
            text += (
                f"• {med.get('name', '')} "
                f"{med.get('strength', '')} | "
                f"{med.get('dose', '')} | "
                f"{med.get('frequency', '')} | "
                f"{med.get('duration', '')}\n"
            )

        return text

    @staticmethod
    def format_medicine_guide(guides):
        if not guides:
            return "Medicine explanation not available."

        text = ""

        for med in guides:
            text += (
                f"Medicine: {med.get('medicine', '')}\n"
                f"Purpose: {med.get('purpose', '')}\n"
                f"When: {med.get('when_to_take', '')}\n"
                f"Food: {med.get('food_instruction', '')}\n"
                f"Side Effects: {med.get('side_effects', '')}\n\n"
            )

        return text