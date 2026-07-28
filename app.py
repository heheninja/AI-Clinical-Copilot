import os
import streamlit as st

from copilot import ClinicalCopilot
from report_generator import ReportGenerator
from storage.department_storage import DepartmentStorage

# Patient lookup helper
from patient.patient_lookup import get_patient
# Doctor auth helper
from auth.doctor_auth import validate_doctor_credentials

st.set_page_config(
    page_title="AI Clinical Copilot",
    page_icon="🏥",
    layout="wide"
)


def login_page():
    st.title("🏥 AI Clinical Copilot — Sign In")
    role = st.radio("Sign in as:", ("Doctor", "Patient"))

    if role == "Patient":
        aadhaar = st.text_input("Enter Aadhaar number", key="login_aadhaar")
        if st.button("Sign in as Patient"):
            if not aadhaar.strip():
                st.error("Please enter an Aadhaar number.")
            else:
                result = get_patient(aadhaar.strip())
                if result.get("status") == "success":
                    st.session_state['user'] = {
                        "role": "patient",
                        "patient": result["patient"]
                    }
                    st.success(f"Signed in as patient: {result['patient'].get('name')}")
                    st.experimental_rerun()
                else:
                    st.error("Patient not found. Check Aadhaar or register first.")

    else:  # Doctor
        username = st.text_input("Doctor username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Sign in as Doctor"):
            if validate_doctor_credentials(username.strip(), password):
                st.session_state['user'] = {"role": "doctor", "username": username.strip()}
                st.success(f"Signed in as doctor: {username.strip()}")
                st.experimental_rerun()
            else:
                st.error("Invalid doctor credentials.")


def main_app():
    user = st.session_state.get('user', {})
    st.title("🏥 AI Clinical Copilot")
    st.write("AI Assisted Clinical Documentation")
    st.write(f"Signed in as: {user.get('role')} — {user.get('username') or user.get('patient', {}).get('name', '')}")

    # If doctor, allow loading a patient by Aadhaar
    if user.get('role') == 'doctor':
        col1, col2 = st.columns([3, 1])
        with col1:
            doctor_patient_aadhaar = st.text_input("Patient Aadhaar (for this report)", key="doctor_patient_aadhaar")
        with col2:
            if st.button("Load Patient"):
                if doctor_patient_aadhaar.strip():
                    result = get_patient(doctor_patient_aadhaar.strip())
                    if result.get("status") == "success":
                        st.session_state['current_patient'] = result['patient']
                        st.success(f"Loaded patient: {result['patient'].get('name')}")
                    else:
                        st.error("Patient not found.")
                else:
                    st.error("Enter Aadhaar to load patient.")

    # Show loaded patient (either patient signed-in or doctor-loaded)
    current_patient = st.session_state.get('current_patient') if user.get('role') == 'doctor' else user.get('patient')

    if current_patient:
        st.info(f"Reporting for patient: {current_patient.get('name')} (Aadhaar: {current_patient.get('aadhaar')})")
    else:
        st.info("No patient loaded. If you're a doctor, load a patient by Aadhaar. Patients who sign in see their own data automatically.")

    conversation = st.text_area(
        "Doctor-Patient Conversation",
        height=250,
        key="conversation"
    )

    uploaded = st.file_uploader(
        "Upload Prescription",
        type=["png", "jpg", "jpeg"],
        key="prescription_upload"
    )

    if st.button("Analyze Conversation"):

        if conversation.strip() == "":
            st.error("Please enter a conversation.")
            st.stop()

        copilot = ClinicalCopilot()

        with st.spinner("Analyzing..."):
            result = copilot.analyze(conversation)

        if result.get("success") is False:
            st.error(result.get("error", "Analysis failed"))
            st.stop()

        if uploaded:
            try:
                from ocr.prescription_ocr import extract_prescription
                from patient.medicine_explainer import explain_medicines

                with open("temp_prescription.png", "wb") as f:
                    f.write(uploaded.read())

                ocr = extract_prescription("temp_prescription.png")

                result["prescription_ocr"] = ocr
                result["medicine_guide"] = explain_medicines(ocr)
            except Exception as e:
                st.warning(f"Prescription OCR / medicine explainer failed: {e}")

        # Prepare default doctor review fields
        ai_diag = ""
        if result.get("clinical_impression"):
            try:
                ai_diag = result["clinical_impression"][0]
            except Exception:
                ai_diag = str(result.get("clinical_impression"))

        st.subheader("AI Analysis Result")
        st.json(result)

        st.subheader("Doctor Review (finalize before saving)")
        diagnosis = st.text_area("Doctor Diagnosis (edit AI suggestion)", value=ai_diag, key="doctor_diagnosis")
        treatment_changes = st.text_area("Treatment Changes (one per line)", key="doctor_treatment")
        notes = st.text_area("Doctor Notes", key="doctor_notes")
        approved = st.checkbox("Approve and finalize report", value=True, key="doctor_approve")

        if st.button("Save Final Report"):
            # Attach user and patient metadata
            user_meta = st.session_state.get('user', {"role": "anonymous"})
            if user_meta.get('role') == 'patient':
                result['patient'] = user_meta.get('patient')
            else:
                # doctor
                if st.session_state.get('current_patient'):
                    result['patient'] = st.session_state.get('current_patient')
                else:
                    st.error("No patient loaded for this report. Load a patient or have them sign in.")
                    st.stop()

            result['doctor_review'] = {
                "reviewed": True,
                "approved": bool(approved),
                "diagnosis": diagnosis,
                "treatment_changes": [t for t in (treatment_changes.splitlines() if treatment_changes else []) if t.strip()],
                "notes": notes,
                "edited_fields": []
            }

            # Mark edited fields
            if diagnosis and ai_diag and diagnosis != ai_diag:
                result['doctor_review']['edited_fields'].append('Diagnosis')
            if result['doctor_review']['treatment_changes']:
                result['doctor_review']['edited_fields'].append('Treatment Plan')
            if notes:
                result['doctor_review']['edited_fields'].append('Notes')

            # Attach user metadata
            result['user'] = user_meta

            storage = DepartmentStorage()
            saved_path = storage.save(result)

            report = ReportGenerator().generate(result)

            st.success(f"Clinical Report Saved: {saved_path}")

            st.download_button(
                "Download Report",
                report,
                file_name="clinical_report.txt"
            )

            st.text_area(
                "Clinical Report",
                report,
                height=600,
                key="final_report"
            )


# Decide whether user is signed in
if 'user' not in st.session_state:
    login_page()
else:
    if st.button("Sign out"):
        del st.session_state['user']
        if 'current_patient' in st.session_state:
            del st.session_state['current_patient']
        st.experimental_rerun()
    main_app()
