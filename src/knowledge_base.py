import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

# Load API key for Google Gemini
genai.configure(api_key="AIzaSyDQLyCZjLZmP0uWO_WaZVdPIr-gZLmTDy0") 

# Function to generate embeddings using Gemini
def get_gemini_embedding(text):
    response = genai.embed_content(
        model="models/embedding-001",  # Correct embedding model
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]  # Extract the embedding vector

def load_knowledge_base(topic):
    """Fetch knowledge from Wikipedia and embed it using Gemini."""
    from wikipedia import summary

    print(f"Fetching knowledge on {topic} from Wikipedia...")
    raw_text = summary(topic)

    # Split text into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    texts = text_splitter.split_text(raw_text)

    # Convert text chunks to Document format
    docs = [Document(page_content=text) for text in texts]

    # Convert documents to embeddings
    print("Embedding documents...")
    doc_embeddings = [get_gemini_embedding(doc.page_content) for doc in docs]

    # ✅ FIX: Pass embeddings first, then texts
    vectorstore = FAISS.from_embeddings(doc_embeddings, texts)

    return vectorstore
