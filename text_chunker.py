"""
text_chunker.py
Intelligently chunks text to fit within LLM token limits
"""

import re
from typing import List


class TextChunker:
    """Smart text chunking with context preservation"""
    
    def __init__(self, max_tokens: int = 3000, overlap: int = 200):
        """
        Initialize chunker
        
        Args:
            max_tokens: Maximum tokens per chunk (rough estimate: 1 token ≈ 4 chars)
            overlap: Number of tokens to overlap between chunks for context
        """
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.max_chars = max_tokens * 4  # Rough approximation
        self.overlap_chars = overlap * 4
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text) // 4
    
    def chunk_by_paragraphs(self, text: str) -> List[str]:
        """Chunk text by paragraphs while respecting token limits"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_length = len(para)
            
            # If single paragraph exceeds limit, split by sentences
            if para_length > self.max_chars:
                # Save current chunk if any
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # Split long paragraph
                sentence_chunks = self._split_long_paragraph(para)
                chunks.extend(sentence_chunks)
                continue
            
            # Check if adding this paragraph exceeds limit
            if current_length + para_length > self.max_chars and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                # Add overlap from previous chunk
                current_chunk = [current_chunk[-1]] if current_chunk else []
                current_length = len(current_chunk[0]) if current_chunk else 0
            
            current_chunk.append(para)
            current_length += para_length
        
        # Add remaining chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """Split a long paragraph by sentences"""
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.max_chars and current_chunk:
                chunks.append(' '.join(current_chunk))
                # Keep last sentence for overlap
                current_chunk = [current_chunk[-1]] if current_chunk else []
                current_length = len(current_chunk[0]) if current_chunk else 0
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Main chunking method
        
        Args:
            text: Full document text
            
        Returns:
            List of text chunks
        """
        estimated_tokens = self.estimate_tokens(text)
        
        # If text fits within limit, return as single chunk
        if estimated_tokens <= self.max_tokens:
            # Silent processing
            return [text]
        
        # Otherwise, chunk intelligently
        # Silent processing
        chunks = self.chunk_by_paragraphs(text)
        
        return chunks
    
    def get_chunk_info(self, chunks: List[str]) -> dict:
        """Get information about chunks"""
        return {
            'num_chunks': len(chunks),
            'chunk_sizes': [self.estimate_tokens(chunk) for chunk in chunks],
            'total_tokens': sum(self.estimate_tokens(chunk) for chunk in chunks)
        }


if __name__ == "__main__":
    # Test the chunker
    sample_text = """
    This is a sample paragraph. It contains multiple sentences.
    
    This is another paragraph with more content. It goes on and on.
    
    Yet another paragraph here. And more text follows.
    """ * 100  # Repeat to create large text
    
    chunker = TextChunker(max_tokens=500)
    chunks = chunker.chunk_text(sample_text)
    
    print(f"\nCreated {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:3]):  # Show first 3
        print(f"\nChunk {i+1} preview ({len(chunk)} chars):")
        print(chunk[:200] + "...")