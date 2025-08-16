import os
import wikipedia
import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from fact_check import fact_check_statement

# Load Pegasus-X model
MODEL_NAME = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(MODEL_NAME)
model = PegasusForConditionalGeneration.from_pretrained(MODEL_NAME)

# Load API keys
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '').strip()
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set.")

# Function to summarize a batch of sentences
def summarize_text(sentences):
    try:
        text = " ".join(sentences)  # Merge sentences into a single passage
        tokens = tokenizer(text, truncation=True, padding="longest", return_tensors="pt")
        summary_ids = model.generate(**tokens, max_length=200, num_beams=5, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
    except Exception as e:
        print(f"Summarization Error: {e}")
        return " ".join(sentences)

# Main pipeline function for batch processing
def process_lecture_statements(statements):
    # Step 1: Fact-check all sentences
    corrected_statements = [fact_check_statement(sentence) for sentence in statements]

    # Step 2: Summarize the corrected statements together
    summarized_text = summarize_text(corrected_statements)

    return {
        "corrected_statements": corrected_statements,
        "summarized_text": summarized_text
    }

# Example Usage
if __name__ == "__main__":
    statements = [
        "The sun rises in the North.",
        "Water boils at 50 degrees Celsius.",
        "The Earth is the center of the universe."
    ]
    result = process_lecture_statements(statements)

    print("\nCorrected Statements:", result["corrected_statements"])
    print("\nSummarized Text:", result["summarized_text"])
