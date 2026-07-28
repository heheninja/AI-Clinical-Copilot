from dotenv import dotenv_values

config = dotenv_values(".env")
GEMINI_API_KEY = config.get("GEMINI_API_KEY")
OPENAI_API_KEY = config.get("OPENAI_API_KEY")
OPENAI_MODEL = config.get("OPENAI_MODEL", "gpt-3.5-turbo")

USE_BACKEND = None
client = None
MODEL_NAME = None

# Try Google GenAI (Gemini) first, but import in a try/except to avoid ImportError
try:
    # import the namespace package directly (this will fail if the installed 'google' package is not the google.* namespace expected)
    import google.genai as genai
    from google.genai import types

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in .env")

    client = genai.Client(api_key=GEMINI_API_KEY)
    MODEL_NAME = "gemini-3.6-flash"
    USE_BACKEND = "genai"
    print("Using Google GenAI client (gemini)")

except Exception as _e:
    # Fallback to OpenAI if available
    try:
        import openai
    except Exception:
        openai = None

    if openai and OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        MODEL_NAME = OPENAI_MODEL
        USE_BACKEND = "openai"
        print("Falling back to OpenAI client")
    else:
        USE_BACKEND = None
        print("No usable LLM backend configured (google.genai not installed or GEMINI_API_KEY missing; OpenAI not configured).")

def ask_gemini(prompt: str) -> str:
    """Generate text for the given prompt using the available backend."""
    if USE_BACKEND == "genai":
        try:
            print(f"\n🧠 Using Model (Gemini): {MODEL_NAME}")
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    top_p=0.8,
                    response_mime_type="application/json"
                )
            )
            return getattr(response, "text", str(response))
        except Exception as e:
            print("\n========== GEMINI ERROR ==========")
            print(e)
            raise

    elif USE_BACKEND == "openai":
        try:
            print(f"\n🧠 Using Model (OpenAI): {MODEL_NAME}")
            resp = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                top_p=0.8,
                n=1,
            )
            return resp["choices"][0]["message"]["content"]
        except Exception as e:
            print("\n========== OPENAI ERROR ==========")
            print(e)
            raise

    else:
        raise RuntimeError(
            "No LLM backend configured. Set GEMINI_API_KEY for Google GenAI or OPENAI_API_KEY for OpenAI in .env and install the corresponding client library."
        )
