from fpdf import FPDF
import os
from integration import process_lecture_statement
from speech_to_text import transcribe_audio

# Path to the processed audio file
AUDIO_PATH = "data/audio/cleaned_audio.wav"

from fpdf import FPDF

def generate_pdf(corrected_statement, expanded_info, output_path="lecture_notes.pdf"):
    """Generates a PDF with only corrected lecture content and knowledge expansion."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 🔹 Use a Unicode-supporting font (DejaVuSans, Arial Unicode, or Times)
    pdf.add_font("Arial", "", "C:/Windows/Fonts/arial.ttf", uni=True)  # Windows
    # pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)  # Linux

    pdf.set_font("Arial", size=12)  # Use the newly added font

    # Title
    pdf.cell(200, 10, "Lecture Notes", ln=True, align="C")
    pdf.ln(10)

    # Content Section (Corrected Statements)
    pdf.cell(0, 10, "Content:", ln=True)
    pdf.multi_cell(0, 10, corrected_statement)  # 🔹 No encoding issue with Unicode fonts
    pdf.ln(5)

    # Knowledge Expansion Section
    pdf.cell(0, 10, "Knowledge Expansion:", ln=True)
    pdf.multi_cell(0, 10, expanded_info)

    # Save PDF
    pdf.output(output_path)
    print(f"✅ PDF saved as {output_path}")



if __name__ == "__main__":
    # Step 1: Transcribe the audio
    print("🎙️ Transcribing audio...")
    transcribed_text = transcribe_audio(AUDIO_PATH)

    if not transcribed_text.strip():
        print("❌ No transcription available. Exiting...")
        exit()

    print("\n✅ Transcription Complete:\n", transcribed_text)

    # Step 2: Process transcription through fact-checking
    print("\n🔍 Fact-checking lecture content...")
    result = process_lecture_statement(transcribed_text)

    # Step 3: Generate the PDF with corrected content and knowledge expansion
    print("Fact-checking result:", result)
    generate_pdf(result["corrected_statement"], result["expanded_info"])
