import os
import wikipedia
import torch
import textwrap
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import WikipediaLoader  # ✅ Fixed Import
from fact_check import fact_check_statement

# Load Pegasus-X for summarization
MODEL_NAME = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(MODEL_NAME)
model = PegasusForConditionalGeneration.from_pretrained(MODEL_NAME)

# Load API Key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '').strip()
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set.")

# Function to correct lecture text
def correct_text(text):
    """Runs fact-checking and auto-correction on text."""
    try:
        return fact_check_statement(text)
    except Exception as e:
        print(f"⚠️ Fact-Checking Error: {e}")
        return text  # Return original if error occurs

# Function to expand knowledge using Wikipedia + Gemini RAG
def expand_knowledge(topic):
    """Retrieves additional information about a topic."""
    try:
        topic = topic[:280]  # Limit topic to 280 chars to avoid API errors
        search_results = wikipedia.search(topic)

        # ✅ Filter out ambiguous results & prioritize relevant pages
        filtered_results = [res for res in search_results if "disambiguation" not in res.lower()]
        if not filtered_results:
            return "No relevant Wikipedia pages found."

        texts = []
        for result in filtered_results[:3]:  # Get up to 3 relevant pages
            try:
                page = wikipedia.page(result, auto_suggest=False)
                texts.append(page.content[:1000])  # Limit content to 1000 chars
            except Exception as e:
                print(f"⚠️ Wikipedia Page Error: {e}")

        if not texts:
            return "No additional information found."

        # ✅ Embed and store in FAISS vector store
        embeddings = GoogleGenerativeAIEmbeddings(api_key=GOOGLE_API_KEY, model="models/embedding-001")

        vectorstore = FAISS.from_texts(texts, embeddings)

        # ✅ Set up RAG retrieval using Gemini
        retriever = vectorstore.as_retriever()
        qa = RetrievalQA.from_chain_type(
            llm=ChatGoogleGenerativeAI(api_key=GOOGLE_API_KEY, model="gemini-1.5-pro"),
            retriever=retriever
        )

        response = qa.run(topic)
        return response
    except Exception as e:
        print(f"⚠️ Knowledge Expansion Error: {e}")
        return "No additional information found."

# Main function to process lecture statements
def process_lecture_statement(statement):
    """Processes lecture text by correcting statements and expanding knowledge."""
    corrected_statement = correct_text(statement)
    expanded_info = expand_knowledge(corrected_statement)

    return {
        "corrected_statement": corrected_statement,
        "expanded_info": expanded_info
    }

# Example Usage
if __name__ == "__main__":
    statement = "Golkonda fort was built by the Kakatiya dynasty in the 11th century."
    result = process_lecture_statement(statement)

    print("\n✅ Corrected Statement:", result["corrected_statement"])
    print("\n🔍 Knowledge Expansion:", result["expanded_info"])
