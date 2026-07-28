import json
import os

from copilot import ClinicalCopilot
from report_generator import ReportGenerator
from speech.recorder import record_audio
from speech.transcriber import transcribe
from patient.patient_lookup import get_patient
from ocr.prescription_ocr import extract_prescription
from patient.medicine_explainer import explain_medicines
from doctor.report_editor import DoctorReview
from storage.department_storage import DepartmentStorage
MAX_FOLLOWUP_ROUNDS = 2


def main():

    print("=" * 60)
    print("🏥 AI CLINICAL COPILOT")
    print("=" * 60)

    # ----------------------------
    # Patient Verification
    # ----------------------------
    print("\n🆔 Patient Verification\n")

    aadhaar = input("Enter Aadhaar Number : ")

    lookup = get_patient(aadhaar)

    if lookup["status"] == "error":
        print("❌ Patient Not Found")
        return

    patient = lookup["patient"]

    print("\n✅ Patient Found")
    print(f"Name        : {patient['name']}")
    print(f"Age         : {patient['age']}")
    print(f"Gender      : {patient['gender']}")
    print(f"Blood Group : {patient['blood_group']}")

    print("\nMedical History")
    for disease in patient["medical_history"]:
        print(f"• {disease}")

    print("\nCurrent Medications")
    for medicine in patient["current_medications"]:
        print(f"• {medicine}")

    print("\nAllergies")
    for allergy in patient["allergies"]:
        print(f"• {allergy}")

    input("\nPress ENTER to start consultation...")

    # ----------------------------
    # Step 1 : Record Consultation
    # ----------------------------
    print("\n🎤 Recording Consultation...\n")

    audio_file = record_audio("temp_audio.wav")

    if audio_file is None:
        print("❌ Recording failed.")
        return

    # ----------------------------
    # Step 2 : Speech to Text
    # ----------------------------
    print("\n📝 Transcribing...\n")

    conversation = transcribe(audio_file)

    if not conversation.strip():
        print("❌ No speech detected.")
        return

    print("\n✅ Transcript Ready\n")

    copilot = ClinicalCopilot()

    followup_round = 0

    # ----------------------------
    # Step 3 : AI Consultation Loop
    # ----------------------------
    while True:

        print("🧠 Performing Clinical Analysis...\n")

        result = copilot.analyze(conversation)

        if result.get("success") is False:
            print("❌ AI Analysis Failed")
            print(result.get("error"))
            return

        questions = result.get("follow_up_questions", [])

        if not questions:
            print("✅ Consultation Complete")
            break

        if followup_round >= MAX_FOLLOWUP_ROUNDS:
            print("⚠ Maximum Follow-up Rounds Reached")
            break

        print("\n" + "=" * 60)
        print("🤖 AI FOLLOW-UP QUESTIONS")
        print("=" * 60)

        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")

        input("\nPress ENTER after asking the patient...")

        follow_audio = record_audio(f"followup_{followup_round + 1}.wav")

        if follow_audio is None:
            break

        follow_text = transcribe(follow_audio)

        if not follow_text.strip():
            break

        conversation += "\n\nFOLLOW-UP CONSULTATION:\n"
        conversation += follow_text

        followup_round += 1

    # ----------------------------
    # Doctor Review Screen
    # ----------------------------
    print("\n" + "=" * 60)
    print("🏥 AI CLINICAL REPORT READY")
    print("=" * 60)

    print(f"Department : {result['patient']['department']}")
    print(f"Risk Level : {result['risk_assessment']['risk_level']}")
    print(f"Triage     : {result['triage']['urgency']}")
    print(f"Confidence : {result['metadata']['model_confidence'] * 100:.0f}%")

    print("\n1. Generate Report")
    print("2. Record More Information")
    print("3. Exit")

    choice = input("\nChoice: ")

    if choice == "2":

        extra_audio = record_audio("extra_info.wav")

        if extra_audio:

            extra_text = transcribe(extra_audio)

            if extra_text.strip():

                conversation += "\n\nADDITIONAL INFORMATION:\n"
                conversation += extra_text

                print("\n🧠 Updating Report...\n")

                result = copilot.analyze(conversation)

    elif choice == "3":
        return

    # ----------------------------
    # Consultation Dashboard
    # ----------------------------
    metrics = result["consultation_metrics"]

    print("\n" + "=" * 60)
    print("📊 CONSULTATION DASHBOARD")
    print("=" * 60)

    print(f"Completeness : {metrics['information_completeness']}%")
    print(f"Quality      : {metrics['consultation_quality']}")
    print(f"Missing Info : {metrics['missing_information_count']}")

    print("\n🧠 AI Confidence")
    print(f"{result['metadata']['model_confidence'] * 100:.0f}%")

    missing = result.get("missing_information", [])

    if missing:
        print("\nReduced because:")
        for item in missing[:5]:
            print(f"• {item}")

    if followup_round > 0:
        print("\n" + "=" * 60)
        print("✅ CONSULTATION UPDATED")
        print("=" * 60)
        print(f"Follow-up Rounds : {followup_round}")
        print(f"Remaining Missing Information : {len(missing)}")
    # ----------------------------
    # Prescription OCR
    # ----------------------------
    print("\n📸 Upload Prescription")

    image_path = input("Prescription Image Path (Press ENTER to skip): ").strip()

    if image_path:
        try:
            print("🔍 Reading Prescription...")

            ocr_result = extract_prescription(image_path)

            medicine_guide = explain_medicines(
                ocr_result["medicines"]
            )

            result["prescription_ocr"] = ocr_result
            result["medicine_guide"] = medicine_guide

            print("✅ Prescription Successfully Added")

        except Exception as e:
            print("❌ OCR Failed")
            print(e)

    # ----------------------------
    # Save Outputs
    # ----------------------------
    os.makedirs("outputs", exist_ok=True)

    with open("outputs/extracted.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    review = DoctorReview()

    result = review.review(result)
    storage = DepartmentStorage()

    saved_path = storage.save(result)

    print(f"\n📁 Department Record Saved:")
    print(saved_path)
    report_generator = ReportGenerator()

    report = report_generator.generate(result)

    with open("outputs/clinical_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    report_generator.generate_pdf(
        result,
        "outputs/clinical_report.pdf"
    )

    print("\n")
    print(report)

    print("\n============================================================")
    print("🏥 AI CLINICAL COPILOT")
    print("============================================================")
    print("✅ Consultation Successfully Processed")
    print("📄 Clinical Report Saved")
    print("📑 PDF Report Saved")
    print("📂 Structured JSON Saved")
    print("============================================================")
if __name__ == "__main__":
    main()