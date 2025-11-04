"""
Main entry point for the AI Competitor Intelligence Tracker.
Orchestrates scraping, processing, and reporting.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.scraper import CompetitorScraper
from src.processors.content_processor import ContentProcessor
from src.reporters.report_generator import ReportGenerator
from src.utils.config_loader import load_config
from src.utils.logger_setup import setup_logging, get_logger


class CompetitorIntelligence:
    """Main orchestrator for competitive intelligence gathering."""

    def __init__(self, config_path: str = "config/config.yaml"):
        # Load configuration
        self.config = load_config(config_path)

        # Setup logging
        setup_logging(self.config)
        self.logger = get_logger()

        # Initialize components
        self.scraper = CompetitorScraper(self.config)
        self.processor = ContentProcessor(self.config)
        self.reporter = ReportGenerator(self.config)

        self.logger.info("AI Competitor Intelligence Tracker initialized")

    def execute_intelligence_gathering(self):
        """Execute the complete intelligence gathering pipeline."""
        self.logger.info("=" * 80)
        self.logger.info("STARTING COMPETITIVE INTELLIGENCE GATHERING")
        self.logger.info("=" * 80)

        try:
            # Step 1: Scrape all sources
            self.logger.info("STEP 1: Scraping competitor sources...")
            scrape_results = self.scraper.scrape_all()
            self.logger.success(f"Scraping complete. Results from {len(scrape_results)} sources")

            # Step 2: Process and validate content
            self.logger.info("STEP 2: Processing and validating content...")
            processed_data = self.processor.process_scrape_results(scrape_results)
            self.logger.success(
                f"Processing complete. {len(processed_data['articles'])} valid articles"
            )

            # Step 3: Generate reports
            self.logger.info("STEP 3: Generating reports...")
            report_files = self.reporter.generate_reports(processed_data)
            self.logger.success(f"Reports generated: {len(report_files)} formats")

            # Display summary
            self._display_summary(processed_data, report_files)

            # Cleanup
            self.scraper.cleanup()

            self.logger.info("=" * 80)
            self.logger.info("INTELLIGENCE GATHERING COMPLETE")
            self.logger.info("=" * 80)

            return {
                "status": "success",
                "articles": processed_data["articles"],
                "stats": processed_data["stats"],
                "reports": report_files,
            }

        except Exception as e:
            self.logger.error(f"Intelligence gathering failed: {e}")
            self.logger.exception("Full traceback:")
            return {"status": "failed", "error": str(e)}

    def _display_summary(self, data: dict, report_files: dict):
        """Display execution summary."""
        stats = data.get("stats", {})
        articles = data.get("articles", [])

        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("EXECUTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Sources Monitored: {stats.get('successful_sources', 0)}/{stats.get('total_sources', 0)}")
        self.logger.info(f"Raw Articles: {stats.get('total_articles_raw', 0)}")
        self.logger.info(f"After Validation: {stats.get('articles_after_validation', 0)}")
        self.logger.info(f"After Deduplication: {stats.get('articles_after_deduplication', 0)}")
        self.logger.info(f"Duplicates Removed: {stats.get('duplicates_removed', 0)}")
        self.logger.info(f"Invalid Articles: {stats.get('invalid_articles', 0)}")
        self.logger.info("")
        self.logger.info("Generated Reports:")
        for format_name, file_path in report_files.items():
            self.logger.info(f"  - {format_name.upper()}: {file_path}")
        self.logger.info("=" * 80)

        # Show top articles
        if articles:
            self.logger.info("")
            self.logger.info("TOP 5 ARTICLES:")
            self.logger.info("-" * 80)
            for i, article in enumerate(articles[:5], 1):
                self.logger.info(f"{i}. [{article.get('source')}] {article.get('title', 'No title')}")
                self.logger.info(f"   Priority: {article.get('priority', 'N/A')} | Link: {article.get('link', 'N/A')}")
            self.logger.info("-" * 80)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Competitor Intelligence Tracker - Enterprise-grade competitive monitoring"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file (default: config/config.yaml)",
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Launch web dashboard after gathering intelligence",
    )

    args = parser.parse_args()

    # Initialize and run
    tracker = CompetitorIntelligence(config_path=args.config)
    result = tracker.execute_intelligence_gathering()

    # Launch dashboard if requested
    if args.dashboard and result["status"] == "success":
        print("\n" + "=" * 80)
        print("Launching enhanced web dashboard...")
        print("=" * 80)
        from src.dashboard.enhanced_app import launch_dashboard

        launch_dashboard(tracker.config, result)

    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
