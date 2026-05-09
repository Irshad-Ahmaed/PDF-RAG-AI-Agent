import os
from pathlib import Path
from typing import List
from google import genai
from google.genai import types
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

EMBEDDING_MODEL = "gemini-embedding-2"
EMBED_DIM = 768

# Split the text into chunks of 1000 characters with an overlap of 200 characters
splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

# Function to load a PDF file, extract the text, and split it into chunks
def load_chunk_pdf(path: str) -> list[str]:
    file_path = Path(path)
    docs = PDFReader().load_data(file=file_path)
    # Extract the text from the documents, ensuring that we only include those that have a 'text' attribute
    texts = [d.text for d in docs if getattr(d, "text", None)]
    chunks = []
    for t in texts:
        # Split the text into chunks and add them to the list of chunks
        chunks.extend(splitter.split_text(t))
    return chunks


# Function to embed a list of texts using the Gemini embedding model
def embed_texts(texts: list[str]) -> list[list[float]]:
    # response = client.models.embed_content(
    #     model=EMBEDDING_MODEL,
    #     contents=[str(t) for t in texts]
    # )

    # if response.embeddings is None:
    #     raise RuntimeError("No embeddings returned from API")
    
    # embeddings: List[List[float]] = []

    # for e in response.embeddings:
    #     if e.values is None:
    #         raise ValueError("Embedding returned None")
    #     embeddings.append(e.values)
# --------
    embeddings: List[List[float]] = []
    
    # gemini-embedding-2 aggregates multiple inputs into one embedding,
    # so we need to embed each text individually
    for text in texts:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=[str(text)],
            config=types.EmbedContentConfig(output_dimensionality=EMBED_DIM)
        )
        
        if response.embeddings is None:
            raise RuntimeError("No embeddings returned from API")
        
        for e in response.embeddings:
            if e.values is None:
                raise ValueError("Embedding returned None")
            embeddings.append(e.values)

    return embeddings