from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import Config

class TextProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
        )

    def split_documents(self, documents):
        """Splits a list of documents into chunks."""
        return self.text_splitter.split_documents(documents)
