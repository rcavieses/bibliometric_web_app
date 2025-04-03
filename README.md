# Scientific Literature Analysis Toolkit

A comprehensive toolkit for searching, analyzing, and visualizing scientific literature across multiple academic databases with AI-powered classification. Now with a Streamlit web interface and Firebase integration.

## Overview

This project provides an end-to-end pipeline for:

1. Searching for scientific articles across multiple databases (Crossref, Semantic Scholar, Science Direct)
2. Integrating and deduplicating search results
3. Analyzing domain-specific terms and relevance
4. Classifying articles using AI (Claude via Anthropic API)
5. Generating visualizations and statistics
6. Creating comprehensive Markdown/PDF reports

The toolkit is designed for bibliometric analysis and systematic literature reviews, with a focus on multi-domain searches (e.g., articles that mention both AI/ML methods and specific application domains like fisheries).

## Directory Structure

```
root/
├── data/                          # Data files
│   ├── raw/                       # Raw input data
│   │   ├── Domain1.csv            # Terms for first domain
│   │   ├── Domain2.csv            # Terms for second domain
│   │   └── Domain3.csv            # Terms for third domain (optional)
│   ├── processed/                 # Processed data
│   ├── output/                    # Final outputs
│   └── questions.json             # Classification questions for Claude
├── secrets/                       # API keys (gitignored)
│   ├── anthropic-apikey           # Anthropic API key
│   ├── firebase_credentials.json  # Firebase credentials
│   └── sciencedirect_apikey.txt   # Science Direct API key
├── src/                           # Source code
│   ├── core/                      # Core components
│   │   ├── config_manager.py      # Configuration management
│   │   ├── logger.py              # Logging setup
│   │   ├── phase_runner.py        # Phase implementations
│   │   └── pipeline_executor.py   # Pipeline management
│   ├── search/                    # Search modules
│   │   ├── crossref_search.py     # Search Crossref
│   │   ├── semantic_scholar_search.py # Search Semantic Scholar
│   │   ├── science_direct_search.py # Search Science Direct
│   │   ├── google_scholar_scraper.py # Google Scholar search
│   │   └── integrated_search.py   # Combine and deduplicate results
│   ├── analysis/                  # Analysis modules
│   │   ├── domain_analysis.py     # Analyze domain term frequency
│   │   ├── nlp_classifier_anthropic.py # Classify using Claude API
│   │   ├── analysis_generator.py  # Generate visualizations
│   │   ├── report_generator.py    # Create reports
│   │   ├── export_articles_table.py # Export article data
│   │   └── cross_domain.py        # Cross-domain analysis
│   ├── utils/                     # Utility functions
│   │   └── text_normalizer.py     # Text normalization
│   ├── cli/                       # Command-line interfaces
│   │   ├── master_script.py       # Main CLI
│   │   └── pipeline_executor_main.py # Pipeline executor
│   └── web/                       # Web interface
│       ├── streamlit_app.py       # Streamlit web app
│       ├── init_firebase.py       # Firebase initialization
│       ├── Dockerfile             # Docker configuration
│       ├── docker-compose.yml     # Docker Compose configuration
│       └── README.md              # Web app documentation
├── docs/                          # Documentation
│   ├── guides/                    # User guides
│   ├── api/                       # API documentation
│   └── pipeline_chart.md          # Pipeline documentation
├── figures/                       # Generated visualizations
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── setup.py                       # Package setup
├── requirements.txt               # Dependencies
└── README.md                      # Project overview
```

## Installation

### Command-Line Tool

```bash
# Install the package and dependencies
pip install -e .
```

### Web Application

The web application uses Streamlit and Firebase. See `src/web/README.md` for detailed setup instructions.

```bash
# Install required packages
pip install -r requirements.txt

# Initialize Firebase (after setting up Firebase project)
python src/web/init_firebase.py --admin-email your@email.com --admin-password password --admin-name "Admin User"

# Run the Streamlit app
streamlit run src/web/streamlit_app.py
```

## Prerequisites

### Python Dependencies

- Python 3.8+
- See `requirements.txt` for all dependencies

### API Keys

1. **Science Direct API Key** (optional): For accessing Science Direct/Scopus
   - Create file `secrets/sciencedirect_apikey.txt` with your API key
   
2. **Anthropic API Key**: For Claude classification
   - Create file `secrets/anthropic-apikey` with your API key
   - Create an account at [anthropic.com](https://anthropic.com/) if needed

3. **Firebase** (for web application):
   - Create a Firebase project
   - Save service account credentials as `secrets/firebase_credentials.json`

## Usage

### Command-Line Interface

```bash
# Run the full pipeline
python -m src.cli.pipeline_executor_main --domain1 data/raw/Domain1.csv --domain2 data/raw/Domain2.csv --max-results 100

# Run specific phases
python -m src.cli.pipeline_executor_main --only-search
python -m src.cli.pipeline_executor_main --only-analysis
python -m src.cli.pipeline_executor_main --only-report --generate-pdf
```

### Web Interface

The web interface provides a user-friendly way to interact with the bibliometric analysis toolkit:

1. **User Authentication**: Secure login and registration
2. **Search Configuration**: Configure search parameters through a simple form
3. **Results Visualization**: Interactive charts and visualizations
4. **Profile Management**: View and edit user profiles
5. **API Key Management**: Centralized API key storage

To run the web application:

```bash
streamlit run src/web/streamlit_app.py
```

Or using Docker:

```bash
cd src/web
docker-compose up -d
```

## Command-Line Options

```
--domain1 FILE        CSV file with terms for domain 1 (default: data/raw/Domain1.csv)
--domain2 FILE        CSV file with terms for domain 2 (default: data/raw/Domain2.csv)
--domain3 FILE        CSV file with terms for domain 3 (default: data/raw/Domain3.csv)
--max-results N       Maximum results per source (default: 100)
--year-start YEAR     Filter by start year (default: 2008)
--year-end YEAR       Filter by end year (default: None)
--email EMAIL         Email for Crossref API
--only-search         Run only search phase
--only-analysis       Run only analysis phase
--only-report         Run only report phase
--generate-pdf        Generate PDF report (requires Pandoc)
```

## Example Output

The toolkit generates various visualizations:

- Publication trends over time
- Domain distribution
- Source distribution
- Top journals and authors
- Topic co-occurrence matrix
- Word clouds of key terms
- Collaboration networks
- Citations analysis

Reports are generated in Markdown format with optional PDF conversion.

## License

This project is provided for academic and research purposes.

## Troubleshooting

### Common Issues

- **API connection failures**: Check internet connection and API key validity
- **Missing dependencies**: Ensure all required packages are installed
- **PDF generation fails**: Verify Pandoc is installed and accessible
- **Firebase authentication issues**: Verify Firebase credentials and configuration

For additional support or to report issues, please open an issue on the repository.