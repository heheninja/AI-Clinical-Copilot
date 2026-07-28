import queue
import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 1

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status)

    audio_queue.put(indata.copy())


def start_microphone():
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        callback=audio_callback
    )

    stream.start()

    print("🎤 Listening...")

    return stream