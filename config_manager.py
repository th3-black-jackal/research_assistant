import os
import configparser
from typing import List, Dict, Any, Optional
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTabWidget, 
                            QWidget, QGroupBox, QFormLayout, QLineEdit, QPushButton, 
                            QSpinBox, QDoubleSpinBox, QCheckBox, QHBoxLayout, 
                            QComboBox, QTextEdit, QMessageBox, QFileDialog)
from PyQt5.QtGui import QFont


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.default_config = {
            'model': {
                'name': 'orca-mini-3b-gguf2-q4_0.gguf',
                'model_path': '',
                'max_tokens': '2000',
                'temperature': '0.1',
                'top_k': '40',
                'top_p': '0.9',
                'repeat_penalty': '1.1'
            },
            'analysis': {
                'default_summaries': 'true',
                'default_gap_analysis': 'true',
                'default_github_extraction': 'true',
                'default_export_format': 'markdown',
                'summary_length': '150',
                'embedding_chunk_size': '1000',
                'cluster_eps': '0.5',
                'cluster_min_samples': '2'
            },
            'ui': {
                'window_width': '1200',
                'window_height': '800',
                'auto_save_results': 'true',
                'results_directory': './results',
                'theme': 'light'
            },
            'advanced': {
                'enable_debug_logging': 'false',
                'max_concurrent_tasks': '2',
                'cache_embeddings': 'true',
                'embedding_cache_size': '100'
            }
        }
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            self._migrate_config()
        else:
            self.create_default_config()
    
    def _migrate_config(self):
        """Migrate old config files to new format"""
        needs_save = False
        
        # Ensure all sections exist
        for section, options in self.default_config.items():
            if not self.config.has_section(section):
                self.config[section] = options
                needs_save = True
        
        # Ensure all options exist
        for section, options in self.default_config.items():
            for option, default_value in options.items():
                if not self.config.has_option(section, option):
                    self.config.set(section, option, default_value)
                    needs_save = True
        
        if needs_save:
            self.save_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        for section, options in self.default_config.items():
            self.config[section] = options
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        return {
            'name': self.config.get('model', 'name', fallback=self.default_config['model']['name']),
            'model_path': self.config.get('model', 'model_path', fallback=self.default_config['model']['model_path']),
            'max_tokens': self.config.getint('model', 'max_tokens', fallback=int(self.default_config['model']['max_tokens'])),
            'temperature': self.config.getfloat('model', 'temperature', fallback=float(self.default_config['model']['temperature'])),
            'top_k': self.config.getint('model', 'top_k', fallback=int(self.default_config['model']['top_k'])),
            'top_p': self.config.getfloat('model', 'top_p', fallback=float(self.default_config['model']['top_p'])),
            'repeat_penalty': self.config.getfloat('model', 'repeat_penalty', fallback=float(self.default_config['model']['repeat_penalty']))
        }
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration"""
        return {
            'default_summaries': self.config.getboolean('analysis', 'default_summaries', fallback=True),
            'default_gap_analysis': self.config.getboolean('analysis', 'default_gap_analysis', fallback=True),
            'default_github_extraction': self.config.getboolean('analysis', 'default_github_extraction', fallback=True),
            'default_export_format': self.config.get('analysis', 'default_export_format', fallback='markdown'),
            'summary_length': self.config.getint('analysis', 'summary_length', fallback=150),
            'embedding_chunk_size': self.config.getint('analysis', 'embedding_chunk_size', fallback=1000),
            'cluster_eps': self.config.getfloat('analysis', 'cluster_eps', fallback=0.5),
            'cluster_min_samples': self.config.getint('analysis', 'cluster_min_samples', fallback=2)
        }
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration"""
        return {
            'window_width': self.config.getint('ui', 'window_width', fallback=1200),
            'window_height': self.config.getint('ui', 'window_height', fallback=800),
            'auto_save_results': self.config.getboolean('ui', 'auto_save_results', fallback=True),
            'results_directory': self.config.get('ui', 'results_directory', fallback='./results'),
            'theme': self.config.get('ui', 'theme', fallback='light')
        }
    
    def get_advanced_config(self) -> Dict[str, Any]:
        """Get advanced configuration"""
        return {
            'enable_debug_logging': self.config.getboolean('advanced', 'enable_debug_logging', fallback=False),
            'max_concurrent_tasks': self.config.getint('advanced', 'max_concurrent_tasks', fallback=2),
            'cache_embeddings': self.config.getboolean('advanced', 'cache_embeddings', fallback=True),
            'embedding_cache_size': self.config.getint('advanced', 'embedding_cache_size', fallback=100)
        }
    
    def save_model_config(self, model_config: Dict[str, Any]):
        """Save model configuration"""
        for key, value in model_config.items():
            self.config.set('model', key, str(value))
        self.save_config()
    
    def save_analysis_config(self, analysis_config: Dict[str, Any]):
        """Save analysis configuration"""
        for key, value in analysis_config.items():
            self.config.set('analysis', key, str(value).lower())
        self.save_config()
    
    def save_ui_config(self, ui_config: Dict[str, Any]):
        """Save UI configuration"""
        for key, value in ui_config.items():
            self.config.set('ui', key, str(value).lower())
        self.save_config()
    
    def save_advanced_config(self, advanced_config: Dict[str, Any]):
        """Save advanced configuration"""
        for key, value in advanced_config.items():
            self.config.set('advanced', key, str(value).lower())
        self.save_config()
    
    def get_all_config(self) -> Dict[str, Dict[str, Any]]:
        """Get all configuration as a dictionary"""
        return {
            'model': self.get_model_config(),
            'analysis': self.get_analysis_config(),
            'ui': self.get_ui_config(),
            'advanced': self.get_advanced_config()
        }
    
    def save_all_config(self, config_dict: Dict[str, Dict[str, Any]]):
        """Save all configuration from dictionary"""
        for section, options in config_dict.items():
            for key, value in options.items():
                self.config.set(section, key, str(value))
        self.save_config()
    
    def refresh_config(self):
        """Reload configuration from file"""
        self.load_config()


