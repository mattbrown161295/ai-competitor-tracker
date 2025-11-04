# AI Competitor Intelligence Tracker

Enterprise-grade competitive intelligence system for monitoring the AI industry landscape. Built with professional web scraping techniques, intelligent rate limiting, and comprehensive reporting capabilities.

## Features

- **Multi-threaded Web Scraping** - Concurrent request handling for efficient data collection
- **Intelligent Rate Limiting** - Per-domain rate limits with randomized delays
- **Anti-Detection Mechanisms** - User-agent rotation, session management, and retry logic
- **RSS Feed Support** - Fallback to RSS feeds when available
- **Content Validation** - Quality assurance and relevance filtering
- **Duplicate Detection** - Content fingerprinting to avoid processing duplicates
- **Multi-Format Reports** - Markdown, JSON, HTML, and CSV outputs
- **Live Web Dashboard** - Real-time visualization of intelligence data
- **Professional Logging** - Structured logging with rotation and retention

## Architecture

```
ai-competitor-tracker/
├── src/
│   ├── core/              # Core scraping engine
│   │   └── scraper.py     # SessionManager, RateLimiter, ContentFetcher
│   ├── processors/        # Data processing pipeline
│   │   └── content_processor.py  # Validation, deduplication, enrichment
│   ├── reporters/         # Report generation
│   │   └── report_generator.py   # Multi-format output generators
│   ├── dashboard/         # Web dashboard
│   │   └── app.py         # Flask application
│   ├── utils/             # Utilities
│   │   ├── config_loader.py
│   │   └── logger_setup.py
│   └── main.py            # Main entry point
├── config/
│   └── config.yaml        # Configuration file
├── data/
│   ├── raw/              # Raw scraped data
│   ├── processed/        # Processed cache
│   └── reports/          # Generated reports
├── logs/                  # Application logs
└── tests/                 # Unit tests
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   cd ai-competitor-tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers** (optional, for headless browser fallback)
   ```bash
   playwright install
   ```

5. **Configure the application**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Configuration

Edit [config/config.yaml](config/config.yaml) to customize:

- **Target sources** - Add or modify competitor websites to monitor
- **Scraping behavior** - Rate limits, timeouts, user agents
- **Content processing** - Validation rules, AI keywords for relevance
- **Report formats** - Enable/disable output formats
- **Dashboard settings** - Host, port, auto-refresh interval

## Usage

### Basic Usage

Run the intelligence gathering system:

```bash
python src/main.py
```

### With Dashboard

Launch with live web dashboard:

```bash
python src/main.py --dashboard
```

Then open your browser to `http://127.0.0.1:5000`

### Custom Configuration

Use a custom configuration file:

```bash
python src/main.py --config /path/to/config.yaml
```

### Command-Line Options

```
usage: main.py [-h] [--config CONFIG] [--dashboard]

AI Competitor Intelligence Tracker

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  Path to configuration file (default: config/config.yaml)
  --dashboard      Launch web dashboard after gathering intelligence
```

## Monitored Sources

### Tier 1 - Primary Competitors (Critical Monitoring)
- OpenAI Blog
- Google AI Blog
- Microsoft AI Blog
- Anthropic News

### Tier 2 - Market Players (Regular Monitoring)
- Meta AI Blog
- DeepMind Blog
- Hugging Face Blog
- Cohere, Stability AI, Runway

### Tier 3 - Industry Intelligence (Weekly Monitoring)
- TechCrunch AI
- VentureBeat AI
- The Information
- ArXiv AI Papers

## Output Reports

Reports are generated in multiple formats:

### Markdown Report
Executive-style summary with:
- Executive summary with key metrics
- Critical developments section
- Competitor analysis by source
- Data quality metrics

Location: `data/reports/intelligence_report_YYYYMMDD_HHMMSS.md`

### JSON Report
Structured data for programmatic access:
```json
{
  "articles": [...],
  "stats": {...},
  "timestamp": "2024-01-15T10:30:00"
}
```

Location: `data/reports/intelligence_report_YYYYMMDD_HHMMSS.json`

### HTML Dashboard
Interactive web page with:
- Visual metrics cards
- Sortable article lists
- Priority indicators
- Clickable links

Location: `data/reports/intelligence_report_YYYYMMDD_HHMMSS.html`

### CSV Export
Spreadsheet-friendly format for Excel/Google Sheets analysis.

Location: `data/reports/intelligence_report_YYYYMMDD_HHMMSS.csv`

## Development

### Project Structure

- **Core Scraping** ([src/core/scraper.py](src/core/scraper.py))
  - `SessionManager` - HTTP session management with rotation
  - `RateLimiter` - Per-domain rate limiting
  - `ContentFetcher` - Request handling with retry logic
  - `HTMLParser` - Content extraction with CSS selectors
  - `CompetitorScraper` - Main orchestration

- **Content Processing** ([src/processors/content_processor.py](src/processors/content_processor.py))
  - `ContentValidator` - Quality and relevance validation
  - `DuplicateDetector` - Content fingerprinting
  - `DateParser` - Intelligent date parsing
  - `RSSFeedProcessor` - RSS/Atom feed handling
  - `ContentProcessor` - Main processing pipeline

- **Report Generation** ([src/reporters/report_generator.py](src/reporters/report_generator.py))
  - `MarkdownReportGenerator` - Executive markdown reports
  - `JSONReportGenerator` - Structured JSON output
  - `HTMLReportGenerator` - Interactive dashboards
  - `CSVReportGenerator` - Spreadsheet exports

### Adding New Sources

Edit [config/config.yaml](config/config.yaml) and add to the appropriate tier:

```yaml
sources:
  tier1:
    - name: "New Competitor"
      url: "https://example.com/blog"
      rss: "https://example.com/feed.xml"  # Optional
      selectors:
        article: "article.post"
        title: "h1"
        date: "time"
        content: ".content"
      priority: "critical"
```

### Running Tests

```bash
pytest tests/ -v
```

## Best Practices

### Respectful Scraping

This system implements industry best practices:
- Honors robots.txt directives
- Implements rate limiting (2-5 second delays)
- Uses realistic user agents
- Includes retry logic with exponential backoff
- Prefers RSS feeds when available

### Error Handling

The system gracefully handles:
- Network timeouts
- HTTP errors (403, 429, 500+)
- HTML structure changes
- Content validation failures
- Individual source failures don't stop the entire run

### Performance

- Multi-threaded scraping (configurable workers)
- Concurrent request handling
- Content caching to avoid re-processing
- Efficient duplicate detection

## Troubleshooting

### "Connection refused" errors
- Check your internet connection
- Verify target websites are accessible
- Some sites may block automated requests

### "No articles found"
- CSS selectors may need updating
- Check logs for parsing errors
- Try RSS feed if available

### High memory usage
- Reduce `max_workers` in config
- Decrease number of monitored sources
- Enable content length limits

### Rate limiting issues
- Increase `min_delay` and `max_delay`
- Reduce `max_workers`
- Check site-specific rate limit policies

## Logging

Logs are stored in [logs/competitor_tracker.log](logs/competitor_tracker.log)

Log levels:
- **DEBUG** - Detailed information for diagnosing problems
- **INFO** - General informational messages
- **WARNING** - Warning messages
- **ERROR** - Error messages
- **SUCCESS** - Successful operation completions

## License

This project is provided as-is for educational and business intelligence purposes. Ensure compliance with target websites' terms of service and robots.txt policies.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues, questions, or feature requests, please open an issue on the repository.

---

**Built with enterprise-grade reliability for professional competitive intelligence.**