import cv2
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from fpdf import FPDF
from datetime import datetime
import os

# Load TrOCR model and processor
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

# Input video path
VIDEO_PATH = "lecture_video.mp4"

# Output PDF path
PDF_PATH = "updated_lecture_notes.pdf"

# Function to extract text using TrOCR
def extract_text_from_frame(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pixel_values = processor(images=frame_rgb, return_tensors="pt").pixel_values
    with torch.no_grad():
        generated_ids = model.generate(pixel_values)
    extracted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return extracted_text

# Function to process video and extract text
def extract_text_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    extracted_text_data = []
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process every nth frame (reduce processing load)
        if frame_count % fps == 0:
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000  # Convert to seconds
            extracted_text = extract_text_from_frame(frame)
            formatted_time = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

            print(f"[{formatted_time}] {extracted_text}")  # Debug: Show extracted text
            extracted_text_data.append((formatted_time, extracted_text))

        frame_count += 1

    cap.release()
    return extracted_text_data

# Function to write extracted text into the PDF
def integrate_text_into_pdf(pdf_path, text_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Lecture Notes with Extracted Board Text", ln=True, align="C")
    pdf.ln(10)  # Add some space

    for timestamp, text in text_data:
        pdf.set_font("Arial", style="B", size=10)
        pdf.cell(0, 10, f"[{timestamp}]", ln=True)  # Add timestamp

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, text)  # Add extracted text with line wrapping
        pdf.ln(5)  # Add space

    pdf.output(pdf_path, "F")
    print("✅ PDF successfully updated with extracted text!")

# Run the pipeline
print("🎥 Extracting text from lecture video...")
text_data = extract_text_from_video(VIDEO_PATH)

print("📄 Integrating extracted text into PDF...")
integrate_text_into_pdf(PDF_PATH, text_data)
print(text_data)