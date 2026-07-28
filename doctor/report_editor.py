from copy import deepcopy


class DoctorReview:

    def review(self, result):

        reviewed = deepcopy(result)

        reviewed["doctor_review"] = {
            "reviewed": True,
            "approved": True,
            "edited_fields": [],
            "diagnosis": "",
            "treatment_changes": [],
            "notes": ""
        }

        print("\n" + "=" * 60)
        print("👨‍⚕️ DOCTOR REVIEW")
        print("=" * 60)

        ai_diag = ""

        if reviewed.get("clinical_impression"):
            ai_diag = reviewed["clinical_impression"][0]

        print(f"\nAI Diagnosis:\n{ai_diag}")

        new_diag = input("\nDoctor Diagnosis (ENTER to keep AI): ").strip()

        if new_diag:
            reviewed["doctor_review"]["diagnosis"] = new_diag
            reviewed["doctor_review"]["edited_fields"].append("Diagnosis")
        else:
            reviewed["doctor_review"]["diagnosis"] = ai_diag

        print("\nTreatment Changes")
        print("Enter one per line.")
        print("Press ENTER on empty line to finish.\n")

        while True:

            item = input("> ").strip()

            if item == "":
                break

            reviewed["doctor_review"]["treatment_changes"].append(item)

        if reviewed["doctor_review"]["treatment_changes"]:
            reviewed["doctor_review"]["edited_fields"].append("Treatment Plan")

        notes = input("\nDoctor Notes: ").strip()

        reviewed["doctor_review"]["notes"] = notes

        if notes:
            reviewed["doctor_review"]["edited_fields"].append("Notes")

        return reviewed