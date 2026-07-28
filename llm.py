from dotenv import dotenv_values

config = dotenv_values(".env")
GEMINI_API_KEY = config.get("GEMINI_API_KEY")
OPENAI_API_KEY = config.get("OPENAI_API_KEY")
OPENAI_MODEL = config.get("OPENAI_MODEL", "gpt-3.5-turbo")

# Prefer Google's GenAI client if available, otherwise fall back to OpenAI if configured.
USE_BACKEND = None

try:
    # Try to import the official Google GenAI SDK
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
        # Neither backend is usable; make imports succeed but raise at runtime
        USE_BACKEND = None
        print("No usable LLM backend configured (google.genai not installed or GEMINI_API_KEY missing; OpenAI not configured).")


def ask_gemini(prompt: str) -> str:
    """Generate text for the given prompt using the available backend.

    Returns a string with the model response. Raises RuntimeError if no backend is
    configured.
    """

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
            # response.text may exist; otherwise fall back to str(response)
            return getattr(response, "text", str(response))
        except Exception as e:
            print("\n========== GEMINI ERROR ==========")
            print(e)
            raise

    elif USE_BACKEND == "openai":
        try:
            print(f"\n🧠 Using Model (OpenAI): {MODEL_NAME}")
            # Use Chat Completions for modern OpenAI models
            resp = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                top_p=0.8,
                n=1,
            )
            # Extract the assistant reply
            return resp["choices"][0]["message"]["content"]
        except Exception as e:
            print("\n========== OPENAI ERROR ==========")
            print(e)
            raise

    else:
        raise RuntimeError("No LLM backend configured. Set GEMINI_API_KEY for Google GenAI or OPENAI_API_KEY for OpenAI in .env and install the corresponding client library.")
