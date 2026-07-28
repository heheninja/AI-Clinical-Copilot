import wave

from faster_whisper import WhisperModel


# Load Whisper model once
model = WhisperModel(
    "large-v3",
    device="cpu",
    compute_type="int8"
)


def transcribe(audio_path: str) -> str:
    """
    Transcribes an audio file using Faster-Whisper.
    """

    # ==========================================
    # Audio Information
    # ==========================================
    try:
        with wave.open(audio_path, "rb") as wf:
            print("\n========== AUDIO INFO ==========")
            print(f"Channels      : {wf.getnchannels()}")
            print(f"Sample Width  : {wf.getsampwidth()} bytes")
            print(f"Sample Rate   : {wf.getframerate()} Hz")
            print(
                f"Duration      : "
                f"{wf.getnframes() / wf.getframerate():.2f} seconds"
            )
            print("================================\n")

    except Exception as e:
        print(f"❌ Could not read audio info: {e}")

    # ==========================================
    # Speech to Text
    # ==========================================
    segments, info = model.transcribe(
        audio_path,
        language="en",
        initial_prompt=(
            "This is a medical consultation between a doctor "
            "and a patient in a hospital."
        ),
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=300
        ),
        condition_on_previous_text=False
    )

    print(
        f"Detected language: "
        f"{info.language} "
        f"({info.language_probability:.2f})"
    )

    transcript = ""

    print("\n========== TRANSCRIPT ==========")

    for segment in segments:
        print(
            f"[{segment.start:.2f}s - {segment.end:.2f}s] "
            f"{segment.text}"
        )
        transcript += segment.text + " "

    print("================================\n")

    return transcript.strip()