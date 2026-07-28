import json
import os
from datetime import datetime


class DepartmentStorage:

    def save(self, report):

        department = (
            report.get("patient", {})
            .get("department", "General")
            .replace(" ", "_")
        )

        folder = os.path.join("hospital_data", department)
        os.makedirs(folder, exist_ok=True)

        patient = report.get("patient", {})

        filename = (
            f"{patient.get('chief_complaint', 'Patient')}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        # Remove invalid filename characters
        filename = filename.replace("/", "_").replace("\\", "_").replace(":", "-")

        filepath = os.path.join(folder, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        return filepath