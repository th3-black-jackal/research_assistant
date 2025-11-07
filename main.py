#!/usr/bin/env python3
import sys
import os
import json
import tempfile
from pathlib import Path
import re
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QListWidget, QTextEdit, 
                             QTabWidget, QProgressBar, QFileDialog, QMessageBox,
                             QCheckBox, QComboBox, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QSplitter, QFrame,
                             QGroupBox, QScrollArea, QHBoxLayout, QFormLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

from llm_utils import *
from config_manager import ConfigEditorWindow, ConfigManager
from styles import DARK_SCIENTIFIC_THEME



class AnalysisWorker(QThread):
    """Worker thread for processing papers"""
    
    progress_update = pyqtSignal(str, int)
    finished_analysis = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, pdf_files: List[str], analysis_config: Dict[str, bool], model_config: Dict[str, Any]):
        super().__init__()
        self.pdf_files = pdf_files
        self.analysis_config = analysis_config
        self.model_config = model_config
        self.model = None
    
    def run(self):
        try:
            # Initialize GPT4All model
	    
            self.progress_update.emit("Loading AI model...", 10)
            
            model_path = self.model_config['model_path'] if self.model_config['model_path'] else None
            self.model = GPT4All(
                model_name=self.model_config['name'],
                model_path=model_path,
                allow_download=True,
                device='gpu'
            )
            
            results = {
                'papers': [],
                'summaries': [],
                'github_links': [],
                'gaps': [],
                'clusters': []
            }
            
            # Process each PDF
            total_files = len(self.pdf_files)
            for i, pdf_file in enumerate(self.pdf_files):
                self.progress_update.emit(f"Processing {os.path.basename(pdf_file)}...", 
                                        int(20 + (i / total_files) * 30))
                
                paper_data = self._process_single_paper(pdf_file)
                results['papers'].append(paper_data)
            
            # Generate summaries
            if self.analysis_config.get('summaries', True):
                self.progress_update.emit("Generating summaries...", 60)
                results['summaries'] = self._generate_summaries(results['papers'])
            
            # Extract GitHub links
            if self.analysis_config.get('github_extraction', True):
                self.progress_update.emit("Extracting GitHub links...", 70)
                results['github_links'] = self._extract_all_github_links(results['papers'])
            
            # Cluster topics and analyze gaps
            if self.analysis_config.get('gap_analysis', True):
                self.progress_update.emit("Analyzing topics and gaps...", 80)
                cluster_results = self._analyze_topics_and_gaps(results['papers'])
                results.update(cluster_results)
            
            self.progress_update.emit("Analysis complete!", 100)
            self.finished_analysis.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def _process_single_paper(self, pdf_path: str) -> Dict[str, Any]:
        """Process a single PDF file"""
        content = PDFProcessor.extract_text_from_pdf(pdf_path)
        
        # Extract basic metadata
        title = os.path.basename(pdf_path).replace('.pdf', '').replace('_', ' ')
        
        # Try to extract year from content
        year_match = re.search(r'(19|20)\d{2}', content)
        year = year_match.group() if year_match else "Unknown"
        
        return {
            'file_path': pdf_path,
            'title': title,
            'content': content,
            'year': year,
            'github_links': PDFProcessor.extract_github_links(content)
        }
    
    def _generate_summaries(self, papers: List[Dict]) -> List[Dict]:
        """Generate summaries for all papers"""
        summary_gen = SummaryGenerator(self.model, self.model_config['max_tokens'])
        summaries = []
        
        for paper in papers:
            summary = summary_gen.generate_summary(paper['content'], paper['title'])
            summaries.append({
                'paper_title': paper['title'],
                'summary': summary,
                'year': paper['year'],
                'has_github': len(paper['github_links']) > 0
            })
        
        return summaries
    
    def _extract_all_github_links(self, papers: List[Dict]) -> List[Dict]:
        """Extract all GitHub links from papers"""
        all_links = []
        for paper in papers:
            for link in paper['github_links']:
                all_links.append({
                    'paper': paper['title'],
                    'url': link['url'],
                    'type': link['type']
                })
        return all_links
    
    def _analyze_topics_and_gaps(self, papers: List[Dict]) -> Dict[str, Any]:
        """Cluster papers and analyze gaps"""
        # Generate embeddings
        embedding_gen = EmbeddingGenerator(self.model)
        embeddings = []
        valid_papers = []
        
        for paper in papers:
            if paper['content'].strip():
                embedding = embedding_gen.generate_embedding(paper['content'])
                embeddings.append(embedding)
                valid_papers.append(paper)
        
        # Cluster papers
        clusterer = TopicClusterer()
        clusters = clusterer.cluster_papers(embeddings)
        
        # Analyze gaps
        gap_analyzer = GapAnalyzer(self.model)
        gaps = gap_analyzer.analyze_gaps(valid_papers, clusters)
        
        return {
            'clusters': clusters,
            'gaps': gaps,
            'clustered_papers': valid_papers
        }

