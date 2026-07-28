from speech.microphone import start_microphone, audio_queue

stream = start_microphone()

while True:
    audio_chunk = audio_queue.get()

    print("Received Audio:", audio_chunk.shape)