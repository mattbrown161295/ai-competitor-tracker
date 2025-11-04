"""
Content processing pipeline for validation, deduplication, and enrichment.
"""

import hashlib
import re
from typing import List, Dict, Any, Set
from datetime import datetime
from dateutil import parser as date_parser

import feedparser
from loguru import logger


class ContentValidator:
    """Validates scraped content for quality and relevance."""

    def __init__(
        self,
        min_length: int = 100,
        max_length: int = 50000,
        ai_keywords: List[str] = None,
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.ai_keywords = [kw.lower() for kw in (ai_keywords or [])]

    def is_valid(self, article: Dict[str, Any]) -> bool:
        """Check if article meets quality standards."""
        title = article.get("title", "")
        content = article.get("content", "")

        # Check minimum content
        if not title or not content:
            logger.debug("Article rejected: missing title or content")
            return False

        # Check content length
        content_length = len(content)
        if content_length < self.min_length:
            logger.debug(f"Article rejected: content too short ({content_length} chars)")
            return False

        if content_length > self.max_length:
            logger.debug(f"Article rejected: content too long ({content_length} chars)")
            return False

        # Check relevance
        if self.ai_keywords and not self._is_relevant(title, content):
            logger.debug("Article rejected: not relevant to AI/tech keywords")
            return False

        return True

    def _is_relevant(self, title: str, content: str) -> bool:
        """Check if content is relevant based on AI keywords."""
        text = f"{title} {content}".lower()
        return any(keyword in text for keyword in self.ai_keywords)


class DuplicateDetector:
    """Detects duplicate content using content hashing."""

    def __init__(self):
        self.seen_hashes: Set[str] = set()
        self.seen_urls: Set[str] = set()

    def is_duplicate(self, article: Dict[str, Any]) -> bool:
        """Check if article is a duplicate."""
        content_hash = article.get("content_hash")
        url = article.get("link")

        # Check content hash
        if content_hash and content_hash in self.seen_hashes:
            logger.debug(f"Duplicate detected (hash): {article.get('title', '')[:50]}")
            return True

        # Check URL
        if url and url in self.seen_urls:
            logger.debug(f"Duplicate detected (URL): {url}")
            return True

        # Add to seen sets
        if content_hash:
            self.seen_hashes.add(content_hash)
        if url:
            self.seen_urls.add(url)

        return False

    def reset(self):
        """Clear duplicate detection cache."""
        self.seen_hashes.clear()
        self.seen_urls.clear()
        logger.info("Duplicate detector cache cleared")


class DateParser:
    """Intelligent date parsing from various formats."""

    @staticmethod
    def parse_date(date_string: str) -> datetime:
        """Parse date from various formats."""
        if not date_string:
            return datetime.now()

        try:
            # Try dateutil parser first (handles most formats)
            return date_parser.parse(date_string)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse date: {date_string}")
            return datetime.now()

    @staticmethod
    def format_date(dt: datetime, format_str: str = "%Y-%m-%d") -> str:
        """Format datetime to string."""
        return dt.strftime(format_str)


class RSSFeedProcessor:
    """Processes RSS/Atom feeds as alternative to HTML scraping."""

    def __init__(self):
        pass

    def fetch_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed."""
        try:
            logger.info(f"Fetching RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                logger.warning(f"RSS feed parse warning for {feed_url}: {feed.bozo_exception}")

            articles = []
            for entry in feed.entries:
                article = self._parse_feed_entry(entry)
                if article:
                    articles.append(article)

            logger.success(f"Parsed {len(articles)} articles from RSS feed")
            return articles

        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            return []

    def _parse_feed_entry(self, entry) -> Dict[str, Any]:
        """Parse a single RSS feed entry."""
        try:
            # Extract title
            title = entry.get("title", "").strip()

            # Extract content
            content = ""
            if hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "description"):
                content = entry.description
            elif hasattr(entry, "content"):
                content = entry.content[0].value if entry.content else ""

            # Remove HTML tags from content
            content = re.sub(r"<[^>]+>", "", content).strip()

            # Extract link
            link = entry.get("link", "")

            # Extract date
            date = None
            if hasattr(entry, "published_parsed"):
                date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed"):
                date = datetime(*entry.updated_parsed[:6])

            # Generate content hash
            content_hash = hashlib.sha256(f"{title}{content}".encode()).hexdigest()

            return {
                "title": title,
                "content": content,
                "link": link,
                "date": date.isoformat() if date else None,
                "content_hash": content_hash,
            }

        except Exception as e:
            logger.error(f"Error parsing feed entry: {e}")
            return None


class ContentProcessor:
    """Main content processing pipeline."""

    def __init__(self, config: Dict[str, Any]):
        processing_config = config.get("processing", {})

        self.validator = ContentValidator(
            min_length=processing_config.get("min_content_length", 100),
            max_length=processing_config.get("max_content_length", 50000),
            ai_keywords=processing_config.get("ai_keywords", []),
        )

        self.duplicate_detector = DuplicateDetector()
        self.date_parser = DateParser()
        self.rss_processor = RSSFeedProcessor()

    def process_scrape_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process raw scraping results into clean, validated data."""
        logger.info("Starting content processing pipeline")

        all_articles = []
        stats = {
            "total_sources": len(results),
            "successful_sources": 0,
            "failed_sources": 0,
            "total_articles_raw": 0,
            "articles_after_validation": 0,
            "articles_after_deduplication": 0,
            "duplicates_removed": 0,
            "invalid_articles": 0,
        }

        # Reset duplicate detector for fresh processing
        self.duplicate_detector.reset()

        # Process each source
        for result in results:
            source_name = result.get("source")
            status = result.get("status")
            articles = result.get("articles", [])

            if status == "success":
                stats["successful_sources"] += 1
            else:
                stats["failed_sources"] += 1
                logger.warning(f"Source {source_name} failed: {result.get('error', 'Unknown error')}")
                continue

            stats["total_articles_raw"] += len(articles)

            # Process articles from this source
            for article in articles:
                # Add source metadata
                article["source"] = source_name
                article["priority"] = result.get("priority", "medium")

                # Validate
                if not self.validator.is_valid(article):
                    stats["invalid_articles"] += 1
                    continue

                stats["articles_after_validation"] += 1

                # Check for duplicates
                if self.duplicate_detector.is_duplicate(article):
                    stats["duplicates_removed"] += 1
                    continue

                stats["articles_after_deduplication"] += 1

                # Enrich article
                article = self._enrich_article(article)
                all_articles.append(article)

        # Sort articles by priority and date
        all_articles = self._sort_articles(all_articles)

        logger.info(f"Content processing complete. Valid articles: {len(all_articles)}")

        return {"articles": all_articles, "stats": stats, "timestamp": datetime.now().isoformat()}

    def _enrich_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich article with additional metadata."""
        # Parse and standardize date
        if article.get("date"):
            try:
                parsed_date = self.date_parser.parse_date(article["date"])
                article["date_parsed"] = parsed_date.isoformat()
                article["date_formatted"] = self.date_parser.format_date(parsed_date, "%B %d, %Y")
            except Exception as e:
                logger.warning(f"Date enrichment failed: {e}")

        # Add processing timestamp
        article["processed_at"] = datetime.now().isoformat()

        # Truncate content for summary
        content = article.get("content", "")
        if len(content) > 500:
            article["summary"] = content[:500] + "..."
        else:
            article["summary"] = content

        return article

    def _sort_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort articles by priority and date."""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        def sort_key(article):
            priority = priority_order.get(article.get("priority", "medium"), 2)
            date_str = article.get("date_parsed", "")
            return (priority, date_str)

        return sorted(articles, key=sort_key, reverse=True)

    def process_rss_feed(self, feed_url: str, source_name: str) -> List[Dict[str, Any]]:
        """Process RSS feed for a source."""
        articles = self.rss_processor.fetch_feed(feed_url)

        # Add source metadata and process
        processed = []
        for article in articles:
            article["source"] = source_name

            if self.validator.is_valid(article) and not self.duplicate_detector.is_duplicate(article):
                processed.append(self._enrich_article(article))

        return processed
