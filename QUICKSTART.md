# Quick Start Guide

Get up and running with the AI Competitor Intelligence Tracker in 5 minutes.

## Installation (One-Time Setup)

### Option 1: Automated Setup (Recommended)

```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

## Running the Tracker

### Basic Run

```bash
# Activate virtual environment
source venv/bin/activate

# Run the tracker
python src/main.py
```

This will:
1. Scrape all configured competitor sources
2. Process and validate the content
3. Generate reports in `data/reports/`

### With Live Dashboard

```bash
python src/main.py --dashboard
```

Then open your browser to: `http://127.0.0.1:5000`

## What You Get

After running, you'll find reports in `data/reports/`:

- **intelligence_report_YYYYMMDD_HHMMSS.md** - Executive summary (Markdown)
- **intelligence_report_YYYYMMDD_HHMMSS.json** - Structured data (JSON)
- **intelligence_report_YYYYMMDD_HHMMSS.html** - Interactive dashboard (HTML)
- **intelligence_report_YYYYMMDD_HHMMSS.csv** - Spreadsheet export (CSV)

## Customization

### Add More Sources

Edit [config/config.yaml](config/config.yaml):

```yaml
sources:
  tier1:
    - name: "Your Competitor"
      url: "https://competitor.com/blog"
      selectors:
        article: "article"
        title: "h1"
        date: "time"
        content: ".content"
      priority: "critical"
```

### Adjust Scraping Speed

In [config/config.yaml](config/config.yaml):

```yaml
scraping:
  min_delay: 3  # Increase for slower, more respectful scraping
  max_delay: 7
  max_workers: 3  # Reduce for fewer concurrent requests
```

### Change Report Formats

In [config/config.yaml](config/config.yaml):

```yaml
reporting:
  formats:
    - "markdown"  # Executive summary
    - "json"      # API integration
    - "html"      # Interactive dashboard
    - "csv"       # Spreadsheet analysis
```

## Monitoring Sources

### Default Sources (No Configuration Needed)

**Tier 1 - Critical:**
- OpenAI Blog
- Google AI Blog
- Microsoft AI Blog
- Anthropic News

**Tier 2 - High Priority:**
- Meta AI Blog
- DeepMind Blog
- Hugging Face Blog

**Tier 3 - Weekly:**
- TechCrunch AI
- VentureBeat AI

## Troubleshooting

### No articles found?
- CSS selectors may need updating
- Check logs in `logs/competitor_tracker.log`
- Some sites may block automated requests

### Rate limiting errors?
- Increase delays in `config/config.yaml`
- Reduce `max_workers`

### Installation errors?
- Ensure Python 3.8+ is installed: `python3 --version`
- Try: `pip install --upgrade pip`
- On macOS with Apple Silicon: `pip install --no-binary :all: lxml`

## Scheduling (Optional)

### Run Daily with Cron

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/ai-competitor-tracker && /path/to/venv/bin/python src/main.py
```

### Run Weekly

```bash
# Add this line (runs Monday at 9 AM)
0 9 * * 1 cd /path/to/ai-competitor-tracker && /path/to/venv/bin/python src/main.py
```

## Next Steps

1. Review the generated reports in `data/reports/`
2. Customize sources in `config/config.yaml`
3. Set up automated scheduling
4. Integrate with your BI tools using JSON/CSV exports
5. Check `logs/competitor_tracker.log` for detailed execution logs

## Resources

- **Full Documentation:** [README.md](README.md)
- **Configuration Reference:** [config/config.yaml](config/config.yaml)
- **Project Specification:** [Claude.md](Claude.md)

## Support

For issues or questions:
- Check the logs: `logs/competitor_tracker.log`
- Review [README.md](README.md) for detailed documentation
- Open an issue on the repository

---

**Happy Intelligence Gathering!**
