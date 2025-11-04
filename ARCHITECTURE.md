# System Architecture

## Overview

The AI Competitor Intelligence Tracker is built with a modular, enterprise-grade architecture designed for reliability, scalability, and maintainability.

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MAIN ORCHESTRATOR                           │
│                         (src/main.py)                               │
│                   CompetitorIntelligence Class                      │
└────────────┬────────────────────────────────────────┬───────────────┘
             │                                        │
             │ 1. Scrape                             │ Config
             │                                        │
             ▼                                        ▼
┌─────────────────────────────────┐    ┌──────────────────────────────┐
│     SCRAPING ENGINE             │    │   CONFIGURATION LOADER       │
│     (src/core/scraper.py)       │    │   (src/utils/config_loader.py)│
│                                 │    │                              │
│  ┌──────────────────────────┐  │    │  • Load config.yaml          │
│  │   SessionManager         │  │    │  • Apply .env overrides      │
│  │   - HTTP sessions        │  │    │  • Validate settings         │
│  │   - User-agent rotation  │  │    └──────────────────────────────┘
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │   RateLimiter            │  │
│  │   - Per-domain delays    │  │
│  │   - Random intervals     │  │
│  └──────────────────────────┘  │
│                                 │    ┌──────────────────────────────┐
│  ┌──────────────────────────┐  │    │   LOGGING SYSTEM             │
│  │   ContentFetcher         │  │───▶│   (src/utils/logger_setup.py)│
│  │   - HTTP requests        │  │    │                              │
│  │   - Retry logic          │  │    │  • Console output            │
│  │   - Error handling       │  │    │  • File rotation             │
│  └──────────────────────────┘  │    │  • Structured logging        │
│                                 │    └──────────────────────────────┘
│  ┌──────────────────────────┐  │
│  │   HTMLParser             │  │
│  │   - CSS selectors        │  │
│  │   - Content extraction   │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │   CompetitorScraper      │  │
│  │   - Multi-threaded       │  │
│  │   - Source orchestration │  │
│  └──────────────────────────┘  │
└────────────┬────────────────────┘
             │
             │ Raw Articles
             │
             ▼
┌─────────────────────────────────┐
│     PROCESSING PIPELINE         │
│  (src/processors/               │
│   content_processor.py)         │
│                                 │
│  ┌──────────────────────────┐  │
│  │   ContentValidator       │  │
│  │   - Quality checks       │  │
│  │   - Relevance filtering  │  │
│  │   - Length validation    │  │
│  └──────────────────────────┘  │
│              │                  │
│              ▼                  │
│  ┌──────────────────────────┐  │
│  │   DuplicateDetector      │  │
│  │   - Content hashing      │  │
│  │   - URL deduplication    │  │
│  └──────────────────────────┘  │
│              │                  │
│              ▼                  │
│  ┌──────────────────────────┐  │
│  │   DateParser             │  │
│  │   - Format standardization│ │
│  │   - Intelligent parsing  │  │
│  └──────────────────────────┘  │
│              │                  │
│              ▼                  │
│  ┌──────────────────────────┐  │
│  │   RSSFeedProcessor       │  │
│  │   - RSS/Atom fallback    │  │
│  │   - Feed parsing         │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │   ContentProcessor       │  │
│  │   - Pipeline coordinator │  │
│  │   - Enrichment           │  │
│  └──────────────────────────┘  │
└────────────┬────────────────────┘
             │
             │ Processed Articles + Stats
             │
             ▼
┌─────────────────────────────────┐
│     REPORT GENERATION           │
│  (src/reporters/                │
│   report_generator.py)          │
│                                 │
│  ┌──────────────────────────┐  │
│  │ MarkdownReportGenerator  │  │──▶ intelligence_report.md
│  │ - Executive summary      │  │
│  │ - Competitor analysis    │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │  JSONReportGenerator     │  │──▶ intelligence_report.json
│  │  - Structured data       │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │  HTMLReportGenerator     │  │──▶ intelligence_report.html
│  │  - Interactive dashboard │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │  CSVReportGenerator      │  │──▶ intelligence_report.csv
│  │  - Spreadsheet export    │  │
│  └──────────────────────────┘  │
└────────────┬────────────────────┘
             │
             │ Report Files
             │
             ▼
