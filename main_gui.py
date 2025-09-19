import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QTextEdit, QFileDialog, QProgressBar,
                            QGroupBox, QListWidget, QSplitter, QMessageBox, QComboBox,
                            QTextBrowser, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QTextCursor
import requests
import re
from datetime import datetime
from html_report_generator import ResearchPaperSummarizer
class SummarizerThread(QThread):
    """Thread for running the summarization process"""
    progress_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, summarizer, pdf_path=None, process_all=False):
        super().__init__()
        self.summarizer = summarizer
        self.pdf_path = pdf_path
        self.process_all = process_all
    
    def run(self):
        try:
            if self.process_all:
                self.progress_signal.emit("Processing all PDFs in directory...")
                results = self.summarizer.process_all_papers()
                self.result_signal.emit({"type": "batch", "results": results})
            elif self.pdf_path:
                self.progress_signal.emit(f"Processing: {self.pdf_path.name}")
                result = self.summarizer.summarize_paper(self.pdf_path)
                if "error" in result:
                    self.error_signal.emit(result["error"])
                else:
                    html_path = self.summarizer.generate_html_report(result)
                    self.result_signal.emit({
                        "type": "single", 
                        "result": result,
                        "html_path": html_path
                    })
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(f"Error in summarization: {str(e)}")

class HTMLTextBrowser(QTextBrowser):
    """Enhanced text browser with better HTML support"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        
    def setStyledHtml(self, html_content):
        """Set HTML content with basic styling"""
        # Basic CSS for better rendering
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    background: white;
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    margin: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .summary-section {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #3498db;
                    margin-bottom: 20px;
                }}
                .summary-section h2 {{
                    color: #2c3e50;
                    margin-top: 0;
                }}
                .metadata-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .metadata-item {{
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .footer {{
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-top: 30px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                {html_content}
            </div>
        </body>
        </html>
        """
        self.setHtml(styled_html)

class ResearchPaperSummarizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.summarizer = None
        self.current_html_content = ""
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Research Paper Summarizer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # LM Studio host input
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("LM Studio Host:"))
        self.host_input = QComboBox()
        self.host_input.addItems(["http://localhost:1234", "http://localhost:8080", "http://127.0.0.1:1234"])
        self.host_input.setEditable(True)
        host_layout.addWidget(self.host_input)
        settings_layout.addLayout(host_layout)
        
        # PDF directory selection
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("No directory selected")
        self.dir_label.setWordWrap(True)
        dir_button = QPushButton("Select PDF Directory")
        dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(dir_button)
        settings_layout.addLayout(dir_layout)
        settings_layout.addWidget(self.dir_label)
        
        # Connection test
        test_button = QPushButton("Test LM Studio Connection")
        test_button.clicked.connect(self.test_connection)
        settings_layout.addWidget(test_button)
        
        left_layout.addWidget(settings_group)
        
        # PDF list group
        pdf_group = QGroupBox("Available PDFs")
        pdf_layout = QVBoxLayout(pdf_group)
        self.pdf_list = QListWidget()
        self.pdf_list.itemDoubleClicked.connect(self.on_pdf_selected)
        pdf_layout.addWidget(self.pdf_list)
        left_layout.addWidget(pdf_group)
        
        # Actions group
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.summarize_button = QPushButton("Summarize Selected PDF")
        self.summarize_button.clicked.connect(self.summarize_selected)
        self.summarize_button.setEnabled(False)
        
        self.summarize_all_button = QPushButton("Summarize All PDFs")
        self.summarize_all_button.clicked.connect(self.summarize_all)
        self.summarize_all_button.setEnabled(False)
        
        actions_layout.addWidget(self.summarize_button)
        actions_layout.addWidget(self.summarize_all_button)
        left_layout.addWidget(actions_group)
        
        # Progress group
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        left_layout.addWidget(progress_group)
        
        left_layout.addStretch()
        
        # Right panel for HTML view
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # HTML browser
        right_layout.addWidget(QLabel("Summary Output:"))
        self.html_browser = HTMLTextBrowser()
        self.html_browser.setHtml("""
            <div class="header">
                <h1>Research Paper Summarizer</h1>
                <p>AI-powered research paper summarization tool</p>
            </div>
            <div class="summary-section">
                <h2>Welcome</h2>
                <p>Select a PDF directory and connect to LM Studio to begin.</p>
                <p><strong>Features:</strong></p>
                <ul>
                    <li>AI-powered research paper summaries</li>
                    <li>Beautiful HTML output rendering</li>
                    <li>Batch processing support</li>
                    <li>Real-time progress tracking</li>
                </ul>
            </div>
        """)
        
        right_layout.addWidget(self.html_browser)
        
        # Add panels to main layout with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 1100])
        main_layout.addWidget(splitter)
        
        # Set style
        self.apply_styles()
        
    def apply_styles(self):
        """Apply modern styling to the GUI"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
            QTextBrowser {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
    def select_directory(self):
        """Select PDF directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select PDF Directory")
        if directory:
            self.dir_label.setText(directory)
            self.pdf_directory = directory
            self.load_pdf_list()
            
    def load_pdf_list(self):
        """Load PDF files into the list"""
        self.pdf_list.clear()
        try:
            pdf_files = list(Path(self.pdf_directory).glob("*.pdf"))
            for pdf_file in pdf_files:
                self.pdf_list.addItem(pdf_file.name)
            
            has_pdfs = len(pdf_files) > 0
            self.summarize_button.setEnabled(has_pdfs)
            self.summarize_all_button.setEnabled(has_pdfs)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load PDF files: {str(e)}")
            
    def test_connection(self):
        """Test connection to LM Studio"""
        host = self.host_input.currentText()
        self.status_label.setText("Testing connection...")
        
        try:
            response = requests.get(f"{host}/v1/models", timeout=10)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Connected to LM Studio successfully!")
                self.status_label.setText("Connected to LM Studio")
                self.initialize_summarizer()
            else:
                QMessageBox.warning(self, "Error", f"LM Studio responded with error: {response.status_code}")
                self.status_label.setText("Connection failed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot connect to LM Studio: {str(e)}")
            self.status_label.setText("Connection failed")
            
    def initialize_summarizer(self):
        """Initialize the summarizer with current settings"""
        # Import your summarizer class here
        try:
            # This is where you'd import your actual summarizer class
            # For now, we'll create a mock one
            self.summarizer = ResearchPaperSummarizer(
                pdf_directory=self.pdf_directory,
                host=self.host_input.currentText()
            )
            self.status_label.setText("Summarizer initialized")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not initialize summarizer: {str(e)}")
            
    def summarize_selected(self):
        """Summarize the selected PDF"""
        selected_items = self.pdf_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
            return
            
        if not self.summarizer:
            self.initialize_summarizer()
            
        pdf_name = selected_items[0].text()
        pdf_path = Path(self.pdf_directory) / pdf_name
        
        self.start_summarization(pdf_path)
        
    def summarize_all(self):
        """Summarize all PDFs"""
        if not self.summarizer:
            self.initialize_summarizer()
            
        self.start_summarization(process_all=True)
        
    def start_summarization(self, pdf_path=None, process_all=False):
        """Start the summarization process in a thread"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Processing...")
        self.set_buttons_enabled(False)
        
        # Show processing message
        self.show_processing_message(pdf_path.name if pdf_path else "all PDFs")
        
        self.thread = SummarizerThread(self.summarizer, pdf_path, process_all)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.result_signal.connect(self.handle_result)
        self.thread.error_signal.connect(self.handle_error)
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.start()
        
    def show_processing_message(self, filename):
        """Show processing message in HTML browser"""
        processing_html = f"""
        <div class="header">
            <h1>Processing Research Paper</h1>
            <p>File: {filename}</p>
        </div>
        <div class="summary-section">
            <h2>Status</h2>
            <p>⏳ Processing paper... Please wait.</p>
            <p>This may take a few minutes depending on the paper size.</p>
        </div>
        """
        self.html_browser.setStyledHtml(processing_html)
        
    def update_progress(self, message):
        """Update progress status"""
        self.status_label.setText(message)
        
    def handle_result(self, result):
        """Handle successful result"""
        try:
            if result["type"] == "single":
                # Load the generated HTML file
                html_path = result["html_path"]
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                self.html_browser.setStyledHtml(html_content)
                self.current_html_content = html_content
                
            elif result["type"] == "batch":
                # Show batch completion message
                completion_html = f"""
                <div class="header">
                    <h1>Batch Processing Complete</h1>
                    <p>Processed {len(result['results'])} PDF files</p>
                </div>
                <div class="summary-section">
                    <h2>Results</h2>
                    <p>✅ All PDFs have been processed successfully.</p>
                    <p>Check the 'summaries' directory for individual HTML files.</p>
                </div>
                """
                self.html_browser.setStyledHtml(completion_html)
                
        except Exception as e:
            self.handle_error(f"Error displaying result: {str(e)}")
            
    def handle_error(self, error_message):
        """Handle errors"""
        QMessageBox.critical(self, "Error", error_message)
        # Show error in HTML browser too
        error_html = f"""
        <div class="header" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
            <h1>Error</h1>
            <p>Processing failed</p>
        </div>
        <div class="summary-section">
            <h2>Error Details</h2>
            <p style="color: #c0392b;">❌ {error_message}</p>
            <p>Please check your settings and try again.</p>
        </div>
        """
        self.html_browser.setStyledHtml(error_html)
        
    def on_finished(self):
        """Clean up after thread finishes"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        self.set_buttons_enabled(True)
        
    def set_buttons_enabled(self, enabled):
        """Enable/disable buttons"""
        self.summarize_button.setEnabled(enabled and self.pdf_list.count() > 0)
        self.summarize_all_button.setEnabled(enabled and self.pdf_list.count() > 0)
        
    def on_pdf_selected(self, item):
        """Handle PDF selection"""
        self.summarize_selected()
        
    def closeEvent(self, event):
        """Handle application close"""
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        event.accept()

# Mock summarizer for demonstration (replace with your actual class)
class MockSummarizer:
    def __init__(self, pdf_directory, host):
        self.pdf_directory = pdf_directory
        self.host = host
        self.output_dir = Path("./summaries")
        self.output_dir.mkdir(exist_ok=True)
    
    def process_all_papers(self):
        return [{"pdf": "test.pdf", "html_path": Path("test.html"), "metadata": {"title": "Test"}}]
    
    def summarize_paper(self, pdf_path):
        return {
            "metadata": {
                "filename": pdf_path.name,
                "title": "Sample Research Paper",
                "author": "John Doe",
                "pages": 10,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "summary": "### Research Objectives\nSample objectives\n### Methodology\nSample methods",
            "raw_text": "Sample text"
        }
    
    def generate_html_report(self, result):
        html_path = self.output_dir / f"summary_{result['metadata']['filename'].replace('.pdf', '')}.html"
        # Create sample HTML content
        sample_html = """
        <div class="header">
            <h1>Research Paper Summary</h1>
            <p>AI-generated comprehensive analysis</p>
        </div>
        <div class="summary-section">
            <h2>Research Objectives</h2>
            <p>Sample research objectives content goes here.</p>
        </div>
        <div class="summary-section">
            <h2>Methodology</h2>
            <p>Sample methodology content goes here.</p>
        </div>
        """
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(sample_html)
        return html_path

# Main application
def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = ResearchPaperSummarizerGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()