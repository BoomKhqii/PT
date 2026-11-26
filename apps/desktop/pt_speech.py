import io
import re
import wave
import winsound


def speak(text, voice):
    if not text.strip():
        return
    audio = io.BytesIO()
    with wave.open(audio, "wb") as wav_file:
        voice.synthesize_wav(re.sub(r"\bJa\b", "Jah", text), wav_file)
    winsound.PlaySound(audio.getvalue(), winsound.SND_MEMORY)
