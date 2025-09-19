import unittest
from pathlib import Path
from datetime import datetime
import re
from html_report_generator import ResearchPaperSummarizer
class TestResearchPaperSummarizer(unittest.TestCase):
    def setUp(self):
        # Create a mock summarizer instance for testing
        self.summarizer = ResearchPaperSummarizer("./test_pdfs")
        
    def test_format_summary_sections_with_markdown_headers(self):
        """Test parsing of markdown-formatted sections"""
        markdown_summary = """### 1. Research Objectives
The paper addresses the need for industrial control system (ICS) threat intelligence.

### 2. Methodology
The whitepaper employs a descriptive approach.

### 3. Key Findings
- Threat Intelligence Definition
- ICS vs. IT Threat Intelligence

### 4. Conclusions
The main conclusions are important.

### 5. Novelty & Contributions
This whitepaper contributes to the field.

### 6. Limitations & Future Work
The study's limitations include lack of empirical research."""
        
        result = self.summarizer.format_summary_sections(markdown_summary)
        
        # Check that all sections are present
        self.assertIn("Research Objectives", result)
        self.assertIn("Methodology", result)
        self.assertIn("Key Findings", result)
        self.assertIn("Conclusions", result)
        self.assertIn("Novelty & Contributions", result)
        self.assertIn("Limitations & Future Work", result)
        
        # Check that content is included
        self.assertIn("industrial control system", result)
        self.assertIn("descriptive approach", result)
    
    def test_format_summary_sections_with_numbered_headers(self):
        """Test parsing of numbered sections"""
        numbered_summary = """1. RESEARCH OBJECTIVES: The paper addresses the need.
        
2. METHODOLOGY: The whitepaper employs a descriptive approach.
        
3. KEY FINDINGS: Important findings are listed.
        
4. CONCLUSIONS: Main conclusions are presented.
        
5. NOVELTY & CONTRIBUTIONS: Contributions to the field.
        
6. LIMITATIONS & FUTURE WORK: Study limitations."""
        
        result = self.summarizer.format_summary_sections(numbered_summary)
        
        # Check that all sections are present
        self.assertIn("Research Objectives", result)
        self.assertIn("Methodology", result)
        self.assertIn("Key Findings", result)
    
    def test_format_summary_sections_with_real_example(self):
        """Test with the actual LM Studio output format"""
        real_summary = """**Industrial Control Threat Intelligence Whitepaper Summary**

### 1. Research Objectives
The paper addresses the need for industrial control system (ICS) threat intelligence.

### 2. Methodology
The whitepaper employs a descriptive approach.

### 3. Key Findings
- Threat Intelligence Definition
- ICS vs. IT Threat Intelligence

### 4. Conclusions
The main conclusions are important.

### 5. Novelty & Contributions
This whitepaper contributes to the field.

### 6. Limitations & Future Work
The study's limitations include lack of empirical research."""
        
        result = self.summarizer.format_summary_sections(real_summary)
        
        # Should contain all sections
        self.assertIn("Research Objectives", result)
        self.assertIn("Methodology", result)
        self.assertIn("Key Findings", result)
        self.assertIn("industrial control system", result)
    
    def test_html_template_generation(self):
        """Test HTML template generation with mock data"""
        metadata = {
            "filename": "test.pdf",
            "title": "Test Research Paper",
            "author": "John Doe",
            "pages": 10,
            "created": "2024-01-01 12:00:00"
        }
        
        summary = "### 1. Research Objectives\nTest objectives."
        
        html_content = self.summarizer.create_html_template(metadata, summary)
        
        # Check that metadata is included
        self.assertIn("Test Research Paper", html_content)
        self.assertIn("John Doe", html_content)
        self.assertIn("test.pdf", html_content)
        
        # Check that CSS styles are included
        self.assertIn("font-family", html_content)
        self.assertIn("background: linear-gradient", html_content)
        
        # Check that summary content is included
        self.assertIn("Research Objectives", html_content)
    
    def test_empty_summary_handling(self):
        """Test handling of empty or malformed summaries"""
        empty_summary = ""
        result = self.summarizer.format_summary_sections(empty_summary)
        self.assertIn("Complete Analysis", result)
        
        malformed_summary = "Just some random text without sections"
        result = self.summarizer.format_summary_sections(malformed_summary)
        self.assertIn("Complete Analysis", result)
        self.assertIn("random text", result)

