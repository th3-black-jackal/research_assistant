import requests
import json
from pathlib import Path
import PyPDF2
import re
from typing import List, Dict
from datetime import datetime


class AdvancedResearchSummarizer:
    def __init__(self, pdf_directory: str, host: str = "http://localhost:1234"):
        self.host = host
        self.pdf_directory = pdf_directory
    
    def extract_structured_text(self, pdf_path: Path) -> Dict:
        """Extract structured content from PDF"""
        text = ""
        metadata = {"title": pdf_path.name, "pages": 0}
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata["pages"] = len(reader.pages)
                
                # Extract title from metadata or first page
                if reader.metadata and reader.metadata.get('/Title'):
                    metadata["title"] = reader.metadata.get('/Title')
                
                # Extract text from first few pages (abstract, intro, conclusion)
                important_pages = [0, 1, 2, -1, -2]  # First 3 and last 2 pages
                for i in set(important_pages):
                    if 0 <= i < len(reader.pages):
                        page_text = reader.pages[i].extract_text()
                        text += f"--- Page {i+1} ---\n{page_text}\n\n"
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")
        
        return {"metadata": metadata, "text": text}
    
    def smart_truncate(self, text: str, max_length: int = 4000) -> str:
        """Smart truncation to preserve important sections"""
        # Look for common academic sections
        sections = {
            'abstract': r'(?i)abstract',
            'introduction': r'(?i)introduction',
            'conclusion': r'(?i)conclusion|discussion',
            'results': r'(?i)results|findings'
        }
        
        # Try to find and preserve key sections
        preserved_text = ""
        for section_name, pattern in sections.items():
            match = re.search(pattern, text)
            if match:
                start = match.start()
                # Get 500 characters around each section
                section_text = text[max(0, start-200):start+500]
                preserved_text += f"\n[{section_name.upper()}]\n{section_text}\n"
        
        if preserved_text:
            return preserved_text[:max_length]
        
        # Fallback: first and last parts
        return text[:max_length//2] + "\n...\n" + text[-max_length//2:]
    
    def generate_summary(self, paper_content: Dict, focus: str = "comprehensive") -> str:
        """Generate summary with different focus options"""
        
        prompts = {
            "comprehensive": f"""Please provide a comprehensive summary of this research paper:

Title: {paper_content['metadata']['title']}

Content:
{paper_content['text'][:5000]}

Structure your summary with:
1. RESEARCH QUESTION: Main problem addressed
2. METHODOLOGY: Approach and methods used
3. KEY FINDINGS: Most important results
4. CONCLUSIONS: Implications and future directions
5. NOVELTY: What makes this research unique""",

            "quick": f"""Provide a brief overview of this paper:

{paper_content['text'][:3000]}

Focus on: Main objective, key method, one most important finding, and overall significance.""",

            "technical": f"""Technical analysis of:

{paper_content['text'][:4000]}

Focus on: Methods used, technical innovations, data analysis approach, and validation methods."""
        }
        
        prompt = prompts.get(focus, prompts["comprehensive"])
        return self.query_llm(prompt)
    
    def query_llm(self, prompt: str) -> str:
        """Query LM Studio with proper error handling"""
        url = f"{self.host}/v1/chat/completions"
        
        payload = {
            "model": "local-model",  # LM Studio handles model selection
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 1500,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"API Error: {response.status_code}"
        except requests.exceptions.Timeout:
            return "Request timeout - try reducing the text length"
        except Exception as e:
            return f"Error: {str(e)}"
        

# Simple usage
def quick_summarize(pdf_path: str):
    """Quick summary function"""
    summarizer = AdvancedResearchSummarizer(".")
    content = summarizer.extract_structured_text(Path(pdf_path))
    summary = summarizer.generate_summary(content, "quick")
    return summary

# Example usage
if __name__ == "__main__":
    # Quick test
    pdf_path = "./research_papers/Industrial-Control-Threat-Intelligence-Whitepaper.pdf"  # Replace with your file
    summary = quick_summarize(pdf_path)
    print(summary)