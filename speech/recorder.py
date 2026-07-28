import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000


def record_audio(filename="temp_audio.wav"):
    print("\nPress ENTER to START recording...")
    input()

    # Print default recording device
    print("\n========== AUDIO DEVICE ==========")
    print("Default Device:", sd.default.device)
    try:
        print(sd.query_devices(sd.default.device[0]))
    except Exception:
        print("Could not fetch device details.")
    print("==================================\n")

    print("🎤 Recording... Press ENTER to STOP.")

    recording = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        recording.append(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=callback,
    ):
        input()

    if not recording:
        print("❌ No audio recorded.")
        return None

    audio = np.concatenate(recording, axis=0)

    # Check recording level
    max_amp = np.max(np.abs(audio))
    print(f"Max amplitude: {max_amp:.4f}")

    # Normalize if not silent
    if max_amp > 0:
        audio = audio / max_amp * 0.9

    sf.write(filename, audio, SAMPLE_RATE)

    print(f"✅ Recording saved: {filename}")

    return filename