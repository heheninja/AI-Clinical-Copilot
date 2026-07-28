from speech.transcriber import transcribe

text = transcribe("temp_audio.wav")

print("\nTranscript:\n")
print(text)