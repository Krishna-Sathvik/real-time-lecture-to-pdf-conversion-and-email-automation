import subprocess
import os
# Define file paths
video_output = "data/videos/lecture_video.mp4"

# Ensure the output directory exists
os.makedirs(os.path.dirname(video_output), exist_ok=True)

# FFmpeg command to capture video and audio
ffmpeg_cmd = [
    "ffmpeg",
    "-y",  # Overwrite existing files
    "-f", "dshow",  # Use DirectShow (Windows)
    "-rtbufsize", "1G",  # Increase buffer size for long recordings
    "-i", "video=USB2.0 FHD UVC WebCam:audio=Microphone Array (2- Intel® Smart Sound Technology for Digital Microphones)",  
    "-vcodec", "libx264",  # Use H.264 encoding
    "-preset", "ultrafast",  # Fast encoding (reduce CPU load)
    "-acodec", "aac",  # Audio encoding
    "-b:a", "128k",  # Audio bitrate
    "-strict", "experimental",  # Allow experimental features
    "-video_size", "1280x720",  # Reduce resolution to improve stability
    "-framerate", "25",  # Lower frame rate to prevent frame drops
    
    video_output
]
print("Recording... Press Ctrl+C to stop.")
try:
    subprocess.run(ffmpeg_cmd, check=True)
except KeyboardInterrupt:
    print("\nRecording stopped.")

print(f"Recording saved at: {video_output}")
