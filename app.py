import streamlit as st

from copilot import ClinicalCopilot
from report_generator import ReportGenerator
from storage.department_storage import DepartmentStorage

st.set_page_config(
    page_title="AI Clinical Copilot",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 AI Clinical Copilot")
st.write("AI Assisted Clinical Documentation")

conversation = st.text_area(
    "Doctor-Patient Conversation",
    height=250
)

uploaded = st.file_uploader(
    "Upload Prescription",
    type=["png", "jpg", "jpeg"]
)

if st.button("Generate Clinical Report"):

    if conversation.strip() == "":
        st.error("Please enter a conversation.")
        st.stop()

    copilot = ClinicalCopilot()

    with st.spinner("Analyzing..."):
        result = copilot.analyze(conversation)

    if result.get("success") is False:
        st.error(result["error"])
        st.stop()

    if uploaded:

        from ocr.prescription_ocr import extract_prescription
        from patient.medicine_explainer import explain_medicines

        with open("temp_prescription.png", "wb") as f:
            f.write(uploaded.read())

        ocr = extract_prescription("temp_prescription.png")

        result["prescription_ocr"] = ocr
        result["medicine_guide"] = explain_medicines(ocr)

    # Temporary Doctor Review
    ai_diag = ""
    if result.get("clinical_impression"):
        ai_diag = result["clinical_impression"][0]

    result["doctor_review"] = {
        "reviewed": True,
        "approved": True,
        "diagnosis": ai_diag,
        "treatment_changes": [],
        "notes": "",
        "edited_fields": []
    }

    storage = DepartmentStorage()
    storage.save(result)

    report = ReportGenerator().generate(result)

    st.success("Clinical Report Generated")

    st.download_button(
        "Download Report",
        report,
        file_name="clinical_report.txt"
    )

    st.text_area(
        "Clinical Report",
        report,
        height=600
    )