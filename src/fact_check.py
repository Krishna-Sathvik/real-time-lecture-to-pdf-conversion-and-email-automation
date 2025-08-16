import os
import wikipedia
import re
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI  # Google Gemini AI
from langchain_community.vectorstores import FAISS

# Load environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '').strip()

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set. Please check your environment variables.")

# Initialize Google Gemini AI model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=GOOGLE_API_KEY)

# ✅ Function to load knowledge base using Wikipedia + Gemini
def load_knowledge_base(topic):
    try:
        # ✅ Handle Wikipedia disambiguation errors
        search_results = [res for res in wikipedia.search(topic) if "disambiguation" not in res.lower()]
        if not search_results:
            return None  # No relevant Wikipedia pages

        texts = []
        for result in search_results[:3]:  # Limit API calls
            try:
                page = wikipedia.page(result, auto_suggest=False)
                texts.append(page.content[:1000])  # Limit content size
            except Exception as e:
                print(f"⚠️ Wikipedia Page Error: {e}")

        if not texts:
            return None  # No content available

        # ✅ Initialize embeddings
        embeddings = GoogleGenerativeAIEmbeddings(api_key=GOOGLE_API_KEY)

        # ✅ Embed the documents in FAISS vectorstore
        vectorstore = FAISS.from_texts(texts, embeddings)

        return vectorstore
    except Exception as e:
        print(f"⚠️ Error loading knowledge base: {e}")
        return None

# ✅ AI-enhanced fact-checking function
def fact_check_statement(statement):
    """
    Checks if a statement is factually correct.
    If false, returns the corrected version using AI + Wikipedia.
    """
    try:
        # ✅ Extract keywords (remove punctuation & limit words)
        keywords = re.sub(r'[^\w\s]', '', statement).split()
        keywords = " ".join(keywords[:5])  # Limit to first 5 words

        # ✅ Search Wikipedia
        search_results = [res for res in wikipedia.search(keywords) if "disambiguation" not in res.lower()]
        if not search_results:
            return statement  # No relevant Wikipedia page found

        # ✅ Get Wikipedia content
        factual_data = ""
        for result in search_results[:3]:  # Limit API calls
            try:
                page = wikipedia.page(result, auto_suggest=False)
                factual_data += page.content[:1000] + "\n\n"
            except Exception:
                continue  # Skip errors

        if not factual_data:
            return statement  # Return original if Wikipedia data is empty

        # ✅ AI prompt for correction
        prompt = f"""
        You are a fact-checking AI. Verify the following statement using the reference information.
        If the statement is false, provide the correct version.
        Return only the corrected statement (if false) or the original (if true).

        **Statement:** "{statement}"

        **Reference Information:** 
        {factual_data}

        **Corrected Statement (if false, correct it accurately; if true, return the same statement):**
        """

        # ✅ Get AI-generated correction
        response = llm.invoke(prompt)
        corrected_statement = response.content.strip()

        return corrected_statement if corrected_statement else statement

    except Exception as e:
        print(f"⚠️ Fact-Checking Error: {e}")
        return statement  # If error, return original statement

# ✅ Example Usage
if __name__ == "__main__":
    
    test_statements = [
        "The sun rises in the North.",
        "Water boils at 50°C.",
        "The Earth is flat.",
        "2 + 2 = 5."
    ]

    for stmt in test_statements:
        print(f"Original: {stmt}")
        print(f"Corrected: {fact_check_statement(stmt)}\n")
