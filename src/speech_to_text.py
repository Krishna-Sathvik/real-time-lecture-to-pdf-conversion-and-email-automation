import librosa
import soundfile as sf
import torch
import numpy as np
import ctypes
from deepmultilingualpunctuation import PunctuationModel
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

# Load Wav2Vec2 Model
MODEL_NAME = "facebook/wav2vec2-large-960h-lv60-self"
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME).to("cpu")

# Load Punctuation Model
punctuation_model = PunctuationModel()

# Load SpeexDSP Library (If noise reduction needs to be applied here)
speex_dll = ctypes.CDLL("C:/vcpkg/installed/x64-windows/bin/libspeexdsp.dll")

# SpeexDSP Constants
FRAME_SIZE = 160
SAMPLE_RATE = 16000

# Initialize Speex Noise Suppression (if applied here)
speex_dll.speex_preprocess_state_init.restype = ctypes.c_void_p
speex_dll.speex_preprocess_run.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_short)]
ns_state = speex_dll.speex_preprocess_state_init(FRAME_SIZE, SAMPLE_RATE)
if not ns_state:
    raise RuntimeError("❌ Failed to initialize Speex Noise Suppression.")

def transcribe_audio(audio_path):
    """Transcribes audio using Wav2Vec2 and applies punctuation restoration."""
    speech_array, sr = librosa.load(audio_path, sr=SAMPLE_RATE)

    # Debugging info
    print(f"📌 Loaded audio: {audio_path}")
    print(f"🎙️ Sample Rate: {sr}")
    print(f"📏 Duration: {len(speech_array) / sr:.2f} seconds")
    print(f"🔊 Max Amplitude: {max(speech_array):.4f}")
    
    if len(speech_array) == 0:
        print("❌ Error: Audio is empty!")
        return ""

    input_values = processor(speech_array, return_tensors="pt", sampling_rate=16000).input_values

    with torch.no_grad():
        logits = model(input_values).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    raw_transcription = processor.batch_decode(predicted_ids)[0]

    print("\n📝 Raw Transcription Before Punctuation:\n", raw_transcription)

    if len(raw_transcription.strip()) == 0:
        print("❌ Error: No speech detected after transcription!")
        return ""

    # Apply punctuation restoration
    transcribed_text = punctuation_model.restore_punctuation(raw_transcription)
    
    return transcribed_text

if __name__ == "__main__":
    audio_path = "data/audio/cleaned_audio.wav"  # ✅ Uses noise-reduced audio from `noise_reduction.py`
    
    # Process & Transcribe
    transcribed_text = transcribe_audio(audio_path)
    
    print("\n✅ Final Transcription with Punctuation:\n", transcribed_text)
