"""Configuration manager for bibliometric web application."""

__all__ = ['PipelineConfig']

from dataclasses import dataclass
from typing import Optional

@dataclass
class PipelineConfig:
    # Search settings
    domain1: str
    domain2: str
    domain3: str
    max_results: int
    year_start: int
    year_end: Optional[int]
    email: Optional[str] = None
    
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

    @classmethod
    def create_from_form(cls, form_data: dict) -> 'PipelineConfig':
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
            table_format=form_data.get('table_format', 'csv'),
            skip_searches=form_data.get('skip_searches', False),
            skip_integration=form_data.get('skip_integration', False),
            skip_domain_analysis=form_data.get('skip_domain_analysis', False),
            skip_classification=form_data.get('skip_classification', False),
            skip_table=form_data.get('skip_table', False),
            only_search=form_data.get('only_search', False),
            only_analysis=form_data.get('only_analysis', False),
            only_report=form_data.get('only_report', False),
        )