# Mock test class for the summarizer
class MockResearchPaperSummarizer:
    def __init__(self):
        self.output_dir = Path("./test_summaries")
    
    def format_summary_sections(self, summary: str) -> str:
        # Use the actual implementation you'll create
        return self._actual_format_summary_sections(summary)
    
    def _actual_format_summary_sections(self, summary: str) -> str:
        """Actual implementation that handles markdown headers"""
        section_patterns = [
            (r"(?i)^#+\s*\d*[\.]?\s*Research Objectives?[:]?\s*", "Research Objectives"),
            (r"(?i)^\d+[\.\)]?\s*Research Objectives?[:]?\s*", "Research Objectives"),
            (r"(?i)^#+\s*\d*[\.]?\s*Methodology[:]?\s*", "Methodology"),
            (r"(?i)^\d+[\.\)]?\s*Methodology[:]?\s*", "Methodology"),
            (r"(?i)^#+\s*\d*[\.]?\s*Key Findings?[:]?\s*", "Key Findings"),
            (r"(?i)^\d+[\.\)]?\s*Key Findings?[:]?\s*", "Key Findings"),
            (r"(?i)^#+\s*\d*[\.]?\s*Conclusions?[:]?\s*", "Conclusions"),
            (r"(i?)^\d+[\.\)]?\s*Conclusions?[:]?\s*", "Conclusions"),
            (r"(?i)^#+\s*\d*[\.]?\s*Novelty\s*[&+]?\s*Contributions?[:]?\s*", "Novelty & Contributions"),
            (r"(?i)^\d+[\.\)]?\s*Novelty\s*[&+]?\s*Contributions?[:]?\s*", "Novelty & Contributions"),
            (r"(?i)^#+\s*\d*[\.]?\s*Limitations?\s*[&+]?\s*Future Work[:]?\s*", "Limitations & Future Work"),
            (r"(?i)^\d+[\.\)]?\s*Limitations?\s*[&+]?\s*Future Work[:]?\s*", "Limitations & Future Work"),
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
    
    def create_html_template(self, metadata: dict, summary: str) -> str:
        """Mock HTML template generation"""
        formatted_sections = self.format_summary_sections(summary)
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Research Summary: {metadata['title']}</title>
    <style>body {{ font-family: Arial; }}</style>
</head>
<body>
    <h1>Research Paper Summary</h1>
    <div class="metadata">
        <p>Title: {metadata['title']}</p>
        <p>Author: {metadata['author']}</p>
    </div>
    <div class="summary">
        {formatted_sections}
    </div>
</body>
</html>"""

# Run the tests
if __name__ == "__main__":
    # Create test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResearchPaperSummarizer)
    result = runner.run(suite)
    
    # Also test with mock data
    print("\n" + "="*50)
    print("TESTING WITH ACTUAL LM STUDIO OUTPUT FORMAT")
    print("="*50)
    
    mock_summarizer = MockResearchPaperSummarizer()
    
    # Test with the exact format from LM Studio
    lm_studio_output = """**Industrial Control Threat Intelligence Whitepaper Summary**

### 1. Research Objectives
The paper addresses the need for industrial control system (ICS) threat intelligence in modern network defense. The main research questions are:

- What is the significance of ICS threat intelligence?
- How does it differ from traditional IT threat intelligence?
- What are the essential components and properties of high-quality threat intelligence?

### 2. Methodology
The whitepaper employs a descriptive approach, outlining the importance of threat intelligence in industrial control systems without conducting empirical research or experiments. It draws on existing knowledge about threat intelligence and its applications.

### 3. Key Findings

- **Threat Intelligence Definition**: Threat intelligence is defined as actionable knowledge that enables defenders to reduce harm through better security decision-making.
- **ICS vs. IT Threat Intelligence**: The paper highlights the unique requirements for ICS threat intelligence, emphasizing the need for context and action tailored to industrial control environments.
- **Properties of High-Quality Threat Intelligence**: Completeness, accuracy, relevance, and timeliness (CART) are identified as essential properties for effective threat intelligence.
- **Three Categories of Threat Intelligence**: Tactical, operational, and strategic threat intelligence categories are introduced, each serving different roles in security operations.

### 4. Conclusions
The main conclusions are:

- ICS owners and operators must seek specialized threat intelligence products to address their unique needs.
- High-quality threat intelligence is crucial for improving detection, response, and prevention capabilities.
- Effective application of threat intelligence can differentiate between mediocre and great cybersecurity programs.

### 5. Novelty & Contributions
This whitepaper contributes to the field by:

- Emphasizing the importance of ICS-specific threat intelligence.
- Outlining essential components and properties of high-quality threat intelligence.
- Providing a framework for understanding different categories of threat intelligence.

### 6. Limitations & Future Work
The study's limitations include:

- Lack of empirical research or experimental validation.
- Limited scope, focusing primarily on the definition and importance of ICS threat intelligence.
Future work could involve conducting case studies or surveys to validate the effectiveness of ICS-specific threat intelligence products and further explore the properties of high-quality threat intelligence."""
    
    result = mock_summarizer.format_summary_sections(lm_studio_output)
    print("Parsed sections from LM Studio output:")
    print(result)
    
    # Test HTML generation
    metadata = {
        "filename": "ics_threat_intelligence.pdf",
        "title": "Industrial Control Threat Intelligence Whitepaper",
        "author": "Security Research Team",
        "pages": 15,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    html_content = mock_summarizer.create_html_template(metadata, lm_studio_output)
    print("\nGenerated HTML preview (first 500 chars):")
    print(html_content[:500] + "...")