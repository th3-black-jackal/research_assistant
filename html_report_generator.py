import requests
import json
from pathlib import Path
import PyPDF2
import re
from datetime import datetime
from typing import List, Dict
import time

class ResearchPaperSummarizer:
    def __init__(self, pdf_directory: str, host: str = "http://localhost:1234"):
        self.host = host
        self.pdf_directory = pdf_directory
        self.output_dir = Path("./summaries")
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: Path, max_pages: int = 15) -> str:
        """Extract text from PDF with page limit"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for i, page in enumerate(reader.pages[:max_pages]):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"--- Page {i+1} ---\n{page_text}\n\n"
        except Exception as e:
            print(f"Error reading {pdf_path.name}: {e}")
        return text
    
    def get_pdf_metadata(self, pdf_path: Path) -> Dict:
        """Extract metadata from PDF"""
        metadata = {
            "filename": pdf_path.name,
            "title": pdf_path.stem,
            "author": "Unknown",
            "pages": 0,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata["pages"] = len(reader.pages)
                
                if reader.metadata:
                    if reader.metadata.get('/Title'):
                        metadata["title"] = reader.metadata.get('/Title')
                    if reader.metadata.get('/Author'):
                        metadata["author"] = reader.metadata.get('/Author')
        except:
            pass
        
        return metadata
    
    def query_lm_studio(self, prompt: str, max_tokens: int = 1500) -> str:
        """Send query to LM Studio"""
        url = f"{self.host}/v1/chat/completions"
        
        payload = {
            "model": "local-model",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert academic research assistant. Provide structured, concise summaries with clear sections. Use academic language but avoid unnecessary jargon."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=180)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error: HTTP {response.status_code}"
        except Exception as e:
            return f"Request failed: {e}"
    
    def generate_summary_prompt(self, paper_text: str, metadata: Dict) -> str:
        """Create comprehensive summary prompt"""
        return f"""Please provide a detailed academic summary of this research paper:

TITLE: {metadata['title']}
AUTHOR: {metadata['author']}

PAPER CONTENT:
{paper_text[:6000]}

Structure your summary with these clear sections:

1. RESEARCH OBJECTIVES: What problem does this paper address? What are the main research questions?
2. METHODOLOGY: What methods, approaches, and techniques were used? Describe the experimental setup.
3. KEY FINDINGS: What are the most important results and discoveries? Include quantitative results if available.
4. CONCLUSIONS: What are the main conclusions and implications? How do the findings contribute to the field?
5. NOVELTY & CONTRIBUTIONS: What is innovative about this research? What new knowledge does it provide?
6. LIMITATIONS & FUTURE WORK: What are the study's limitations and what future research directions are suggested?

