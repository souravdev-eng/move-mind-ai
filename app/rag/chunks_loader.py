import json
from pathlib import Path
from langchain_core.documents import Document


def load_processed_chunks(chunk_file_path: Path | str) -> list[Document]:
    """Load pre-processed chunks from a JSON file exported by the preprocessing notebook."""
    chunk_file_path = Path(chunk_file_path)
    with open(chunk_file_path, "r") as f:
        chunks = json.load(f)
    documents = []
    for chunk in chunks:
        documents.append(Document(page_content=chunk["page_content"], metadata=chunk["metadata"]))
    return documents
