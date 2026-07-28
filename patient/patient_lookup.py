import json
import os


PATIENT_FILE = os.path.join(
    os.path.dirname(__file__),
    "patients.json"
)


def get_patient(aadhaar: str):

    with open(PATIENT_FILE, "r", encoding="utf-8") as file:
        patients = json.load(file)

    for patient in patients:

        if patient["aadhaar"] == aadhaar:
            return {
                "status": "success",
                "patient": patient
            }

    return {
        "status": "error",
        "message": "Patient not found"
    }