from gtts import gTTS
import os

os.makedirs("temp", exist_ok=True)  # Make sure temp/ exists

# Generate speech
tts = gTTS("This is a test")
tts.save("temp/test.mp3")

print("✅ test.mp3 saved successfully in temp/")