Please be comprehensive yet concise. Use academic language and focus on the most significant aspects."""

    def create_html_template(self, metadata: Dict, summary: str, paper_text: str = "") -> str:
        """Generate beautiful HTML output"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Summary: {metadata['title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .metadata {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .metadata-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .metadata-item h3 {{
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .summary {{
            padding: 40px;
        }}
        
        .summary-section {{
            margin-bottom: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }}
        
        .summary-section h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.4em;
            display: flex;
            align-items: center;
        }}
        
        .summary-section h2::before {{
            content: "📌";
            margin-right: 10px;
            font-size: 1.2em;
        }}
        
        .summary-content {{
            font-size: 1.1em;
            color: #495057;
            line-height: 1.8;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        .badge {{
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .summary {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Research Paper Summary</h1>
            <p>AI-generated comprehensive analysis</p>
        </div>
        
        <div class="metadata">
            <h2>Document Information</h2>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <h3>Title</h3>
                    <p>{metadata['title']}</p>
                </div>
                <div class="metadata-item">
                    <h3>Author</h3>
                    <p>{metadata['author']}</p>
                </div>
                <div class="metadata-item">
                    <h3>Filename</h3>
                    <p>{metadata['filename']}</p>
                </div>
                <div class="metadata-item">
                    <h3>Pages Analyzed</h3>
                    <p>{metadata['pages']}</p>
                </div>
                <div class="metadata-item">
                    <h3>Generated On</h3>
                    <p>{metadata['created']}</p>
                </div>
                <div class="metadata-item">
                    <h3>Model</h3>
                    <p>selene-1-mini-llama-3.1-8b <span class="badge">AI</span></p>
                </div>
            </div>
        </div>
        
        <div class="summary">
            <h2 style="color: #2c3e50; margin-bottom: 30px; text-align: center;">
                📋 Executive Summary
            </h2>
            
            {self.format_summary_sections(summary)}
        </div>
        
        <div class="footer">
            <p>Generated by Research Summarization Agent | {datetime.now().year}</p>
            <p>Powered by LM Studio & selene-1-mini-llama-3.1-8b</p>
        </div>
    </div>
</body>
</html>"""

    def format_summary_sections(self, summary: str) -> str:
        """Parse summary with markdown headers (###) and numbered sections"""
        section_patterns = [
            # Markdown headers (### 1. Research Objectives)
            (r"(?i)^#+\s*\d*[\.]?\s*Research Objectives?[:]?\s*", "Research Objectives"),
            (r"(?i)^#+\s*\d*[\.]?\s*Methodology[:]?\s*", "Methodology"),
            (r"(?i)^#+\s*\d*[\.]?\s*Key Findings?[:]?\s*", "Key Findings"),
            (r"(?i)^#+\s*\d*[\.]?\s*Conclusions?[:]?\s*", "Conclusions"),
            (r"(?i)^#+\s*\d*[\.]?\s*Novelty\s*[&+]?\s*Contributions?[:]?\s*", "Novelty & Contributions"),
            (r"(?i)^#+\s*\d*[\.]?\s*Limitations?\s*[&+]?\s*Future Work[:]?\s*", "Limitations & Future Work"),
        
            # Numbered sections (1. Research Objectives:)
            (r"(?i)^\d+[\.\)]?\s*Research Objectives?[:]?\s*", "Research Objectives"),
            (r"(?i)^\d+[\.\)]?\s*Methodology[:]?\s*", "Methodology"),
            (r"(?i)^\d+[\.\)]?\s*Key Findings?[:]?\s*", "Key Findings"),
            (r"(?i)^\d+[\.\)]?\s*Conclusions?[:]?\s*", "Conclusions"),
            (r"(?i)^\d+[\.\)]?\s*Novelty\s*[&+]?\s*Contributions?[:]?\s*", "Novelty & Contributions"),
            (r"(?i)^\d+[\.\)]?\s*Limitations?\s*[&+]?\s*Future Work[:]?\s*", "Limitations & Future Work"),
        
            # Simple headers (Research Objectives:)
            (r"(?i)^Research Objectives?[:]?\s*", "Research Objectives"),
            (r"(?i)^Methodology[:]?\s*", "Methodology"),
            (r"(?i)^Key Findings?[:]?\s*", "Key Findings"),
            (r"(?i)^Conclusions?[:]?\s*", "Conclusions"),
            (r"(?i)^Novelty\s*[&+]?\s*Contributions?[:]?\s*", "Novelty & Contributions"),
            (r"(?i)^Limitations?\s*[&+]?\s*Future Work[:]?\s*", "Limitations & Future Work"),
            ]

        sections = {
            "Research Objectives": "",
            "Methodology": "",
            "Key Findings": "",
            "Conclusions": "",
            "Novelty & Contributions": "",
            "Limitations & Future Work": ""
            }
    
        current_section = None
        lines = summary.split('\n')
    
        for line in lines:
            line = line.strip()
            if not line:
                continue
        
            # Check if this line matches any section pattern
            section_found = False
        for pattern, section_name in section_patterns:
            if re.search(pattern, line):
                current_section = section_name
                # Remove the matched pattern from the line
                remaining_content = re.sub(pattern, '', line).strip()
                if remaining_content:
                    sections[current_section] = remaining_content
                section_found = True
                break
        
        # If no section header found, add to current section
        if not section_found and current_section:
            if sections[current_section]:
                sections[current_section] += " " + line
            else:
                sections[current_section] = line
    
            # Generate HTML for each section that has content
        html_sections = ""
        for section_title, content in sections.items():
            if content.strip():
                        html_sections += f"""
                        <div class="summary-section">
                            <h2>{section_title}</h2>
                            <div class="summary-content">
                            {content.strip()}
                            </div>
                        </div>
                        """
    
        # Fallback if no sections were found
        if not html_sections.strip():
            html_sections = f"""
            <div class="summary-section">
                <h2>Complete Analysis</h2>
                <div class="summary-content">
                {summary}
            </div>
        </div>
        """
    
        return html_sections
    
    def summarize_paper(self, pdf_path: Path) -> Dict:
        """Process a single paper and return summary with metadata"""
        print(f"📄 Processing: {pdf_path.name}")
        
        metadata = self.get_pdf_metadata(pdf_path)
        paper_text = self.extract_text_from_pdf(pdf_path)
        
        if not paper_text.strip():
            return {"error": f"Could not extract text from {pdf_path.name}"}
        
        prompt = self.generate_summary_prompt(paper_text, metadata)
        summary = self.query_lm_studio(prompt)
        
        return {
            "metadata": metadata,
            "summary": summary,
            "raw_text": paper_text[:1000]  # First 1000 chars for reference
        }
    
    def generate_html_report(self, result: Dict, output_path: Path = None):
        """Generate and save HTML report"""
        if not output_path:
            output_path = self.output_dir / f"summary_{result['metadata']['filename'].replace('.pdf', '')}.html"
        
        html_content = self.create_html_template(result['metadata'], result['summary'])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report saved: {output_path}")
        return output_path
    
    def process_all_papers(self):
        """Process all PDFs in the directory"""
        pdf_files = list(Path(self.pdf_directory).glob("*.pdf"))
        results = []
        
        if not pdf_files:
            print("❌ No PDF files found in directory")
            return results
        
        print(f"🔍 Found {len(pdf_files)} PDF files")
        
        for pdf_path in pdf_files:
            result = self.summarize_paper(pdf_path)
            if "error" not in result:
                html_path = self.generate_html_report(result)
                results.append({
                    "pdf": pdf_path.name,
                    "html_path": html_path,
                    "metadata": result["metadata"]
                })
            time.sleep(2)  # Be nice to the API
        
        return results

# Main execution function
def main():
    # Initialize summarizer
    summarizer = ResearchPaperSummarizer(
        pdf_directory="./research_papers/",
        host="http://localhost:1234"
    )
    
    # Test connection
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=10)
        if response.status_code == 200:
            print("✅ Connected to LM Studio successfully")
        else:
            print("⚠ LM Studio responded with error")
    except:
        print("❌ Cannot connect to LM Studio. Make sure it's running on http://localhost:1234")
        return
    
    # Process all papers
    results = summarizer.process_all_papers()
    
    # Generate index page if multiple papers
    if len(results) > 1:
        generate_index_page(results, summarizer.output_dir)
    
    print(f"\n🎉 Processing complete! Generated {len(results)} summaries.")

def generate_index_page(results: List[Dict], output_dir: Path):
    """Generate an index page linking to all summaries"""
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Paper Summaries</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
        }}
        
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        
        .paper-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .paper-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #3498db;
            transition: transform 0.2s;
        }}
        
        .paper-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .paper-card h3 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .paper-card a {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        
        .paper-card a:hover {{
            background: #2980b9;
        }}
        
        .stats {{
            text-align: center;
            margin-top: 30px;
            color: #6c757d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Research Paper Summaries</h1>
        <p style="text-align: center; color: #6c757d;">AI-generated summaries using selene-1-mini-llama-3.1-8b</p>
        
        <div class="paper-grid">
"""
    
    for result in results:
        index_html += f"""
            <div class="paper-card">
                <h3>{result['metadata']['title']}</h3>
                <p><strong>Author:</strong> {result['metadata']['author']}</p>
                <p><strong>Pages:</strong> {result['metadata']['pages']}</p>
                <a href="{result['html_path'].name}">View Summary →</a>
            </div>
        """
    
    index_html += f"""
        </div>
        
        <div class="stats">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | {len(results)} papers processed</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_dir / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"✅ Index page created: {output_dir / 'index.html'}")

if __name__ == "__main__":
    main()