from speech.microphone import record_audio
from speech.transcriber import transcribe

audio = record_audio(duration=5)

print("\n📝 Transcribing...\n")

text = transcribe(audio)

print("Transcript:")
print(text)