class ConfigEditorWindow(QDialog):
    """Main configuration editor window"""
    
    config_updated = pyqtSignal()
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.original_config = self.config_manager.get_all_config()
        self.current_config = self._deep_copy_config(self.original_config)
        self.init_ui()
        self.load_config_to_ui()
    
    def _deep_copy_config(self, config: Dict) -> Dict:
        """Create a deep copy of the configuration"""
        return {section: options.copy() for section, options in config.items()}
    
    def init_ui(self):
        """Initialize the configuration editor UI"""
        self.setWindowTitle("Configuration Editor")
        self.setModal(False)  # Non-modal so user can switch between windows
        self.resize(900, 700)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Application Configuration")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Config file info
        config_info = QLabel(f"Config file: {os.path.abspath(self.config_manager.config_file)}")
        config_info.setStyleSheet("color: #666; font-size: 10pt;")
        layout.addWidget(config_info)
        
        # Tab widget for different config sections
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.setup_model_tab()
        self.setup_analysis_tab()
        self.setup_ui_tab()
        self.setup_advanced_tab()
        self.setup_config_view_tab()
        
        # Status label
        self.status_label = QLabel("Configuration loaded")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.clicked.connect(self.save_config)
        self.save_btn.setMinimumHeight(40)
        
        self.refresh_btn = QPushButton("Refresh from File")
        self.refresh_btn.clicked.connect(self.refresh_config)
        self.refresh_btn.setMinimumHeight(40)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        self.reset_btn.setMinimumHeight(40)
        
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.apply_changes)
        self.apply_btn.setMinimumHeight(40)
        self.apply_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.apply_btn)
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setMinimumHeight(40)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def setup_model_tab(self):
        """Setup model configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Model settings group
        model_group = QGroupBox("GPT4All Model Settings")
        model_layout = QFormLayout(model_group)
        
        self.model_name = QLineEdit()
        self.model_name.textChanged.connect(self.on_config_changed)
        model_layout.addRow("Model Name:", self.model_name)
        
        self.model_path = QLineEdit()
        self.model_path.textChanged.connect(self.on_config_changed)
        model_layout.addRow("Model Path:", self.model_path)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_model_path)
        model_layout.addRow("", browse_btn)
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(100, 10000)
        self.max_tokens.valueChanged.connect(self.on_config_changed)
        model_layout.addRow("Max Tokens:", self.max_tokens)
        
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.0, 2.0)
        self.temperature.setSingleStep(0.1)
        self.temperature.setDecimals(2)
        self.temperature.valueChanged.connect(self.on_config_changed)
        model_layout.addRow("Temperature:", self.temperature)
        
        self.top_k = QSpinBox()
        self.top_k.setRange(1, 100)
        self.top_k.valueChanged.connect(self.on_config_changed)
        model_layout.addRow("Top-K:", self.top_k)
        
        self.top_p = QDoubleSpinBox()
        self.top_p.setRange(0.0, 1.0)
        self.top_p.setSingleStep(0.05)
        self.top_p.setDecimals(2)
        self.top_p.valueChanged.connect(self.on_config_changed)
        model_layout.addRow("Top-P:", self.top_p)
        
        self.repeat_penalty = QDoubleSpinBox()
        self.repeat_penalty.setRange(1.0, 2.0)
        self.repeat_penalty.setSingleStep(0.1)
        self.repeat_penalty.setDecimals(2)
        self.repeat_penalty.valueChanged.connect(self.on_config_changed)
        model_layout.addRow("Repeat Penalty:", self.repeat_penalty)
        
        layout.addWidget(model_group)
        
        # Info text
        info_label = QLabel(
            "Note: Model will be automatically downloaded if not found in the specified path.\n"
            "Leave model path empty to use the default GPT4All models directory.\n"
            "Changes to model settings require restarting the application to take effect."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10pt; padding: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Model")
    
    def setup_analysis_tab(self):
        """Setup analysis configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Default analysis settings
        defaults_group = QGroupBox("Default Analysis Settings")
        defaults_layout = QVBoxLayout(defaults_group)
        
        self.default_summaries = QCheckBox("Enable summaries by default")
        self.default_summaries.stateChanged.connect(self.on_config_changed)
        defaults_layout.addWidget(self.default_summaries)
        
        self.default_gap_analysis = QCheckBox("Enable gap analysis by default")
        self.default_gap_analysis.stateChanged.connect(self.on_config_changed)
        defaults_layout.addWidget(self.default_gap_analysis)
        
        self.default_github_extraction = QCheckBox("Enable GitHub extraction by default")
        self.default_github_extraction.stateChanged.connect(self.on_config_changed)
        defaults_layout.addWidget(self.default_github_extraction)
        
        # Export format
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("Default Export Format:"))
        
        self.export_markdown = QCheckBox("Markdown")
        self.export_markdown.toggled.connect(self.on_config_changed)
        
        self.export_html = QCheckBox("HTML")
        self.export_html.toggled.connect(self.on_config_changed)
        
        export_layout.addWidget(self.export_markdown)
        export_layout.addWidget(self.export_html)
        export_layout.addStretch()
        
        defaults_layout.addLayout(export_layout)
        layout.addWidget(defaults_group)
        
        # Analysis parameters
        params_group = QGroupBox("Analysis Parameters")
        params_layout = QFormLayout(params_group)
        
        self.summary_length = QSpinBox()
        self.summary_length.setRange(50, 500)
        self.summary_length.setSuffix(" words")
        self.summary_length.valueChanged.connect(self.on_config_changed)
        params_layout.addRow("Summary Length:", self.summary_length)
        
        self.embedding_chunk_size = QSpinBox()
        self.embedding_chunk_size.setRange(500, 5000)
        self.embedding_chunk_size.setSuffix(" characters")
        self.embedding_chunk_size.valueChanged.connect(self.on_config_changed)
        params_layout.addRow("Embedding Chunk Size:", self.embedding_chunk_size)
        
        self.cluster_eps = QDoubleSpinBox()
        self.cluster_eps.setRange(0.1, 1.0)
        self.cluster_eps.setSingleStep(0.1)
        self.cluster_eps.setDecimals(2)
        self.cluster_eps.valueChanged.connect(self.on_config_changed)
        params_layout.addRow("Cluster EPS:", self.cluster_eps)
        
        self.cluster_min_samples = QSpinBox()
        self.cluster_min_samples.setRange(1, 10)
        self.cluster_min_samples.valueChanged.connect(self.on_config_changed)
        params_layout.addRow("Cluster Min Samples:", self.cluster_min_samples)
        
        layout.addWidget(params_group)
        layout.addStretch()
        self.tabs.addTab(tab, "Analysis")
    
    def setup_ui_tab(self):
        """Setup UI configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Window settings
        window_group = QGroupBox("Window Settings")
        window_layout = QFormLayout(window_group)
        
        self.window_width = QSpinBox()
        self.window_width.setRange(800, 2000)
        self.window_width.valueChanged.connect(self.on_config_changed)
        window_layout.addRow("Window Width:", self.window_width)
        
        self.window_height = QSpinBox()
        self.window_height.setRange(600, 1500)
        self.window_height.valueChanged.connect(self.on_config_changed)
        window_layout.addRow("Window Height:", self.window_height)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "system"])
        self.theme_combo.currentTextChanged.connect(self.on_config_changed)
        window_layout.addRow("Theme:", self.theme_combo)
        
        layout.addWidget(window_group)
        
        # Results settings
        results_group = QGroupBox("Results Settings")
        results_layout = QVBoxLayout(results_group)
        
        self.auto_save_results = QCheckBox("Auto-save results after analysis")
        self.auto_save_results.stateChanged.connect(self.on_config_changed)
        results_layout.addWidget(self.auto_save_results)
        
        results_dir_layout = QHBoxLayout()
        results_dir_layout.addWidget(QLabel("Results Directory:"))
        
        self.results_directory = QLineEdit()
        self.results_directory.textChanged.connect(self.on_config_changed)
        results_dir_layout.addWidget(self.results_directory)
        
        browse_results_btn = QPushButton("Browse...")
        browse_results_btn.clicked.connect(self.browse_results_directory)
        results_dir_layout.addWidget(browse_results_btn)
        
        results_layout.addLayout(results_dir_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        self.tabs.addTab(tab, "UI")
    
    def setup_advanced_tab(self):
        """Setup advanced configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance settings
        performance_group = QGroupBox("Performance Settings")
        performance_layout = QFormLayout(performance_group)
        
        self.max_concurrent_tasks = QSpinBox()
        self.max_concurrent_tasks.setRange(1, 10)
        self.max_concurrent_tasks.valueChanged.connect(self.on_config_changed)
        performance_layout.addRow("Max Concurrent Tasks:", self.max_concurrent_tasks)
        
        self.cache_embeddings = QCheckBox("Cache embeddings for faster processing")
        self.cache_embeddings.stateChanged.connect(self.on_config_changed)
        performance_layout.addRow("", self.cache_embeddings)
        
        self.embedding_cache_size = QSpinBox()
        self.embedding_cache_size.setRange(10, 1000)
        self.embedding_cache_size.setSuffix(" items")
        self.embedding_cache_size.valueChanged.connect(self.on_config_changed)
        performance_layout.addRow("Embedding Cache Size:", self.embedding_cache_size)
        
        layout.addWidget(performance_group)
        
        # Debug settings
        debug_group = QGroupBox("Debug Settings")
        debug_layout = QVBoxLayout(debug_group)
        
        self.enable_debug_logging = QCheckBox("Enable debug logging")
        self.enable_debug_logging.stateChanged.connect(self.on_config_changed)
        debug_layout.addWidget(self.enable_debug_logging)
        
        layout.addWidget(debug_group)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Advanced")
    
    def setup_config_view_tab(self):
        """Setup configuration view tab (read-only)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Raw config view
        raw_group = QGroupBox("Raw Configuration File Content")
        raw_layout = QVBoxLayout(raw_group)
        
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        self.config_text.setFont(QFont("Courier", 9))
        raw_layout.addWidget(self.config_text)
        
        refresh_raw_btn = QPushButton("Refresh View")
        refresh_raw_btn.clicked.connect(self.update_raw_config_view)
        raw_layout.addWidget(refresh_raw_btn)
        
        layout.addWidget(raw_group)
        
        # Config file actions
        actions_group = QGroupBox("Configuration File Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        open_in_editor_btn = QPushButton("Open in Text Editor")
        open_in_editor_btn.clicked.connect(self.open_in_editor)
        
        reload_from_file_btn = QPushButton("Reload from File")
        reload_from_file_btn.clicked.connect(self.reload_from_file)
        
        show_file_location_btn = QPushButton("Show File Location")
        show_file_location_btn.clicked.connect(self.show_file_location)
        
        actions_layout.addWidget(open_in_editor_btn)
        actions_layout.addWidget(reload_from_file_btn)
        actions_layout.addWidget(show_file_location_btn)
        actions_layout.addStretch()
        
        layout.addWidget(actions_group)
        
        self.tabs.addTab(tab, "Raw Config")
    
    def browse_model_path(self):
        """Browse for model directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Model Directory", self.model_path.text())
        if directory:
            self.model_path.setText(directory)
    
    def browse_results_directory(self):
        """Browse for results directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Results Directory", self.results_directory.text())
        if directory:
            self.results_directory.setText(directory)
    
    def load_config_to_ui(self):
        """Load current configuration into UI elements"""
        config = self.current_config
        
        # Model tab
        model_config = config['model']
        self.model_name.setText(model_config['name'])
        self.model_path.setText(model_config['model_path'])
        self.max_tokens.setValue(model_config['max_tokens'])
        self.temperature.setValue(model_config['temperature'])
        self.top_k.setValue(model_config['top_k'])
        self.top_p.setValue(model_config['top_p'])
        self.repeat_penalty.setValue(model_config['repeat_penalty'])
        
        # Analysis tab
        analysis_config = config['analysis']
        self.default_summaries.setChecked(analysis_config['default_summaries'])
        self.default_gap_analysis.setChecked(analysis_config['default_gap_analysis'])
        self.default_github_extraction.setChecked(analysis_config['default_github_extraction'])
        
        export_format = analysis_config['default_export_format']
        self.export_markdown.setChecked(export_format == 'markdown')
        self.export_html.setChecked(export_format == 'html')
        
        self.summary_length.setValue(analysis_config['summary_length'])
        self.embedding_chunk_size.setValue(analysis_config['embedding_chunk_size'])
        self.cluster_eps.setValue(analysis_config['cluster_eps'])
        self.cluster_min_samples.setValue(analysis_config['cluster_min_samples'])
        
        # UI tab
        ui_config = config['ui']
        self.window_width.setValue(ui_config['window_width'])
        self.window_height.setValue(ui_config['window_height'])
        self.theme_combo.setCurrentText(ui_config['theme'])
        self.auto_save_results.setChecked(ui_config['auto_save_results'])
        self.results_directory.setText(ui_config['results_directory'])
        
        # Advanced tab
        advanced_config = config['advanced']
        self.max_concurrent_tasks.setValue(advanced_config['max_concurrent_tasks'])
        self.cache_embeddings.setChecked(advanced_config['cache_embeddings'])
        self.embedding_cache_size.setValue(advanced_config['embedding_cache_size'])
        self.enable_debug_logging.setChecked(advanced_config['enable_debug_logging'])
        
        # Update raw config view
        self.update_raw_config_view()
        
        self.config_changed = False
        self.update_status()
    
    def update_raw_config_view(self):
        """Update the raw configuration text view"""
        try:
            with open(self.config_manager.config_file, 'r') as f:
                content = f.read()
            self.config_text.setText(content)
        except Exception as e:
            self.config_text.setText(f"Error reading config file: {e}")
    
    def on_config_changed(self):
        """Handle configuration changes"""
        self.config_changed = True
        self.update_status()
    
    def update_status(self):
        """Update status label"""
        if self.config_changed:
            self.status_label.setText("Unsaved changes")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.status_label.setText("Configuration saved")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Update current_config from UI
            self.update_config_from_ui()
            
            # Save to file
            self.config_manager.save_all_config(self.current_config)
            
            self.config_changed = False
            self.update_status()
            self.update_raw_config_view()
            
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")
    
    def refresh_config(self):
        """Refresh configuration from file"""
        try:
            self.config_manager.refresh_config()
            self.current_config = self.config_manager.get_all_config()
            self.load_config_to_ui()
            QMessageBox.information(self, "Success", "Configuration refreshed from file!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh configuration: {e}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self, "Confirm Reset", 
            "Are you sure you want to reset all configuration to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.create_default_config()
            self.current_config = self.config_manager.get_all_config()
            self.load_config_to_ui()
            QMessageBox.information(self, "Success", "Configuration reset to defaults!")
    
    def apply_changes(self):
        """Apply changes to the running application"""
        self.update_config_from_ui()
        self.config_updated.emit()
        QMessageBox.information(self, "Success", 
                              "Configuration changes applied!\n\n"
                              "Note: Some changes (like model settings) may require restarting the application.")
    
    def update_config_from_ui(self):
        """Update current_config from UI elements"""
        # Model config
        self.current_config['model']['name'] = self.model_name.text().strip()
        self.current_config['model']['model_path'] = self.model_path.text().strip()
        self.current_config['model']['max_tokens'] = self.max_tokens.value()
        self.current_config['model']['temperature'] = self.temperature.value()
        self.current_config['model']['top_k'] = self.top_k.value()
        self.current_config['model']['top_p'] = self.top_p.value()
        self.current_config['model']['repeat_penalty'] = self.repeat_penalty.value()
        
        # Analysis config
        self.current_config['analysis']['default_summaries'] = self.default_summaries.isChecked()
        self.current_config['analysis']['default_gap_analysis'] = self.default_gap_analysis.isChecked()
        self.current_config['analysis']['default_github_extraction'] = self.default_github_extraction.isChecked()
        
        if self.export_markdown.isChecked():
            self.current_config['analysis']['default_export_format'] = 'markdown'
        elif self.export_html.isChecked():
            self.current_config['analysis']['default_export_format'] = 'html'
        
        self.current_config['analysis']['summary_length'] = self.summary_length.value()
        self.current_config['analysis']['embedding_chunk_size'] = self.embedding_chunk_size.value()
        self.current_config['analysis']['cluster_eps'] = self.cluster_eps.value()
        self.current_config['analysis']['cluster_min_samples'] = self.cluster_min_samples.value()
        
        # UI config
        self.current_config['ui']['window_width'] = self.window_width.value()
        self.current_config['ui']['window_height'] = self.window_height.value()
        self.current_config['ui']['theme'] = self.theme_combo.currentText()
        self.current_config['ui']['auto_save_results'] = self.auto_save_results.isChecked()
        self.current_config['ui']['results_directory'] = self.results_directory.text()
        
        # Advanced config
        self.current_config['advanced']['max_concurrent_tasks'] = self.max_concurrent_tasks.value()
        self.current_config['advanced']['cache_embeddings'] = self.cache_embeddings.isChecked()
        self.current_config['advanced']['embedding_cache_size'] = self.embedding_cache_size.value()
        self.current_config['advanced']['enable_debug_logging'] = self.enable_debug_logging.isChecked()
    
    def open_in_editor(self):
        """Open config file in system text editor"""
        try:
            if sys.platform == "win32":
                os.startfile(self.config_manager.config_file)
            elif sys.platform == "darwin":  # macOS
                os.system(f"open {self.config_manager.config_file}")
            else:  # Linux and other Unix-like
                os.system(f"xdg-open {self.config_manager.config_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open config file: {e}")
    
    def reload_from_file(self):
        """Reload configuration from file and update UI"""
        try:
            self.config_manager.load_config()
            self.current_config = self.config_manager.get_all_config()
            self.load_config_to_ui()
            QMessageBox.information(self, "Success", "Configuration reloaded from file!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reload configuration: {e}")
    
    def show_file_location(self):
        """Show config file location in file explorer"""
        try:
            config_path = os.path.abspath(self.config_manager.config_file)
            if sys.platform == "win32":
                os.startfile(os.path.dirname(config_path))
            elif sys.platform == "darwin":  # macOS
                os.system(f"open {os.path.dirname(config_path)}")
            else:  # Linux and other Unix-like
                os.system(f"xdg-open {os.path.dirname(config_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show file location: {e}")