import subprocess

# Input video file (recorded earlier)
video_input = "data/videos/lecture_video.mp4"
audio_output = "data/audio/lecture_audio.wav"

# Ensure directories exist
import os
os.makedirs(os.path.dirname(audio_output), exist_ok=True)

# FFmpeg command to extract audio
ffmpeg_cmd = [
    "ffmpeg",
    "-i", video_input,  # Input video
    "-vn",  # No video
    "-acodec", "pcm_s16le",  # Uncompressed WAV format
    "-ar", "16000",  # 16kHz sample rate (for Wav2Vec 2.0)
    "-ac", "1",  # Mono channel
    audio_output
]

# Run FFmpeg
subprocess.run(ffmpeg_cmd, check=True)
print(f"Audio extracted: {audio_output}")
