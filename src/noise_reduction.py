import ctypes
import numpy as np
import soundfile as sf

# Load SpeexDSP Library (Ensure correct path)
speex_dll = ctypes.CDLL("C:/vcpkg/installed/x64-windows/bin/libspeexdsp.dll")

# Define Speex Constants
FRAME_SIZE = 160  # Speex frame size (should match sample rate)
SAMPLE_RATE = 16000  # Must match your input audio

# Initialize Speex Noise Suppression
speex_dll.speex_preprocess_state_init.restype = ctypes.c_void_p
speex_dll.speex_preprocess_ctl.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
speex_dll.speex_preprocess_run.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_short)]

ns_state = speex_dll.speex_preprocess_state_init(FRAME_SIZE, SAMPLE_RATE)
if not ns_state:
    raise RuntimeError("❌ Failed to initialize Speex Noise Suppression.")

# 🔧 Adjust Noise Suppression Level
NOISE_SUPPRESS_LEVEL = -15  # Keep speech clear
AGC_LEVEL = 30000  # Automatic Gain Control (boosts weak voices)

# ✅ Set Speex Parameters
speex_dll.speex_preprocess_ctl(ns_state, 0, ctypes.byref(ctypes.c_int(NOISE_SUPPRESS_LEVEL)))  
speex_dll.speex_preprocess_ctl(ns_state, 1, ctypes.byref(ctypes.c_int(1)))  # Enable VAD
speex_dll.speex_preprocess_ctl(ns_state, 2, ctypes.byref(ctypes.c_int(AGC_LEVEL)))  # Enable AGC

def speex_noise_suppress(audio_data):
    """Applies Speex noise suppression while keeping speech clear."""
    
    # Ensure audio is mono
    if audio_data.ndim > 1:
        audio_data = audio_data.mean(axis=1)  # Convert to mono
    
    # Convert to int16
    audio_data = (audio_data * 32768).astype(np.int16)

    num_samples = len(audio_data)
    num_frames = num_samples // FRAME_SIZE

    processed_audio = np.zeros_like(audio_data, dtype=np.int16)

    for i in range(num_frames):
        frame = np.ascontiguousarray(audio_data[i * FRAME_SIZE:(i + 1) * FRAME_SIZE], dtype=np.int16)
        frame_ptr = frame.ctypes.data_as(ctypes.POINTER(ctypes.c_short))
        
        # ✅ Correctly pass ns_state
        speex_dll.speex_preprocess_run(ctypes.c_void_p(ns_state), frame_ptr)

        processed_audio[i * FRAME_SIZE:(i + 1) * FRAME_SIZE] = frame

    return processed_audio.astype(np.float32) / 32768.0  # Normalize back to float

def process_audio(input_path, output_path):
    """Loads audio, applies noise suppression, and saves it."""
    # ✅ Read audio correctly (force mono if stereo)
    speech_array, sr = sf.read(input_path, dtype='float32', always_2d=True)
    
    # ✅ Convert to mono if stereo
    if speech_array.shape[1] > 1:
        speech_array = speech_array.mean(axis=1)

    # Apply Speex noise suppression
    speech_array = speex_noise_suppress(speech_array)

    # ✅ Convert back to int16 before saving
    speech_array = (speech_array * 32768).astype(np.int16)

    # Save the cleaned audio
    sf.write(output_path, speech_array, sr)
    print(f"✅ Cleaned audio saved to: {output_path}")

if __name__ == "__main__":
    process_audio("data/audio/lecture_audio.wav", "data/audio/cleaned_audio.wav")
