from faster_whisper import WhisperModel

print("Loading model...")

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

print("Model loaded successfully!")

segments, info = model.transcribe(
    "temp_audio.wav",
    beam_size=5,
    language="en",
    vad_filter=True
)

print("\nDetected language:", info.language)
print("\nTranscript:\n")

for segment in segments:
    print(segment.text)