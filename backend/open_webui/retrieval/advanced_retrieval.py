import logging
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter
from sentence_transformers import CrossEncoder
import numpy as np

from open_webui.config import (
    RAG_EMBEDDING_QUERY_PREFIX,
    RAG_EMBEDDING_CONTENT_PREFIX,
)
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["RAG"])


class FileSource(Enum):
    """Enum to identify the source of files"""
    KNOWLEDGE_BASE = "knowledge_base"
    CHAT_UPLOAD = "chat_upload"
    DIRECT_UPLOAD = "direct_upload"


class ProcessingMode(Enum):
    """Processing modes for different file sources"""
    FULL_CONTEXT = "full_context"  # Direct chat uploads - full content
    CHUNKED_VECTORIZED = "chunked_vectorized"  # Knowledge base - chunked and vectorized
    HYBRID = "hybrid"  # Combination of both approaches


class AdvancedRetrieval:
    """Advanced retrieval system with context-aware processing"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        text_splitter_type: str = "recursive",
        enable_semantic_chunking: bool = False,
        enable_query_expansion: bool = True,
        enable_document_reranking: bool = True,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter_type = text_splitter_type
        self.enable_semantic_chunking = enable_semantic_chunking
        self.enable_query_expansion = enable_query_expansion
        self.enable_document_reranking = enable_document_reranking
        
        # Initialize text splitters
        self._init_text_splitters()
        
    def _init_text_splitters(self):
        """Initialize different text splitters"""
        if self.text_splitter_type == "recursive":
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
                keep_separator=True,
            )
        elif self.text_splitter_type == "token":
            self.text_splitter = TokenTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        else:
            # Default to recursive
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
    
    def determine_processing_mode(self, file_metadata: Dict[str, Any]) -> ProcessingMode:
        """Determine the processing mode based on file metadata"""
        source = file_metadata.get("source", FileSource.DIRECT_UPLOAD)
        
        # Files from knowledge base should be chunked and vectorized
        if source == FileSource.KNOWLEDGE_BASE:
            return ProcessingMode.CHUNKED_VECTORIZED
        
        # Files uploaded directly in chat should use full context
        elif source == FileSource.CHAT_UPLOAD:
            return ProcessingMode.FULL_CONTEXT
        
        # Direct uploads (drag & drop) can be configured
        else:
            # Check if file size suggests full context or chunking
            file_size = file_metadata.get("size", 0)
            # If file is small (< 50KB), use full context
            if file_size < 50 * 1024:
                return ProcessingMode.FULL_CONTEXT
            else:
                return ProcessingMode.CHUNKED_VECTORIZED
    
    def process_documents(
        self,
        documents: List[Document],
        file_metadata: Dict[str, Any],
        processing_mode: Optional[ProcessingMode] = None,
    ) -> List[Document]:
        """Process documents based on the determined processing mode"""
        
        if processing_mode is None:
            processing_mode = self.determine_processing_mode(file_metadata)
        
        log.info(f"Processing documents with mode: {processing_mode.value}")
        
        if processing_mode == ProcessingMode.FULL_CONTEXT:
            return self._process_full_context(documents, file_metadata)
        elif processing_mode == ProcessingMode.CHUNKED_VECTORIZED:
            return self._process_chunked_vectorized(documents, file_metadata)
        else:  # HYBRID
            return self._process_hybrid(documents, file_metadata)
    
    def _process_full_context(
        self, documents: List[Document], file_metadata: Dict[str, Any]
    ) -> List[Document]:
        """Process documents for full context retrieval"""
        # For full context, we keep the documents as-is but add metadata
        for doc in documents:
            doc.metadata.update({
                "processing_mode": ProcessingMode.FULL_CONTEXT.value,
                "source": file_metadata.get("source", FileSource.DIRECT_UPLOAD).value,
                **file_metadata
            })
        return documents
    
    def _process_chunked_vectorized(
        self, documents: List[Document], file_metadata: Dict[str, Any]
    ) -> List[Document]:
        """Process documents for chunked and vectorized retrieval"""
        all_chunks = []
        
        for doc in documents:
            # Apply semantic chunking if enabled
            if self.enable_semantic_chunking:
                chunks = self._semantic_chunk(doc)
            else:
                chunks = self.text_splitter.split_documents([doc])
            
            # Add metadata to each chunk
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "processing_mode": ProcessingMode.CHUNKED_VECTORIZED.value,
                    "source": file_metadata.get("source", FileSource.KNOWLEDGE_BASE).value,
                    **file_metadata
                })
            
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def _process_hybrid(
        self, documents: List[Document], file_metadata: Dict[str, Any]
    ) -> List[Document]:
        """Process documents using a hybrid approach"""
        # For hybrid, we create both full context and chunks
        processed_docs = []
        
        # Add full documents
        full_docs = self._process_full_context(documents.copy(), file_metadata)
        processed_docs.extend(full_docs)
        
        # Add chunks
        chunks = self._process_chunked_vectorized(documents.copy(), file_metadata)
        processed_docs.extend(chunks)
        
        return processed_docs
    
    def _semantic_chunk(self, document: Document) -> List[Document]:
        """Apply semantic chunking to a document"""
        # This is a simplified version - in production, you'd use
        # more sophisticated semantic segmentation
        sentences = document.page_content.split('. ')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            if current_size + sentence_size > self.chunk_size and current_chunk:
                chunk_text = '. '.join(current_chunk) + '.'
                chunks.append(Document(
                    page_content=chunk_text,
                    metadata=document.metadata.copy()
                ))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        # Add the last chunk
        if current_chunk:
            chunk_text = '. '.join(current_chunk) + '.'
            chunks.append(Document(
                page_content=chunk_text,
                metadata=document.metadata.copy()
            ))
        
        return chunks
    
    def expand_query(self, query: str, context: Optional[str] = None) -> List[str]:
        """Expand a single query into multiple related queries"""
        if not self.enable_query_expansion:
            return [query]
        
        expanded_queries = [query]
        
        # Simple query expansion - in production, use LLM or other techniques
        # Add question variations
        if "what" in query.lower():
            expanded_queries.append(query.replace("What", "How"))
            expanded_queries.append(query.replace("What", "Why"))
        
        # Add context-based expansion if available
        if context:
            # Extract key terms from context for expansion
            # This is simplified - use NLP libraries in production
            pass
        
        return list(set(expanded_queries))  # Remove duplicates
    
    def rerank_documents(
        self,
        query: str,
        documents: List[Document],
        reranking_model: Optional[Any] = None,
        top_k: int = 10,
    ) -> List[Tuple[Document, float]]:
        """Rerank documents based on relevance to query"""
        if not self.enable_document_reranking or not documents:
            return [(doc, 1.0) for doc in documents[:top_k]]
        
        if reranking_model:
            # Use provided reranking model
            pairs = [(query, doc.page_content) for doc in documents]
            scores = reranking_model.predict(pairs)
            
            # Sort by score and return top_k
            doc_scores = list(zip(documents, scores))
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            return doc_scores[:top_k]
        else:
            # Simple keyword-based reranking
            query_terms = set(query.lower().split())
            doc_scores = []
            
            for doc in documents:
                content_terms = set(doc.page_content.lower().split())
                overlap = len(query_terms.intersection(content_terms))
                score = overlap / len(query_terms) if query_terms else 0
                doc_scores.append((doc, score))
            
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            return doc_scores[:top_k]
    
    def retrieve_with_context_trigger(
        self,
        query: str,
        files: List[Dict[str, Any]],
        embedding_function: Any,
        vector_db_client: Any,
        k: int = 5,
        reranking_function: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Main retrieval function with context-based triggering
        """
        results = []
        
        for file in files:
            file_metadata = file.get("metadata", {})
            processing_mode = self.determine_processing_mode(file_metadata)
            
            if processing_mode == ProcessingMode.FULL_CONTEXT:
                # For full context files, return the entire content
                if "content" in file:
                    results.append({
                        "document": file["content"],
                        "metadata": {
                            **file_metadata,
                            "processing_mode": ProcessingMode.FULL_CONTEXT.value,
                            "score": 1.0  # Full context always has perfect score
                        },
                        "source": file
                    })
            else:
                # For chunked files, perform vector search
                collection_name = file.get("collection_name")
                if collection_name and vector_db_client.has_collection(collection_name):
                    # Expand query if enabled
                    queries = self.expand_query(query)
                    
                    # Perform vector search for each query
                    all_results = []
                    for q in queries:
                        query_embedding = embedding_function(q, prefix=RAG_EMBEDDING_QUERY_PREFIX)
                        search_results = vector_db_client.search(
                            collection_name=collection_name,
                            vectors=[query_embedding],
                            limit=k * 2,  # Get more results for reranking
                        )
                        
                        # Convert results to documents
                        for idx in range(len(search_results.ids[0])):
                            doc = Document(
                                page_content=search_results.documents[0][idx],
                                metadata=search_results.metadatas[0][idx]
                            )
                            all_results.append(doc)
                    
                    # Remove duplicates
                    unique_docs = {}
                    for doc in all_results:
                        doc_id = doc.metadata.get("id", doc.page_content[:50])
                        if doc_id not in unique_docs:
                            unique_docs[doc_id] = doc
                    
                    # Rerank if enabled
                    if self.enable_document_reranking:
                        reranked = self.rerank_documents(
                            query, 
                            list(unique_docs.values()),
                            reranking_function,
                            k
                        )
                        
                        for doc, score in reranked:
                            results.append({
                                "document": doc.page_content,
                                "metadata": {
                                    **doc.metadata,
                                    "processing_mode": ProcessingMode.CHUNKED_VECTORIZED.value,
                                    "score": score
                                },
                                "source": file
                            })
                    else:
                        # Return top k without reranking
                        for doc in list(unique_docs.values())[:k]:
                            results.append({
                                "document": doc.page_content,
                                "metadata": {
                                    **doc.metadata,
                                    "processing_mode": ProcessingMode.CHUNKED_VECTORIZED.value,
                                    "score": 0.0
                                },
                                "source": file
                            })
        
        return results


# Singleton instance
_advanced_retrieval_instance = None


def get_advanced_retrieval(
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    text_splitter_type: Optional[str] = None,
    enable_semantic_chunking: Optional[bool] = None,
    enable_query_expansion: Optional[bool] = None,
    enable_document_reranking: Optional[bool] = None,
) -> AdvancedRetrieval:
    """Get or create the advanced retrieval instance"""
    global _advanced_retrieval_instance
    
    if _advanced_retrieval_instance is None or any([
        chunk_size is not None,
        chunk_overlap is not None,
        text_splitter_type is not None,
        enable_semantic_chunking is not None,
        enable_query_expansion is not None,
        enable_document_reranking is not None,
    ]):
        # Create new instance with provided parameters
        _advanced_retrieval_instance = AdvancedRetrieval(
            chunk_size=chunk_size or 1000,
            chunk_overlap=chunk_overlap or 200,
            text_splitter_type=text_splitter_type or "recursive",
            enable_semantic_chunking=enable_semantic_chunking or False,
            enable_query_expansion=enable_query_expansion or True,
            enable_document_reranking=enable_document_reranking or True,
        )
    
    return _advanced_retrieval_instance 