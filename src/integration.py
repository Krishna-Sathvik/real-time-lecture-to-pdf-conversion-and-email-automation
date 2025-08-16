import os
from speech_to_text import transcribe_audio
from fact_check_pipeline import process_lecture_statement

# Path to the audio file
AUDIO_PATH = "data/audio/cleaned_audio.wav"

if __name__ == "__main__":
    # Step 1: Transcribe audio to text
    print("🎙️ Transcribing audio...")
    transcribed_text = transcribe_audio(AUDIO_PATH)

    if not transcribed_text.strip():
        print("❌ No transcription available. Exiting...")
        exit()

    print("\n✅ Transcription Complete:\n", transcribed_text)

    # Step 2: Process transcription through fact-check pipeline
    print("\n🔍 Fact-checking and expanding knowledge...")
    result = process_lecture_statement(transcribed_text)

    # Step 3: Display results
    print("\n📖 Corrected Statement:\n", result["corrected_statement"])

