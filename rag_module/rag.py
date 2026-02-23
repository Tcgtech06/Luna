from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from .loader import DocumentLoader
from .processor import TextProcessor
from .vector_store import VectorStore
from .config import Config

class RAGChatbot:
    def __init__(self):
        self.loader = DocumentLoader()
        self.processor = TextProcessor()
        self.vector_store_manager = VectorStore()
        self.qa_chain = None
        self.llm = None # LLM is initialized in initialize_chat
        self.retriever = None  # Retriever is initialized in initialize_chat
        self.current_document = None  # Track most recently uploaded document
        # Load existing vector database if available
        self.vector_store_manager.load_vector_db()

    def ingest_document(self, file_path, source_name=None):
        """Loads, processes, and stores a document with source metadata."""
        import os
        import time
        
        # Use filename as source if not provided
        if not source_name:
            source_name = os.path.basename(file_path)
        
        try:
            start_time = time.time()
            print(f"[RAG] Loading document: {file_path} (source: {source_name})")
            docs = self.loader.load_document(file_path)
            
            if not docs:
                raise ValueError(f"No content extracted from {source_name}")
            
            load_time = time.time() - start_time
            print(f"[RAG] ✓ Loaded in {load_time:.1f}s - Splitting into chunks...")
            
            split_start = time.time()
            chunks = self.processor.split_documents(docs)
            
            if not chunks:
                raise ValueError(f"Document '{source_name}' produced no chunks after splitting")
            
            split_time = time.time() - split_start
            print(f"[RAG] ✓ Created {len(chunks)} chunks in {split_time:.1f}s")
            
            # Add source metadata to each chunk
            print(f"[RAG] Adding source metadata to {len(chunks)} chunks...")
            for chunk in chunks:
                chunk.metadata["source"] = source_name
                chunk.metadata["source_file"] = source_name  # For backward compatibility
            
            # Estimate processing time based on chunk count
            estimated_time = len(chunks) * 0.3  # ~0.3s per chunk average
            if len(chunks) > 100:
                print(f"[RAG] Large document detected ({len(chunks)} chunks)")
                print(f"[RAG] Estimated processing time: {estimated_time/60:.1f} minutes")
            
            print(f"[RAG] Creating vector embeddings using {Config.EMBEDDING_MODEL}...")
            embed_start = time.time()
            self.vector_store_manager.create_vector_db(chunks)
            embed_time = time.time() - embed_start
            
            total_time = time.time() - start_time
            print(f"[RAG] ✓ Document '{source_name}' processed successfully!")
            print(f"[RAG]   - Total chunks: {len(chunks)}")
            print(f"[RAG]   - Embedding time: {embed_time:.1f}s")
            print(f"[RAG]   - Total time: {total_time:.1f}s")
            
            # Set as current document for filtered retrieval
            self.current_document = source_name
            print(f"[RAG] ✓ Set '{source_name}' as active document for queries")
            
        except ValueError as e:
            # ValueError contains user-friendly messages from loader
            print(f"[RAG] ✗ Validation error: {e}")
            raise
        except FileNotFoundError as e:
            print(f"[RAG] ✗ File not found: {e}")
            raise
        except Exception as e:
            # Catch embedding or other unexpected errors
            error_msg = str(e)
            print(f"[RAG] ✗ Unexpected error processing '{source_name}': {error_msg}")
            
            # Provide helpful error messages for common issues
            if "404" in error_msg and "embedding" in error_msg.lower():
                raise ValueError(f"Embedding service error for '{source_name}'. The embedding model may be unavailable. Please try again later.")
            elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise ValueError(f"API quota exceeded while processing '{source_name}'. Please wait a moment and try again.")
            elif "api key" in error_msg.lower():
                raise ValueError(f"API key error while processing '{source_name}'. Please check your Google API key configuration.")
            else:
                raise ValueError(f"Error processing '{source_name}': {error_msg}")


    def initialize_chat(self, llm=None):
        """Initializes the QA chain using modern langchain approach with model fallback."""
        if llm:
            self.llm = llm
            
        if not self.llm:
            if Config.GOOGLE_API_KEY:
                # Get available models from model_manager
                try:
                    from model_manager import model_manager
                    available_models = model_manager.get_all_available_chat_models()
                    if not available_models:
                        raise ValueError("All models are currently exhausted. Please wait a moment.")
                    llm_models = available_models
                except:
                    llm_models = Config.LLM_MODELS
                
                # Try multiple models with fallback
                for model_name in llm_models:
                    try:
                        print(f"[RAG] Trying LLM model: {model_name}")
                        self.llm = ChatGoogleGenerativeAI(
                            model=model_name,
                            temperature=0.3,
                            google_api_key=Config.GOOGLE_API_KEY,
                            convert_system_message_to_human=True # Often needed for Gemini interactions
                        )
                        print(f"[RAG] ✓ Successfully initialized LLM with {model_name}")
                        break
                    except Exception as e:
                        error_str = str(e)
                        print(f"[RAG] ✗ Failed to initialize {model_name}: {error_str[:200]}")
                        
                        # Mark model as exhausted if quota error
                        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                            try:
                                from model_manager import model_manager
                                model_manager.handle_quota_error(model_name, error_str)
                            except:
                                pass
                        
                        if model_name == llm_models[-1]:  # Last model
                            raise ValueError(f"All LLM models failed. Last error: {error_str[:200]}")
                        continue
            else:
                 raise ValueError("No LLM provided and GOOGLE_API_KEY not found. Please set the key.")

        retriever = self.vector_store_manager.as_retriever()
        if not retriever:
            raise ValueError("Vector store is empty. Please ingest a document first.")
        
        # Create prompt template
        template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Keep the answer concise and relevant to the question.

        Context: {context}

        Question: {question}

        Helpful Answer:"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create modern langchain chain using LCEL (LangChain Expression Language)
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        self.qa_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Store retriever for later use
        self.retriever = retriever

    def ask(self, query):
        """Asks a question to the RAG system with model fallback."""
        if not self.qa_chain:
            self.initialize_chat()
            
        # Retrieve relevant documents for context
        docs = self.retriever.invoke(query)
        
        # Get available models from model_manager
        try:
            from model_manager import model_manager
            available_models = model_manager.get_all_available_chat_models()
            if not available_models:
                raise Exception("All models are currently exhausted. Please wait a moment.")
        except:
            available_models = Config.LLM_MODELS
        
        # Try multiple models for generation if one fails
        for model_name in available_models:
            try:
                # Update LLM if needed
                if not hasattr(self.llm, 'model') or self.llm.model != model_name:
                    print(f"[RAG] Switching to LLM model: {model_name}")
                    self.llm = ChatGoogleGenerativeAI(
                        model=model_name,
                        temperature=0.3,
                        google_api_key=Config.GOOGLE_API_KEY,
                        convert_system_message_to_human=True
                    )
                    
                    # Rebuild the chain with new LLM
                    retriever = self.vector_store_manager.as_retriever()
                    template = """Use the following pieces of context to answer the question at the end. 
                    If you don't know the answer, just say that you don't know, don't try to make up an answer.
                    Keep the answer concise and relevant to the question.

                    Context: {context}

                    Question: {question}

                    Helpful Answer:"""
                    
                    prompt = PromptTemplate(
                        template=template,
                        input_variables=["context", "question"]
                    )
                    
                    def format_docs(docs):
                        return "\n\n".join(doc.page_content for doc in docs)
                    
                    self.qa_chain = (
                        {"context": retriever | format_docs, "question": RunnablePassthrough()}
                        | prompt
                        | self.llm
                        | StrOutputParser()
                    )
                
                # Invoke the chain with the question
                result = self.qa_chain.invoke(query)
                print(f"[RAG] ✓ Successfully generated response with {model_name}")
                
                return {
                    "answer": result,
                    "source_documents": docs
                }
                
            except Exception as e:
                error_str = str(e)
                print(f"[RAG] ✗ Model {model_name} failed: {error_str[:200]}")
                
                if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower() or "RESOURCE_EXHAUSTED" in error_str:
                    # Mark model as exhausted
                    try:
                        from model_manager import model_manager
                        model_manager.handle_quota_error(model_name, error_str)
                    except:
                        pass
                    
                    if model_name != available_models[-1]:  # Not the last model
                        print(f"[RAG] Rate limit hit for {model_name}, trying next model...")
                        continue
                    else:
                        raise Exception("All LLM models have hit rate limits. Please wait a few minutes and try again.")
                else:
                    if model_name != available_models[-1]:  # Not the last model
                        print(f"[RAG] Error with {model_name}, trying next model...")
                        continue
                    else:
                        raise e
        
        raise Exception("All LLM models failed")

    def retrieve_documents(self, query, k=4, source_filter=None):
        """Retrieves relevant documents for a query, optionally filtered by source."""
        try:
            if not self.vector_store_manager.db:
                print("DEBUG: Vector DB not loaded, attempting to load...")
                self.vector_store_manager.load_vector_db()
             
            retriever = self.vector_store_manager.as_retriever()
            if not retriever:
                print("DEBUG: No retriever available (database might be empty)")
                return []
            
            # Use current document as filter if not specified
            if source_filter is None and self.current_document:
                source_filter = self.current_document
                print(f"DEBUG: Auto-filtering by current document: '{source_filter}'")
            
            print(f"DEBUG: Invoking retriever with query: {query[:50]}...")
            docs = retriever.invoke(query)
            print(f"DEBUG: Retriever returned {len(docs)} documents")
            
            # Filter by source if specified
            if source_filter:
                original_count = len(docs)
                docs = [doc for doc in docs if doc.metadata.get("source") == source_filter]
                print(f"DEBUG: Filtered to {len(docs)}/{original_count} documents from '{source_filter}'")
            
            return docs
        except FileNotFoundError as e:
            print(f"DEBUG: Vector database not found: {e}")
            return []
        except Exception as e:
            print(f"DEBUG: Error during retrieval: {e}")
            raise

