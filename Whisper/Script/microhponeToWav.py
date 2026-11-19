import sounddevice as sd
from scipy.io.wavfile import write

fs = 44100  # Sample rate (CD quality)
seconds = 5  # Duration of recording

print("Recording...")
# Capture audio into a NumPy array
myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
sd.wait()  # Wait until recording is finished
print("Finished recording.")

# Save as WAV file
write('output.wav', fs, myrecording)
