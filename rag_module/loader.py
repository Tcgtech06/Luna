from langchain_community.document_loaders import PyPDFLoader, TextLoader
import os

class DocumentLoader:
    def load_document(self, file_path):
        """Loads a document based on its file extension with validation."""
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check if file is empty
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError(f"File is empty (0 bytes): {os.path.basename(file_path)}")

        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            if file_extension == ".pdf":
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                
                # Validate PDF was parsed successfully
                if not docs:
                    raise ValueError(f"PDF file appears to be empty or corrupted: {os.path.basename(file_path)}")
                
                # Check if PDF has any text content
                total_text = "".join([doc.page_content for doc in docs]).strip()
                if not total_text:
                    raise ValueError(f"PDF contains no extractable text (might be images only): {os.path.basename(file_path)}")
                
                return docs
                
            elif file_extension == ".txt":
                loader = TextLoader(file_path, encoding='utf-8')
                docs = loader.load()
                
                # Validate text file has content
                if not docs or not docs[0].page_content.strip():
                    raise ValueError(f"Text file is empty: {os.path.basename(file_path)}")
                    
                return docs
            else:
                raise ValueError(f"Unsupported file type: {file_extension}. Only .pdf and .txt are supported.")
                
        except Exception as e:
            # Re-raise with more context
            filename = os.path.basename(file_path)
            if "password" in str(e).lower():
                raise ValueError(f"PDF is password-protected: {filename}. Please upload an unprotected version.")
            elif "encrypted" in str(e).lower():
                raise ValueError(f"PDF is encrypted: {filename}. Please upload an unencrypted version.")
            else:
                # Re-raise original exception if it's already a ValueError or FileNotFoundError
                if isinstance(e, (ValueError, FileNotFoundError)):
                    raise
                # Otherwise wrap it
                raise ValueError(f"Error loading {filename}: {str(e)}")
