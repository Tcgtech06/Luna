import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from .config import Config

class VectorStore:
    def __init__(self):
        self.persist_directory = Config.PERSIST_DIRECTORY
        self.embedding_function = self._get_embedding_function()
        self.db = None

    def _get_embedding_function(self, model_name=None):
        """Returns the Google GenAI embedding function with fallback support."""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found. Please set it in your environment or .env file.")
        
        # Use specified model or default to first in list
        if model_name is None:
            model_name = Config.EMBEDDING_MODEL
            
        return GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=Config.GOOGLE_API_KEY
        )

    def _try_embedding_models(self, chunks, batch_size):
        """Try different embedding models if one fails due to rate limits."""
        import time
        
        for model_idx, model_name in enumerate(Config.EMBEDDING_MODELS):
            try:
                print(f"DEBUG: Trying embedding model {model_idx + 1}/{len(Config.EMBEDDING_MODELS)}: {model_name}")
                
                # Update embedding function for this model
                self.embedding_function = self._get_embedding_function(model_name)
                
                # Try to process the chunks
                return self._process_chunks_with_model(chunks, batch_size, model_name)
                
            except Exception as e:
                error_str = str(e)
                print(f"DEBUG: Model {model_name} failed: {error_str}")
                
                if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                    if model_idx < len(Config.EMBEDDING_MODELS) - 1:
                        print(f"DEBUG: Rate limit hit for {model_name}, trying next model...")
                        time.sleep(5)  # Brief pause before trying next model
                        continue
                    else:
                        raise Exception("All embedding models have hit rate limits. Please wait a few minutes and try again.")
                else:
                    # Non-rate-limit error, try next model
                    if model_idx < len(Config.EMBEDDING_MODELS) - 1:
                        print(f"DEBUG: Error with {model_name}, trying next model...")
                        continue
                    else:
                        raise e
        
        raise Exception("All embedding models failed")

    def _process_chunks_with_model(self, chunks, batch_size, model_name):
        """Process chunks with a specific embedding model."""
        import time
        import os
        
        total_chunks = len(chunks)
        
        # Check if database already exists
        if os.path.exists(self.persist_directory):
            print(f"DEBUG: Vector DB exists, loading and appending {total_chunks} chunks with {model_name}...")
            # Load existing database
            self.db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function
            )
            
            # Process in batches for large documents with rate limiting
            if total_chunks > batch_size:
                total_batches = (total_chunks + batch_size - 1) // batch_size
                for i in range(0, total_chunks, batch_size):
                    batch = chunks[i:i+batch_size]
                    batch_num = (i // batch_size) + 1
                    print(f"DEBUG: Processing batch {batch_num}/{total_batches} ({len(batch)} chunks) with {model_name}...")
                    
                    # Add retry logic for this specific model
                    max_retries = 2
                    for attempt in range(max_retries):
                        try:
                            self.db.add_documents(batch)
                            break
                        except Exception as e:
                            error_str = str(e)
                            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                                if attempt < max_retries - 1:
                                    wait_time = (attempt + 1) * 5
                                    print(f"DEBUG: Rate limit hit for {model_name}, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                                    time.sleep(wait_time)
                                    continue
                                else:
                                    raise Exception(f"Rate limit exceeded for {model_name}")
                            else:
                                raise e
                    
                    # Add delay between batches to avoid rate limiting
                    if batch_num < total_batches:
                        time.sleep(3)  # 3 second delay between batches
            else:
                # Small document, process all at once with retry
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        self.db.add_documents(chunks)
                        break
                    except Exception as e:
                        error_str = str(e)
                        if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                            if attempt < max_retries - 1:
                                wait_time = (attempt + 1) * 5
                                print(f"DEBUG: Rate limit hit for {model_name}, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                                time.sleep(wait_time)
                                continue
                            else:
                                raise Exception(f"Rate limit exceeded for {model_name}")
                        else:
                            raise e
            
            print(f"DEBUG: Successfully appended {total_chunks} chunks to existing database using {model_name}")
        else:
            print(f"DEBUG: Creating new vector DB with {total_chunks} chunks using {model_name}...")
            
            # For very large documents, create in batches too
            if total_chunks > batch_size:
                total_batches = (total_chunks + batch_size - 1) // batch_size
                print(f"DEBUG: Large document detected, processing in {total_batches} batches...")
                
                # Create with first batch with retry logic
                first_batch = chunks[:batch_size]
                print(f"DEBUG: Creating database with first batch ({len(first_batch)} chunks) using {model_name}...")
                
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        self.db = Chroma.from_documents(
                            documents=first_batch,
                            embedding=self.embedding_function,
                            persist_directory=self.persist_directory
                        )
                        break
                    except Exception as e:
                        error_str = str(e)
                        if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                            if attempt < max_retries - 1:
                                wait_time = (attempt + 1) * 5
                                print(f"DEBUG: Rate limit hit for {model_name}, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                                time.sleep(wait_time)
                                continue
                            else:
                                raise Exception(f"Rate limit exceeded for {model_name}")
                        else:
                            raise e
                
                # Add remaining batches with rate limiting
                for i in range(batch_size, total_chunks, batch_size):
                    batch = chunks[i:i+batch_size]
                    batch_num = (i // batch_size) + 1
                    print(f"DEBUG: Processing batch {batch_num}/{total_batches} ({len(batch)} chunks) with {model_name}...")
                    
                    max_retries = 2
                    for attempt in range(max_retries):
                        try:
                            self.db.add_documents(batch)
                            break
                        except Exception as e:
                            error_str = str(e)
                            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                                if attempt < max_retries - 1:
                                    wait_time = (attempt + 1) * 5
                                    print(f"DEBUG: Rate limit hit for {model_name}, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                                    time.sleep(wait_time)
                                    continue
                                else:
                                    raise Exception(f"Rate limit exceeded for {model_name}")
                            else:
                                raise e
                    
                    # Add delay between batches
                    if batch_num < total_batches:
                        time.sleep(3)
            else:
                # Small document, create all at once with retry
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        self.db = Chroma.from_documents(
                            documents=chunks,
                            embedding=self.embedding_function,
                            persist_directory=self.persist_directory
                        )
                        break
                    except Exception as e:
                        error_str = str(e)
                        if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                            if attempt < max_retries - 1:
                                wait_time = (attempt + 1) * 5
                                print(f"DEBUG: Rate limit hit for {model_name}, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                                time.sleep(wait_time)
                                continue
                            else:
                                raise Exception(f"Rate limit exceeded for {model_name}")
                        else:
                            raise e
            
            print(f"DEBUG: Successfully created new database with {total_chunks} chunks using {model_name}")
        
        return self.db

    def create_vector_db(self, chunks, batch_size=None):
        """Creates a new vector database from document chunks or appends to existing one.
        Uses multiple embedding models with fallback when rate limited.
        """
        # Use config batch size if not specified
        if batch_size is None:
            batch_size = getattr(Config, 'EMBEDDING_BATCH_SIZE', 10)
        
        total_chunks = len(chunks)
        print(f"DEBUG: Starting vector DB creation with {total_chunks} chunks, batch size: {batch_size}")
        
        # Try different embedding models if rate limited
        return self._try_embedding_models(chunks, batch_size)

    def load_vector_db(self):
        """Loads an existing vector database."""
        if not os.path.exists(self.persist_directory):
             raise FileNotFoundError(f"No vector database found at {self.persist_directory}. Please ingest documents first.")
             
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function
        )
        return self.db

    def as_retriever(self):
        """Returns the vector store as a retriever."""
        if not self.db:
            try:
                self.load_vector_db()
            except FileNotFoundError:
                # If loading fails (e.g. first run), we can't return a retriever yet
                return None
        return self.db.as_retriever()
