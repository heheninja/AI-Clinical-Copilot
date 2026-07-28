import io
import os
from typing import List
from dotenv import dotenv_values
from PIL import Image

config = dotenv_values(".env")
OCR_SPACE_API_KEY = config.get("OCR_SPACE_API_KEY")

# If requests is not installed, the import will fail — the requirements.txt includes it.
try:
    import requests
except Exception:
    requests = None


def extract_prescription_from_bytes(image_bytes: bytes) -> List[str]:
    """Extract text lines from prescription image bytes.

    Preference order:
    1) OCR.space API if OCR_SPACE_API_KEY is provided.
    2) pytesseract local OCR if available (requires tesseract installed).

    Returns a list of non-empty lines detected.
    """

    # Try OCR.space if API key present
    if OCR_SPACE_API_KEY and requests is not None:
        url = "https://api.ocr.space/parse/image"
        files = {
            'file': ('prescription.png', image_bytes)
        }
        data = {
            'apikey': OCR_SPACE_API_KEY,
            'language': 'eng',
            'isOverlayRequired': False
        }
        try:
            r = requests.post(url, files=files, data=data, timeout=60)
            r.raise_for_status()
            result = r.json()
            parsed = []
            if result.get('IsErroredOnProcessing'):
                # Fall through to local OCR
                print("OCR.space reported an error; falling back to local OCR if available.")
            else:
                for parsed_result in result.get('ParsedResults', []):
                    text = parsed_result.get('ParsedText', '')
                    parsed.extend([line.strip() for line in text.splitlines() if line.strip()])
                if parsed:
                    return parsed
        except Exception as e:
            print(f"OCR.space request failed: {e}; falling back to local OCR.")

    # Fallback: pytesseract (local tesseract must be installed)
    try:
        import pytesseract
    except Exception:
        pytesseract = None

    if pytesseract is not None:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            text = pytesseract.image_to_string(image)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return lines
        except Exception as e:
            print(f"pytesseract OCR failed: {e}")

    # As a last resort, attempt to use PIL's basic getdata (not real OCR) — return empty
    raise RuntimeError("No OCR method succeeded. Configure OCR_SPACE_API_KEY for OCR.space or install tesseract + pytesseract for local OCR.")


def extract_prescription(path_or_bytes) -> List[str]:
    """Compatibility wrapper: accepts a filepath or raw bytes and returns OCR lines."""
    if isinstance(path_or_bytes, (bytes, bytearray)):
        return extract_prescription_from_bytes(bytes(path_or_bytes))
    elif isinstance(path_or_bytes, str) and os.path.exists(path_or_bytes):
        with open(path_or_bytes, "rb") as f:
            return extract_prescription_from_bytes(f.read())
    else:
        raise ValueError("extract_prescription expects either image bytes or a path to an existing file")
