"""
question_generator.py
LLM-powered question generation from documents using Groq API
"""

import os
from typing import List, Dict

try:
    from groq import Groq
except ImportError:
    Groq = None


class QuestionGenerator:
    """Generate questions from document text using Groq (Llama 3.3)"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the question generator
        
        Args:
            api_key: Groq API key (if None, reads from environment)
        """
        if Groq is None:
            raise ImportError("Groq library not found. Install: pip install groq")
        
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError("Groq API key not found. Set GROQ_API_KEY environment variable.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def create_prompt(self, document_text: str, chunk_num: int = None, total_chunks: int = None) -> str:
        """
        Create the prompt for question generation
        
        Args:
            document_text: The document or chunk text
            chunk_num: Current chunk number (if chunked)
            total_chunks: Total number of chunks (if chunked)
        """
        chunk_context = ""
        if chunk_num is not None and total_chunks is not None:
            chunk_context = f"\n(Note: This is chunk {chunk_num} of {total_chunks} from a larger document)"
        
        prompt = f"""You are an expert educator creating study questions from academic or educational content.

Given the following document{chunk_context}, generate high-quality questions that help students understand and test their comprehension.

REQUIREMENTS:
1. Generate 5-10 factual questions (who, what, when, where, which)
   - These should test recall of specific facts from the document
   - Prefer questions with one-word or short answers
   
2. Generate 3-5 conceptual questions (why, how, explain)
   - These should test deeper understanding
   - Focus on concepts, relationships, and reasoning

3. All questions must:
   - Be directly answerable from the document content
   - Be grammatically correct and clear
   - Not be vague or ambiguous
   - Not repeat or be too similar to each other
   - Cover different sections/topics in the document

4. Format your response EXACTLY as follows:
FACTUAL QUESTIONS:
1. [Question]
2. [Question]
...

CONCEPTUAL QUESTIONS:
1. [Question]
2. [Question]
...

DOCUMENT:
{document_text}

Now generate the questions following the format above:"""
        
        return prompt
    
    def parse_response(self, response_text: str) -> Dict[str, List[str]]:
        """
        Parse LLM response into structured format
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Dictionary with 'factual' and 'conceptual' question lists
        """
        questions = {
            'factual': [],
            'conceptual': []
        }
        
        # Split by sections
        sections = response_text.split('CONCEPTUAL QUESTIONS:')
        
        if len(sections) == 2:
            factual_section = sections[0]
            conceptual_section = sections[1]
        else:
            factual_section = response_text
            conceptual_section = ""
        
        # Extract factual questions
        factual_part = factual_section.split('FACTUAL QUESTIONS:')[-1]
        factual_lines = factual_part.strip().split('\n')
        
        for line in factual_lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                question = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                if question and len(question) > 5:
                    questions['factual'].append(question)
        
        # Extract conceptual questions
        conceptual_lines = conceptual_section.strip().split('\n')
        
        for line in conceptual_lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                question = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                if question and len(question) > 5:
                    questions['conceptual'].append(question)
        
        return questions
    
    def generate_from_text(self, document_text: str, chunk_num: int = None, total_chunks: int = None) -> Dict[str, List[str]]:
        """
        Generate questions from document text
        
        Args:
            document_text: The document or chunk text
            chunk_num: Current chunk number (if chunked)
            total_chunks: Total number of chunks (if chunked)
            
        Returns:
            Dictionary with factual and conceptual questions
        """
        # Silent processing
        
        prompt = self.create_prompt(document_text, chunk_num, total_chunks)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educator who creates clear, relevant study questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            questions = self.parse_response(response_text)
            
            # Silent processing
            
            return questions
        
        except Exception as e:
            raise Exception(f"Error generating questions: {str(e)}")
    
    def generate_from_chunks(self, chunks: List[str]) -> Dict[str, List[str]]:
        """
        Generate questions from multiple chunks and combine them
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Combined dictionary of questions
        """
        all_questions = {
            'factual': [],
            'conceptual': []
        }
        
        for i, chunk in enumerate(chunks, 1):
            # Silent processing
            questions = self.generate_from_text(chunk, i, len(chunks))
            
            all_questions['factual'].extend(questions['factual'])
            all_questions['conceptual'].extend(questions['conceptual'])
        
        # Remove duplicates while preserving order
        all_questions['factual'] = self._remove_duplicates(all_questions['factual'])
        all_questions['conceptual'] = self._remove_duplicates(all_questions['conceptual'])
        
        # Limit to requirements (7 factual, 3 conceptual)
        all_questions['factual'] = all_questions['factual'][:7]
        all_questions['conceptual'] = all_questions['conceptual'][:3]
        
        return all_questions
    
    def _remove_duplicates(self, questions: List[str]) -> List[str]:
        """Remove duplicate or very similar questions"""
        seen = set()
        unique = []
        
        for q in questions:
            normalized = q.lower().strip().rstrip('?')
            if normalized not in seen:
                seen.add(normalized)
                unique.append(q)
        
        return unique