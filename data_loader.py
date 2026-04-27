import os
from google import genai
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

EMBEDDING_MODEL = "text-embedding-004"
EMBED_DIM = 3072

# Split the text into chunks of 1000 characters with an overlap of 200 characters
splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

# Function to load a PDF file, extract the text, and split it into chunks
def load_chunk_pdf(path: str):
    docs = PDFReader().load_data(file=path)
    # Extract the text from the documents, ensuring that we only include those that have a 'text' attribute
    texts = [d.text for d in docs if getattr(d, "text", None)]
    chunks = []
    for t in texts:
        # Split the text into chunks and add them to the list of chunks
        chunks.extend(splitter.split_text(t))
    return chunks


# Function to embed a list of texts using the Gemini embedding model
def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [e.embedding for e in response.data]