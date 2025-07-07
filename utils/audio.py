import whisper
from gtts import gTTS

# Load Whisper model only once
model = whisper.load_model("base")

def speech_to_text(audio_path: str) -> str:
    """Transcribes voice input to text using Whisper."""
    result = model.transcribe(audio_path)
    return result["text"]

def text_to_speech(text: str, output_path: str = "response.mp3"):
    """Converts text response to speech using gTTS."""
    tts = gTTS(text)
    tts.save(output_path)