┌─────────────────────────────────┐
│     LIVE DASHBOARD              │
│  (src/dashboard/app.py)         │
│                                 │
│  ┌──────────────────────────┐  │
│  │   Flask Application      │  │
│  │   - Real-time viewing    │  │
│  │   - Auto-refresh         │  │
│  │   - Interactive UI       │  │
│  └──────────────────────────┘  │
│                                 │
│  Routes:                        │
│  • GET / - Main dashboard       │
│  • GET /health - Health check   │
└─────────────────────────────────┘
```

## Component Responsibilities

### 1. Main Orchestrator (`src/main.py`)
- **Purpose:** Coordinates the entire intelligence gathering process
- **Key Classes:** `CompetitorIntelligence`
- **Responsibilities:**
  - Initialize all components
  - Execute 3-step pipeline (Scrape → Process → Report)
  - Handle command-line arguments
  - Display execution summary
  - Launch optional web dashboard

### 2. Scraping Engine (`src/core/scraper.py`)
- **Purpose:** Fetch content from competitor websites
- **Key Classes:**
  - `SessionManager` - Manages HTTP sessions with rotation
  - `RateLimiter` - Enforces respectful crawling delays
  - `ContentFetcher` - Handles requests with retry logic
  - `HTMLParser` - Extracts structured data from HTML
  - `CompetitorScraper` - Orchestrates multi-threaded scraping

### 3. Processing Pipeline (`src/processors/content_processor.py`)
- **Purpose:** Validate, deduplicate, and enrich scraped content
- **Key Classes:**
  - `ContentValidator` - Quality and relevance checks
  - `DuplicateDetector` - Content fingerprinting
  - `DateParser` - Intelligent date parsing
  - `RSSFeedProcessor` - RSS/Atom feed handling
  - `ContentProcessor` - Pipeline coordinator

### 4. Report Generation (`src/reporters/report_generator.py`)
- **Purpose:** Generate executive reports in multiple formats
- **Key Classes:**
  - `MarkdownReportGenerator` - Executive-style markdown
  - `JSONReportGenerator` - Structured data export
  - `HTMLReportGenerator` - Interactive dashboards
  - `CSVReportGenerator` - Spreadsheet exports
  - `ReportGenerator` - Format coordinator

### 5. Web Dashboard (`src/dashboard/app.py`)
- **Purpose:** Provide live visualization of intelligence data
- **Key Functions:**
  - `create_app()` - Flask app factory
  - `launch_dashboard()` - Server launcher

### 6. Utilities (`src/utils/`)
- **Purpose:** Configuration and logging infrastructure
- **Modules:**
  - `config_loader.py` - YAML and environment variable loading
  - `logger_setup.py` - Structured logging with rotation

## Execution Flow

### Standard Execution
```
1. Load Configuration (config.yaml + .env)
2. Setup Logging (console + file)
3. Initialize Components (scraper, processor, reporter)
4. Execute Scraping (multi-threaded, with rate limiting)
5. Process Content (validate → deduplicate → enrich)
6. Generate Reports (markdown, json, html, csv)
7. Display Summary (stats + top articles)
8. Cleanup Resources (close sessions)
```

### Dashboard Execution
```
1-7. Same as Standard Execution
8. Launch Flask Server (http://127.0.0.1:5000)
9. Auto-refresh every 5 minutes
10. Serve Real-time Dashboard
```

## Concurrency Model

### Multi-threaded Scraping
- Uses `ThreadPoolExecutor` for concurrent requests
- Configurable worker pool size (`max_workers`)
- Per-domain rate limiting prevents overwhelming sources
- Error isolation ensures one failure doesn't stop others

### Thread-Safe Components
- `SessionManager` - Separate session per domain
- `RateLimiter` - Domain-specific timing
- `DuplicateDetector` - Thread-safe hash sets

## Error Handling Strategy

### Graceful Degradation
```
Source A Success ────┐
                     │
Source B Fails ──────┤──▶ Continue with available data
                     │
Source C Success ────┘
```

### Retry Logic
```
Request Failed
    │
    ├─ Retry 1 (2s delay)
    │   └─ Retry 2 (4s delay)
    │       └─ Retry 3 (8s delay)
    │           └─ Mark as failed, continue
```

### Fallback Mechanisms
1. HTML scraping fails → Try RSS feed
2. Primary selector fails → Try secondary selector
3. Individual source fails → Continue with other sources
4. Entire scraping fails → Log error, exit gracefully

## Data Storage

### Directory Structure
```
data/
├── raw/              # Optional: Raw HTML/XML (not currently used)
├── processed/        # Content cache (duplicate detection)
└── reports/          # Generated reports
    ├── intelligence_report_YYYYMMDD_HHMMSS.md
    ├── intelligence_report_YYYYMMDD_HHMMSS.json
    ├── intelligence_report_YYYYMMDD_HHMMSS.html
    └── intelligence_report_YYYYMMDD_HHMMSS.csv
```

### Logs
```
logs/
└── competitor_tracker.log     # Rotating logs (100MB, 30 days retention)
```

## Configuration Management

### Hierarchy
```
1. Default values (in code)
2. config.yaml (file-based config)
3. .env (environment variables)
4. Command-line arguments (highest priority)
```

### Hot-Reloadable Settings
- User agents list
- Rate limiting parameters
- Target sources
- CSS selectors
- Report formats
- Dashboard settings

## Security Considerations

### Respectful Scraping
- Honors robots.txt (configurable)
- Implements rate limiting (2-5s delays)
- Uses realistic user agents
- Session management prevents detection

### Data Privacy
- No credentials stored in code
- Environment variables for sensitive data
- Logs exclude sensitive information
- Reports contain only public data

## Performance Characteristics

### Typical Execution Times
- Single source: 10-30 seconds
- All 10 sources: 2-5 minutes (parallel)
- Report generation: <5 seconds
- Dashboard launch: <2 seconds

### Resource Usage
- Memory: ~100-200 MB
- CPU: Moderate (multi-threaded)
- Disk: Reports ~1-5 MB each
- Network: Respectful (rate-limited)

## Extension Points

### Adding New Sources
1. Edit `config/config.yaml`
2. Add source with selectors
3. No code changes required

### Adding New Report Formats
1. Create new generator class
2. Implement `generate()` method
3. Register in `ReportGenerator`

### Custom Processing
1. Add processor to `content_processor.py`
2. Integrate in `ContentProcessor.process_scrape_results()`

### Dashboard Customization
1. Modify `DASHBOARD_TEMPLATE` in `app.py`
2. Add new Flask routes as needed

---

**Architecture designed for enterprise reliability and developer extensibility.**
