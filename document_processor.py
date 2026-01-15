"""
document_processor.py
Handles document extraction, cleaning, and preprocessing for academic papers
"""

import re
from pathlib import Path
from typing import Optional, List

try:
    import pypdf
except ImportError:
    pypdf = None


class DocumentProcessor:
    """Extract and clean text from PDF or TXT files, optimized for academic papers"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.raw_text = ""
        self.cleaned_text = ""
        
    def extract_text(self) -> str:
        """Extract text from PDF or TXT file"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        file_extension = self.file_path.suffix.lower()
        
        if file_extension == '.pdf':
            self.raw_text = self._extract_from_pdf()
        elif file_extension == '.txt':
            self.raw_text = self._extract_from_txt()
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Use .pdf or .txt")
        
        return self.raw_text
    
    def _extract_from_pdf(self) -> str:
        """Extract text from PDF using pypdf"""
        if pypdf is None:
            raise ImportError("pypdf is required for PDF processing. Install: pip install pypdf")
        
        text_content = []
        
        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                # Silent extraction
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text)
            
            return "\n\n".join(text_content)
        
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def _extract_from_txt(self) -> str:
        """Extract text from TXT file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(self.file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _remove_references_section(self, text: str) -> str:
        """Remove references section from academic papers"""
        # Common reference section headers
        ref_patterns = [
            r'\n\s*REFERENCES\s*\n',
            r'\n\s*References\s*\n',
            r'\n\s*BIBLIOGRAPHY\s*\n',
            r'\n\s*Bibliography\s*\n',
            r'\n\s*WORKS CITED\s*\n'
        ]
        
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Keep only text before references
                text = text[:match.start()]
                break
        
        return text
    
    def _remove_common_headers_footers(self, text: str) -> str:
        """Remove common headers, footers, and metadata"""
        lines = text.split('\n')
        cleaned_lines = []
        
        # Patterns to identify headers/footers/metadata
        skip_patterns = [
            r'^Page\s+\d+',
            r'^\d+\s*$',  # Standalone page numbers
            r'^Copyright\s+',
            r'^\d{4}\s+IEEE',
            r'^IEEE\s+',
            r'^Proceedings\s+of',
            r'^\s*\d+\s*\|\s*Page',
            r'^Volume\s+\d+',
            r'^Issue\s+\d+',
            r'^DOI:\s*',
            r'^https?://',
            r'^www\.',
            r'^\[?\d+\]?\s*$',  # Reference numbers
        ]
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Skip lines matching header/footer patterns
            skip_line = False
            for pattern in skip_patterns:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    skip_line = True
                    break
            
            if not skip_line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _remove_author_affiliations(self, text: str) -> str:
        """Remove author names, emails, and affiliations from the beginning"""
        lines = text.split('\n')
        
        # Patterns that indicate author/affiliation information
        author_patterns = [
            r'@',  # Email addresses
            r'\.edu',
            r'\.com',
            r'Department\s+of',
            r'University\s+of',
            r'Institute\s+of',
            r'\d{5}',  # Zip codes
        ]
        
        # Find where main content likely starts (after abstract or introduction)
        content_start_idx = 0
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in ['abstract', 'introduction', 'i. introduction']):
                content_start_idx = i
                break
        
        # If we found content start, remove everything before it that looks like metadata
        if content_start_idx > 0:
            # Look backwards from content start for actual title
            for i in range(content_start_idx - 1, -1, -1):
                line = lines[i].strip()
                # If line is substantial (likely title), keep from here
                if len(line) > 20 and not any(re.search(pattern, line, re.IGNORECASE) for pattern in author_patterns):
                    return '\n'.join(lines[i:])
        
        return text
    
    def _handle_two_column_format(self, text: str) -> str:
        """
        Handle two-column academic paper format
        Merge columns that were split during extraction
        """
        lines = text.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip very short lines that are likely artifacts of column splitting
            if len(line) < 3:
                continue
            
            # If current line ends mid-sentence and next line starts lowercase,
            # it's likely a column break - merge them
            if i < len(lines) - 1:
                next_line = lines[i + 1].strip()
                if (line and not line.endswith(('.', '!', '?', ':')) and 
                    next_line and next_line[0].islower()):
                    # Don't add line yet, will be merged with next
                    continue
            
            cleaned_lines.append(line)
        
        # Join lines back together
        text = '\n'.join(cleaned_lines)
        
        # Fix broken words at column splits
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        return text
    
    def _extract_main_sections(self, text: str) -> str:
        """Extract only main content sections"""
        # Common section headers in academic papers
        main_sections = [
            'abstract',
            'introduction',
            'background',
            'related work',
            'methodology',
            'method',
            'approach',
            'implementation',
            'experiments',
            'results',
            'evaluation',
            'discussion',
            'conclusion',
            'future work'
        ]
        
        lines = text.split('\n')
        in_main_section = False
        content_lines = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line is a main section header
            is_section_header = any(section in line_lower for section in main_sections)
            
            if is_section_header:
                in_main_section = True
                content_lines.append(line)
            elif in_main_section:
                # Stop at references, acknowledgments, or appendix
                if any(keyword in line_lower for keyword in ['references', 'acknowledgment', 'appendix']):
                    break
                content_lines.append(line)
        
        return '\n'.join(content_lines) if content_lines else text
    
    def clean_text(self) -> str:
        """Clean and preprocess extracted text for academic papers"""
        text = self.raw_text
        
        # Step 1: Remove references section
        text = self._remove_references_section(text)
        
        # Step 2: Handle two-column format
        text = self._handle_two_column_format(text)
        
        # Step 3: Remove author affiliations and metadata
        text = self._remove_author_affiliations(text)
        
        # Step 4: Remove headers, footers, page numbers
        text = self._remove_common_headers_footers(text)
        
        # Step 5: Extract main content sections
        text = self._extract_main_sections(text)
        
        # Step 6: General cleaning
        # Remove multiple newlines (keep paragraph structure)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove excessive whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove empty lines at start and end
        text = text.strip()
        
        # Fix common OCR issues
        text = text.replace('ï¿½', '')
        
        # Remove remaining reference citations like [1], [2, 3]
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
        
        self.cleaned_text = text
        return self.cleaned_text
    
    def get_text_stats(self) -> dict:
        """Get statistics about the processed text"""
        text = self.cleaned_text if self.cleaned_text else self.raw_text
        
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        return {
            'characters': len(text),
            'words': len(words),
            'sentences': len(sentences),
            'paragraphs': len(text.split('\n\n'))
        }
    
    def process(self) -> str:
        """Complete processing pipeline"""
        # Silent processing
        
        # Extract
        self.extract_text()
        
        # Clean
        self.cleaned_text = self.clean_text()
        
        # Stats (calculate but don't print)
        stats = self.get_text_stats()
        
        return self.cleaned_text


if __name__ == "__main__":
    # Test the processor
    import sys
    
    if len(sys.argv) > 1:
        processor = DocumentProcessor(sys.argv[1])
        text = processor.process()
        print("\n" + "="*50)
        print("CLEANED TEXT PREVIEW:")
        print("="*50)
        print(text[:500] + "...")
    else:
        print("Usage: python document_processor.py <file_path>")