class ResearchAssistantApp(QMainWindow):
    """Main application window with dark scientific theme"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.pdf_files = []
        self.analysis_results = None
        
        # Load configurations
        self.model_config = self.config_manager.get_model_config()
        analysis_defaults = self.config_manager.get_analysis_config()
        self.analysis_config = {
            'summaries': analysis_defaults['default_summaries'],
            'gap_analysis': analysis_defaults['default_gap_analysis'],
            'github_extraction': analysis_defaults['default_github_extraction'],
            'export_format': analysis_defaults['default_export_format']
        }
        
        self.apply_theme()
        self.init_ui()
    
    def apply_theme(self):
        """Apply the dark scientific theme"""
        self.setStyleSheet(DARK_SCIENTIFIC_THEME)
    
    def init_ui(self):
        """Initialize the user interface with scientific styling"""
        self.setWindowTitle("Research Assistant - Academic Analysis Tool")
        
        # Set window size from config
        ui_config = self.config_manager.get_ui_config()
        self.setGeometry(100, 100, ui_config['window_width'], ui_config['window_height'])
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.setup_import_tab()
        self.setup_analysis_tab()
        self.setup_results_tab()
        
        # Set initial tab
        self.tabs.setCurrentIndex(0)
    
    def setup_import_tab(self):
        """Setup the file import tab with scientific styling"""
        import_tab = QWidget()
        layout = QVBoxLayout(import_tab)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title with academic styling
        title = QLabel("Research Assistant")
        title.setProperty("class", "title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Academic Paper Analysis & Research Gap Identification")
        subtitle.setProperty("class", "subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Model info with badge styling
        model_info = QLabel(f"Active Model: {self.model_config['name']}")
        model_info.setProperty("class", "muted")
        model_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(model_info)
        
        layout.addSpacing(20)
        
        # Import buttons with primary styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        import_files_btn = QPushButton("📁 Import Research Papers")
        import_files_btn.setProperty("class", "primary")
        import_files_btn.setMinimumHeight(50)
        import_files_btn.setFont(QFont("Arial", 12, QFont.Bold))
        import_files_btn.clicked.connect(self.import_files)
        
        import_folder_btn = QPushButton("📂 Select Folder of PDFs")
        import_folder_btn.setProperty("class", "primary")
        import_folder_btn.setMinimumHeight(50)
        import_folder_btn.setFont(QFont("Arial", 12, QFont.Bold))
        import_folder_btn.clicked.connect(self.import_folder)
        
        button_layout.addWidget(import_files_btn)
        button_layout.addWidget(import_folder_btn)
        layout.addLayout(button_layout)
        
        layout.addSpacing(20)
        
        # File list with card styling
        file_group = QGroupBox("Selected Research Papers")
        file_layout = QVBoxLayout(file_group)
        
        self.file_list = QListWidget()
        self.file_list.setAlternatingRowColors(True)
        file_layout.addWidget(self.file_list)
        
        # File actions
        file_actions_layout = QHBoxLayout()
        clear_files_btn = QPushButton("Clear All")
        clear_files_btn.setProperty("class", "danger")
        clear_files_btn.clicked.connect(self.clear_files)
        file_actions_layout.addWidget(clear_files_btn)
        file_actions_layout.addStretch()
        
        file_layout.addLayout(file_actions_layout)
        layout.addWidget(file_group)
        
        # Continue button
        self.continue_btn = QPushButton("Continue to Analysis Configuration →")
        self.continue_btn.setProperty("class", "primary")
        self.continue_btn.setMinimumHeight(45)
        self.continue_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.continue_btn.clicked.connect(self.go_to_analysis_tab)
        self.continue_btn.setEnabled(False)
        layout.addWidget(self.continue_btn)
        
        self.tabs.addTab(import_tab, "📄 Paper Import")
    
    def setup_analysis_tab(self):
        """Setup the analysis configuration tab with scientific styling"""
        analysis_tab = QWidget()
        layout = QVBoxLayout(analysis_tab)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title = QLabel("Analysis Configuration")
        title.setProperty("class", "title")
        layout.addWidget(title)
        
        # Analysis options with enhanced styling
        options_group = QGroupBox("Research Analysis Modules")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)
        
        # Summaries option
        summary_frame = QFrame()
        summary_frame.setProperty("class", "card")
        summary_layout = QHBoxLayout(summary_frame)
        
        self.summaries_cb = QCheckBox("Technical Summaries")
        self.summaries_cb.setChecked(self.analysis_config['summaries'])
        self.summaries_cb.stateChanged.connect(self.update_analysis_config)
        summary_layout.addWidget(self.summaries_cb)
        
        summary_desc = QLabel("Abstractive 150-word summaries for technical audience")
        summary_desc.setProperty("class", "muted")
        summary_layout.addWidget(summary_desc)
        summary_layout.addStretch()
        
        options_layout.addWidget(summary_frame)
        
        # Gap analysis option
        gap_frame = QFrame()
        gap_frame.setProperty("class", "card")
        gap_layout = QHBoxLayout(gap_frame)
        
        self.gap_analysis_cb = QCheckBox("Research Gap Analysis")
        self.gap_analysis_cb.setChecked(self.analysis_config['gap_analysis'])
        self.gap_analysis_cb.stateChanged.connect(self.update_analysis_config)
        gap_layout.addWidget(self.gap_analysis_cb)
        
        gap_desc = QLabel("Topic clustering and gap identification across papers")
        gap_desc.setProperty("class", "muted")
        gap_layout.addWidget(gap_desc)
        gap_layout.addStretch()
        
        options_layout.addWidget(gap_frame)
        
        # GitHub extraction option
        github_frame = QFrame()
        github_frame.setProperty("class", "card")
        github_layout = QHBoxLayout(github_frame)
        
        self.github_cb = QCheckBox("GitHub Repository Extraction")
        self.github_cb.setChecked(self.analysis_config['github_extraction'])
        self.github_cb.stateChanged.connect(self.update_analysis_config)
        github_layout.addWidget(self.github_cb)
        
        github_desc = QLabel("Extract code repositories and research artifacts")
        github_desc.setProperty("class", "muted")
        github_layout.addWidget(github_desc)
        github_layout.addStretch()
        
        options_layout.addWidget(github_frame)
        
        layout.addWidget(options_group)
        
        # Export format with enhanced styling
        export_group = QGroupBox("Output Configuration")
        export_layout = QVBoxLayout(export_group)
        
        export_format_layout = QHBoxLayout()
        export_format_layout.addWidget(QLabel("Export Format:"))
        
        self.markdown_rb = QCheckBox("📝 Markdown")
        self.markdown_rb.setChecked(self.analysis_config['export_format'] == 'markdown')
        self.markdown_rb.toggled.connect(self.update_export_format)
        
        self.html_rb = QCheckBox("🌐 HTML")
        self.html_rb.setChecked(self.analysis_config['export_format'] == 'html')
        self.html_rb.toggled.connect(self.update_export_format)
        
        export_format_layout.addWidget(self.markdown_rb)
        export_format_layout.addWidget(self.html_rb)
        export_format_layout.addStretch()
        
        export_layout.addLayout(export_format_layout)
        layout.addWidget(export_group)
        
        # Progress section with scientific styling
        self.progress_group = QGroupBox("Analysis Progress")
        self.progress_layout = QVBoxLayout(self.progress_group)
        
        self.progress_label = QLabel("Ready to commence analysis")
        self.progress_label.setProperty("class", "accent")
        self.progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setProperty("class", "analysis")
        self.progress_bar.setVisible(False)
        self.progress_layout.addWidget(self.progress_bar)
        
        # Cancel button
        self.cancel_btn = QPushButton("⏹️ Cancel Analysis")
        self.cancel_btn.setProperty("class", "danger")
        self.cancel_btn.clicked.connect(self.cancel_analysis)
        self.cancel_btn.setVisible(False)
        self.progress_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(self.progress_group)
        self.progress_group.setVisible(False)
        
        layout.addStretch()
        
        # Run analysis button
        self.run_analysis_btn = QPushButton("🔬 Start Analysis")
        self.run_analysis_btn.setProperty("class", "primary")
        self.run_analysis_btn.setMinimumHeight(55)
        self.run_analysis_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.run_analysis_btn.clicked.connect(self.run_analysis)
        self.run_analysis_btn.setEnabled(len(self.pdf_files) > 0)
        layout.addWidget(self.run_analysis_btn)
        
        self.tabs.addTab(analysis_tab, "⚙️ Analysis Setup")



    def cancel_analysis(self):
        """Cancel the ongoing analysis"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(5000)  # Wait up to 5 seconds for thread to finish
            self.progress_label.setText("Analysis cancelled")
            self.progress_bar.setValue(0)
            self.cancel_btn.setVisible(False)
            self.run_analysis_btn.setEnabled(True)
            QMessageBox.information(self, "Cancelled", "Analysis was cancelled.")

    def setup_results_tab(self):
        """Setup the results tab with scientific styling"""
        self.results_tab = QWidget()
        layout = QVBoxLayout(self.results_tab)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Results header
        header = QLabel("Research Analysis Results")
        header.setProperty("class", "title")
        layout.addWidget(header)
        
        # Results tabs
        self.results_tabs = QTabWidget()
        layout.addWidget(self.results_tabs)
        
        # Setup sub-tabs with enhanced styling
        self.setup_summaries_tab()
        self.setup_gaps_tab()
        self.setup_github_tab()
        
        # Initially disabled
        self.results_tabs.setEnabled(False)
        
        self.tabs.addTab(self.results_tab, "📊 Results")
    
    def setup_summaries_tab(self):
        """Setup the paper summaries tab with academic styling"""
        summaries_tab = QWidget()
        layout = QVBoxLayout(summaries_tab)
        layout.setSpacing(8)
        
        # Filters with card styling
        filter_frame = QFrame()
        filter_frame.setProperty("class", "card")
        filter_layout = QHBoxLayout(filter_frame)
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.year_filter = QComboBox()
        self.year_filter.addItem("All Years")
        self.year_filter.currentTextChanged.connect(self.filter_summaries)
        
        self.topic_filter = QComboBox()
        self.topic_filter.addItem("All Topics")
        self.topic_filter.currentTextChanged.connect(self.filter_summaries)
        
        filter_layout.addWidget(QLabel("Publication Year:"))
        filter_layout.addWidget(self.year_filter)
        filter_layout.addWidget(QLabel("Research Topic:"))
        filter_layout.addWidget(self.topic_filter)
        filter_layout.addStretch()
        
        layout.addWidget(filter_frame)
        
        # Splitter for paper list and summary view
        splitter = QSplitter(Qt.Horizontal)
        
        # Paper list with enhanced styling
        paper_list_frame = QFrame()
        paper_list_layout = QVBoxLayout(paper_list_frame)
        
        paper_list_label = QLabel("Research Papers")
        paper_list_label.setProperty("class", "accent")
        paper_list_layout.addWidget(paper_list_label)
        
        self.paper_list = QListWidget()
        self.paper_list.setAlternatingRowColors(True)
        self.paper_list.currentRowChanged.connect(self.show_paper_summary)
        paper_list_layout.addWidget(self.paper_list)
        
        splitter.addWidget(paper_list_frame)
        
        # Summary view with card styling
        summary_frame = QFrame()
        summary_frame.setProperty("class", "card")
        summary_layout = QVBoxLayout(summary_frame)
        
        self.summary_title = QLabel("Select a research paper to view technical summary")
        self.summary_title.setProperty("class", "accent")
        self.summary_title.setWordWrap(True)
        summary_layout.addWidget(self.summary_title)
        
        # Separator
        separator = QFrame()
        separator.setProperty("class", "separator")
        summary_layout.addWidget(separator)
        
        self.summary_content = QTextEdit()
        self.summary_content.setReadOnly(True)
        self.summary_content.setFont(QFont("Consolas", 10))
        summary_layout.addWidget(self.summary_content)
        
        splitter.addWidget(summary_frame)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        
        self.results_tabs.addTab(summaries_tab, "📄 Paper Summaries")
    
    def setup_gaps_tab(self):
        """Setup the gap analysis tab"""
        gaps_tab = QWidget()
        layout = QVBoxLayout(gaps_tab)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.cluster_filter = QComboBox()
        self.cluster_filter.addItem("All Clusters")
        self.cluster_filter.currentTextChanged.connect(self.filter_gaps)
        
        self.impact_filter = QComboBox()
        self.impact_filter.addItem("All Impact Levels")
        self.impact_filter.addItems(["High", "Medium", "Low"])
        self.impact_filter.currentTextChanged.connect(self.filter_gaps)
        
        filter_layout.addWidget(QLabel("Topic Cluster:"))
        filter_layout.addWidget(self.cluster_filter)
        filter_layout.addWidget(QLabel("Impact:"))
        filter_layout.addWidget(self.impact_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Gaps table
        self.gaps_table = QTableWidget()
        self.gaps_table.setColumnCount(4)
        self.gaps_table.setHorizontalHeaderLabels(["Statement", "Impact", "Cluster", "Papers"])
        self.gaps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.gaps_table.cellClicked.connect(self.show_gap_details)
        layout.addWidget(self.gaps_table)
        
        # Gap details
        self.gap_details = QTextEdit()
        self.gap_details.setReadOnly(True)
        self.gap_details.setMaximumHeight(200)
        layout.addWidget(self.gap_details)
        
        self.results_tabs.addTab(gaps_tab, "Gap Analysis")
    
    def setup_github_tab(self):
        """Setup the GitHub repositories tab"""
        github_tab = QWidget()
        layout = QVBoxLayout(github_tab)
        
        # GitHub links table
        self.github_table = QTableWidget()
        self.github_table.setColumnCount(3)
        self.github_table.setHorizontalHeaderLabels(["Paper", "URL", "Type"])
        self.github_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.github_table)
        
        self.results_tabs.addTab(github_tab, "GitHub Repositories")
    
    def import_files(self):
        """Import individual PDF files"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Research Papers", "", "PDF Files (*.pdf)")
        
        if files:
            self.pdf_files.extend(files)
            self.update_file_list()
            self.continue_btn.setEnabled(True)
            self.run_analysis_btn.setEnabled(True)
    
    def import_folder(self):
        """Import PDF files from a folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with PDFs")
        
        if folder:
            pdf_files = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
            
            if pdf_files:
                self.pdf_files.extend(pdf_files)
                self.update_file_list()
                self.continue_btn.setEnabled(True)
                self.run_analysis_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "No PDFs Found", "No PDF files found in the selected folder.")
    
    def update_file_list(self):
        """Update the file list widget"""
        self.file_list.clear()
        for file_path in self.pdf_files:
            self.file_list.addItem(os.path.basename(file_path))
    
    def clear_files(self):
        """Clear all selected files"""
        self.pdf_files.clear()
        self.file_list.clear()
        self.continue_btn.setEnabled(False)
        self.run_analysis_btn.setEnabled(False)
    
    def go_to_analysis_tab(self):
        """Switch to analysis settings tab"""
        self.tabs.setCurrentIndex(1)
    
    def update_analysis_config(self):
        """Update analysis configuration based on UI state"""
        self.analysis_config['summaries'] = self.summaries_cb.isChecked()
        self.analysis_config['gap_analysis'] = self.gap_analysis_cb.isChecked()
        self.analysis_config['github_extraction'] = self.github_cb.isChecked()
    
    def update_export_format(self):
        """Update export format configuration"""
        if self.markdown_rb.isChecked():
            self.analysis_config['export_format'] = 'markdown'
        elif self.html_rb.isChecked():
            self.analysis_config['export_format'] = 'html'
    
    def run_analysis(self):
        """Start the analysis process"""
        if not self.pdf_files:
            QMessageBox.warning(self, "No Files", "Please import some PDF files first.")
            return
        
        # Show processing tab
        self.tabs.setCurrentIndex(2)
        self.results_tabs.setEnabled(False)
        
        # Create and start worker thread with model config
        self.worker = AnalysisWorker(self.pdf_files, self.analysis_config, self.model_config)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished_analysis.connect(self.analysis_finished)
        self.worker.error_occurred.connect(self.analysis_error)
        self.worker.start()
    
    def update_progress(self, message: str, percentage: int):
        """Update progress display"""
        # You can implement a proper progress dialog here
        print(f"Progress: {percentage}% - {message}")
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        import_action = file_menu.addAction('Import Papers')
        import_action.triggered.connect(self.import_files)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        
        model_config_action = settings_menu.addAction('Model Configuration')
        model_config_action.triggered.connect(self.show_model_config_dialog)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about_dialog)
    
    def show_model_config_dialog(self):
        """Show model configuration dialog"""
        dialog = ModelConfigDialog(self.config_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            new_config = dialog.get_config()
            self.config_manager.save_model_config(new_config)
            self.model_config = new_config
            QMessageBox.information(self, "Configuration Saved", 
                                  "Model configuration has been saved. Restart the application for changes to take effect.")


    def analysis_finished(self, results: Dict):
        """Handle completed analysis"""
        self.analysis_results = results
        self.display_results()
        self.results_tabs.setEnabled(True)
        QMessageBox.information(self, "Analysis Complete", "Research paper analysis completed successfully!")
    
    def analysis_error(self, error_message: str):
        """Handle analysis errors"""
        QMessageBox.critical(self, "Analysis Error", f"An error occurred during analysis:\n{error_message}")
    
    def display_results(self):
        """Display analysis results in the UI"""
        if not self.analysis_results:
            return
        
        # Display summaries
        self.display_summaries()
        
        # Display gap analysis
        self.display_gaps()
        
        # Display GitHub links
        self.display_github_links()
    
    def display_summaries(self):
        """Display paper summaries"""
        self.paper_list.clear()
        
        if 'summaries' in self.analysis_results:
            for summary in self.analysis_results['summaries']:
                item_text = f"{summary['paper_title']} ({summary['year']})"
                if summary['has_github']:
                    item_text += " 🔗"
                self.paper_list.addItem(item_text)
        
        # Update filters
        self.update_summary_filters()
    
    def update_summary_filters(self):
        """Update summary filter options"""
        if not self.analysis_results or 'summaries' not in self.analysis_results:
            return
        
        # Year filter
        years = set()
        for summary in self.analysis_results['summaries']:
            if summary['year'] != 'Unknown':
                years.add(summary['year'])
        
        self.year_filter.clear()
        self.year_filter.addItem("All Years")
        for year in sorted(years, reverse=True):
            self.year_filter.addItem(year)
    
    def show_paper_summary(self, row: int):
        """Show summary for selected paper"""
        if row < 0 or not self.analysis_results or 'summaries' not in self.analysis_results:
            return
        
        summary = self.analysis_results['summaries'][row]
        self.summary_title.setText(f"{summary['paper_title']} ({summary['year']})")
        self.summary_content.setText(summary['summary'])
    
    def filter_summaries(self):
        """Filter summaries based on selected criteria"""
        # Implementation for filtering summaries
        pass
    
    def display_gaps(self):
        """Display gap analysis results"""
        self.gaps_table.setRowCount(0)
        
        if 'gaps' not in self.analysis_results:
            return
        
        gaps = self.analysis_results['gaps']
        self.gaps_table.setRowCount(len(gaps))
        
        for i, gap in enumerate(gaps):
            self.gaps_table.setItem(i, 0, QTableWidgetItem(gap.get('statement', 'N/A')))
            self.gaps_table.setItem(i, 1, QTableWidgetItem(gap.get('impact', 'N/A')))
            self.gaps_table.setItem(i, 2, QTableWidgetItem(str(gap.get('cluster_id', 'N/A'))))
            papers_text = ', '.join(gap.get('papers_involved', []))
            self.gaps_table.setItem(i, 3, QTableWidgetItem(papers_text))
        
        # Update cluster filter
        clusters = set()
        for gap in gaps:
            clusters.add(f"Cluster {gap.get('cluster_id', '')}")
        
        self.cluster_filter.clear()
        self.cluster_filter.addItem("All Clusters")
        for cluster in sorted(clusters):
            self.cluster_filter.addItem(cluster)
    
    def show_gap_details(self, row: int, column: int):
        """Show details for selected gap"""
        if row < 0 or not self.analysis_results or 'gaps' not in self.analysis_results:
            return
        
        gap = self.analysis_results['gaps'][row]
        details = f"Statement: {gap.get('statement', 'N/A')}\n\n"
        details += f"Impact: {gap.get('impact', 'N/A')}\n\n"
        details += f"Evidence: {gap.get('evidence', 'N/A')}\n\n"
        details += f"Next Steps: {gap.get('next_steps', 'N/A')}\n\n"
        details += f"Papers Involved: {', '.join(gap.get('papers_involved', []))}"
        
        self.gap_details.setText(details)
    
    def filter_gaps(self):
        """Filter gaps based on selected criteria"""
        # Implementation for filtering gaps
        pass
    
    def display_github_links(self):
        """Display GitHub repository links"""
        self.github_table.setRowCount(0)
        
        if 'github_links' not in self.analysis_results:
            return
        
        links = self.analysis_results['github_links']
        self.github_table.setRowCount(len(links))
        
        for i, link in enumerate(links):
            self.github_table.setItem(i, 0, QTableWidgetItem(link.get('paper', 'N/A')))
            self.github_table.setItem(i, 1, QTableWidgetItem(link.get('url', 'N/A')))
            self.github_table.setItem(i, 2, QTableWidgetItem(link.get('type', 'N/A')))
    
    def show_about_dialog(self):
        """Show about dialog"""
        QMessageBox.about(self, "About AI Research Assistant",
                         "AI Research Assistant\n\n"
                         "A desktop application for summarizing research papers, "
                         "finding research gaps, and extracting GitHub repositories.\n\n"
                         "Built with PyQt5 and GPT4All.")
    


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = ResearchAssistantApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
