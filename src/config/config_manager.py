"""Configuration manager for bibliometric web application.

This module provides a centralized configuration system for the bibliometric
analysis pipeline. It defines the PipelineConfig dataclass for storing configuration
settings and the ConfigManager class for loading configurations from various sources.
"""

__all__ = ['ConfigManager', 'PipelineConfig']

import os
import argparse
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class PipelineConfig:
    """Configuration settings for the bibliometric analysis pipeline."""
    # Search settings
    domain1: str
    domain2: str
    domain3: str
    max_results: int
    year_start: int
    year_end: Optional[int] = None
    email: Optional[str] = None
    
    # API settings
    anthropic_api_path: Optional[str] = None
    sciencedirect_api_path: Optional[str] = None
    
    # Output settings
    figures_dir: str = "figures"
    report_file: str = "report.md"
    generate_pdf: bool = False
    pandoc_path: Optional[str] = None
    table_file: str = "articles_table.csv"
    table_format: str = "csv"
    
    # Flow control
    skip_searches: bool = False
    skip_integration: bool = False
    skip_domain_analysis: bool = False
    skip_classification: bool = False
    skip_table: bool = False
    only_search: bool = False
    only_analysis: bool = False
    only_report: bool = False
    
    def validate(self) -> bool:
        """Validate configuration settings.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        # Check required files exist
        for filepath in [self.domain1, self.domain2]:
            if not os.path.exists(filepath):
                return False
                
        # Check domain3 if provided
        if self.domain3 and not os.path.exists(self.domain3):
            return False
            
        # Check that output directories exist or can be created
        os.makedirs(self.figures_dir, exist_ok=True)
            
        return True

    @classmethod
    def create_from_form(cls, form_data: Dict[str, Any]) -> 'PipelineConfig':
        """Create configuration from web form data.
        
        Args:
            form_data: Dictionary containing form inputs
            
        Returns:
            PipelineConfig instance with form values
        """
        return cls(
            domain1=form_data.get('domain1', 'Domain1.csv'),
            domain2=form_data.get('domain2', 'Domain2.csv'),
            domain3=form_data.get('domain3', 'Domain3.csv'),
            max_results=int(form_data.get('max_results', 50)),
            year_start=int(form_data.get('year_start', 2008)),
            year_end=int(form_data.get('year_end')) if form_data.get('year_end') else None,
            email=form_data.get('email'),
            figures_dir=form_data.get('figures_dir', 'figures'),
            report_file=form_data.get('report_file', 'report.md'),
            generate_pdf=form_data.get('generate_pdf', False),
            pandoc_path=form_data.get('pandoc_path'),
            table_file=form_data.get('table_file', 'articles_table.csv'),
            table_format=form_data.get('table_format', 'csv')
        )


class ConfigManager:
    """Manages configuration loading from various sources."""
    
    @staticmethod
    def get_config() -> PipelineConfig:
        """Get configuration from command line arguments.
        
        Returns:
            PipelineConfig: Configuration settings from command line arguments
        """
        parser = argparse.ArgumentParser(
            description='Executes the complete workflow for bibliometric analysis.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        # Add argument groups
        search_group = parser.add_argument_group('Search options')
        ConfigManager._add_search_arguments(search_group)
        
        output_group = parser.add_argument_group('Output options')
        ConfigManager._add_output_arguments(output_group)
        
        flow_group = parser.add_argument_group('Workflow control')
        ConfigManager._add_flow_arguments(flow_group)
        
        args = parser.parse_args()
        return PipelineConfig(**vars(args))
    
    @staticmethod
    def _add_search_arguments(group):
        """Add search-related arguments to argument group."""
        group.add_argument('--domain1', type=str, default='Domain1.csv',
                          help='CSV file with first domain terms')
        group.add_argument('--domain2', type=str, default='Domain2.csv',
                          help='CSV file with second domain terms')
        group.add_argument('--domain3', type=str, default='Domain3.csv',
                          help='CSV file with third domain terms')
        group.add_argument('--max-results', type=int, default=50,
                          help='Maximum results per search')
        group.add_argument('--year-start', type=int, default=2008,
                          help='Start year for filtering results')
        group.add_argument('--year-end', type=int, default=None,
                          help='End year for filtering results')
        group.add_argument('--email', type=str, default=None,
                          help='Email for academic APIs')

    @staticmethod
    def _add_output_arguments(group):
        """Add output-related arguments to argument group."""
        group.add_argument('--figures-dir', type=str, default='figures',
                          help='Directory to save figures')
        group.add_argument('--report-file', type=str, default='report.md',
                          help='Output file for the report')
        group.add_argument('--generate-pdf', action='store_true',
                          help='Generate PDF report')
        group.add_argument('--pandoc-path', type=str, default=None,
                          help='Path to Pandoc executable')
        group.add_argument('--table-file', type=str, default='articles_table.csv',
                          help='File for articles table')
        group.add_argument('--table-format', type=str, choices=['csv', 'excel'],
                          default='csv', help='Format for articles table')

    @staticmethod
    def _add_flow_arguments(group):
        """Add workflow control arguments to argument group."""
        group.add_argument('--skip-searches', action='store_true',
                          help='Skip searches')
        group.add_argument('--skip-integration', action='store_true',
                          help='Skip integration')
        group.add_argument('--skip-domain-analysis', action='store_true',
                          help='Skip domain analysis')
        group.add_argument('--skip-classification', action='store_true',
                          help='Skip classification')
        group.add_argument('--skip-table', action='store_true',
                          help='Skip table generation')
        group.add_argument('--only-search', action='store_true',
                          help='Run only search phase')
        group.add_argument('--only-analysis', action='store_true',
                          help='Run only analysis phase')
        group.add_argument('--only-report', action='store_true',
                          help='Run only report phase')