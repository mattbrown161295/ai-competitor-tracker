"""
Core scraping engine with multi-threaded capabilities,
intelligent rate limiting, and anti-detection mechanisms.
"""

import time
import random
import hashlib
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


class SessionManager:
    """Manages HTTP sessions with rotation and persistence."""

    def __init__(self, user_agents: List[str]):
        self.user_agents = user_agents
        self.sessions: Dict[str, requests.Session] = {}

    def get_session(self, domain: str) -> requests.Session:
        """Get or create a session for a specific domain."""
        if domain not in self.sessions:
            session = requests.Session()
            session.headers.update(self._get_random_headers())
            self.sessions[domain] = session
            logger.debug(f"Created new session for domain: {domain}")
        return self.sessions[domain]

    def _get_random_headers(self) -> Dict[str, str]:
        """Generate randomized request headers."""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def rotate_user_agent(self, domain: str):
        """Rotate the user agent for a specific domain."""
        if domain in self.sessions:
            self.sessions[domain].headers["User-Agent"] = random.choice(self.user_agents)
            logger.debug(f"Rotated user agent for domain: {domain}")

    def close_all(self):
        """Close all active sessions."""
        for session in self.sessions.values():
            session.close()
        self.sessions.clear()
        logger.info("All sessions closed")


class RateLimiter:
    """Implements intelligent rate limiting with per-domain tracking."""

    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time: Dict[str, float] = {}

    def wait(self, domain: str):
        """Wait before making a request to respect rate limits."""
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            delay = random.uniform(self.min_delay, self.max_delay)
            wait_time = max(0, delay - elapsed)
            if wait_time > 0:
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s for {domain}")
                time.sleep(wait_time)

        self.last_request_time[domain] = time.time()


class ContentFetcher:
    """Handles HTTP requests with retry logic and error handling."""

    def __init__(
        self,
        session_manager: SessionManager,
        rate_limiter: RateLimiter,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
        self.timeout = timeout
        self.max_retries = max_retries

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def fetch(self, url: str) -> Optional[str]:
        """Fetch content from a URL with retry logic."""
        domain = urlparse(url).netloc

        try:
            # Apply rate limiting
            self.rate_limiter.wait(domain)

            # Get session and make request
            session = self.session_manager.get_session(domain)
            logger.info(f"Fetching: {url}")

            response = session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()

            logger.success(f"Successfully fetched: {url} (Status: {response.status_code})")
            return response.text

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {url}: {e}")
            if e.response.status_code == 429:
                logger.warning(f"Rate limited by {domain}, increasing delay")
                time.sleep(10)
            raise

        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching {url}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None


class HTMLParser:
    """Parses HTML content and extracts structured data."""

    def __init__(self, selectors: Dict[str, str]):
        self.selectors = selectors

    def parse(self, html_content: str, source_url: str) -> List[Dict[str, Any]]:
        """Parse HTML and extract articles using configured selectors."""
        soup = BeautifulSoup(html_content, "lxml")
        articles = []

        # Find all article elements
        article_selector = self.selectors.get("article", "article")
        article_elements = soup.select(article_selector)

        logger.info(f"Found {len(article_elements)} articles using selector: {article_selector}")

        for idx, article_elem in enumerate(article_elements):
            try:
                article_data = self._extract_article_data(article_elem, source_url)
                if article_data:
                    articles.append(article_data)
            except Exception as e:
                logger.error(f"Error parsing article {idx} from {source_url}: {e}")
                continue

        return articles

    def _extract_article_data(self, element: BeautifulSoup, source_url: str) -> Optional[Dict[str, Any]]:
        """Extract data from a single article element."""
        # Extract title
        title_elem = element.select_one(self.selectors.get("title", "h1, h2"))
        title = title_elem.get_text(strip=True) if title_elem else None

        if not title:
            return None

        # Extract date
        date_elem = element.select_one(self.selectors.get("date", "time"))
        date = date_elem.get("datetime") or date_elem.get_text(strip=True) if date_elem else None

        # Extract content/summary
        content_selector = self.selectors.get("content", "p")
        content_elems = element.select(content_selector)
        content = " ".join([p.get_text(strip=True) for p in content_elems[:3]])  # First 3 paragraphs

        # Extract link
        link_elem = element.find("a", href=True)
        link = link_elem["href"] if link_elem else source_url

        # Make link absolute if relative
        if link.startswith("/"):
            from urllib.parse import urljoin
            link = urljoin(source_url, link)

        # Generate content hash for deduplication
        content_hash = hashlib.sha256(f"{title}{content}".encode()).hexdigest()

        return {
            "title": title,
            "date": date,
            "content": content,
            "link": link,
            "source_url": source_url,
            "content_hash": content_hash,
        }


class CompetitorScraper:
    """Main scraper class orchestrating the intelligence gathering."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        scraping_config = config.get("scraping", {})

        # Initialize components
        self.session_manager = SessionManager(scraping_config.get("user_agents", []))
        self.rate_limiter = RateLimiter(
            min_delay=scraping_config.get("min_delay", 2),
            max_delay=scraping_config.get("max_delay", 5),
        )
        self.content_fetcher = ContentFetcher(
            self.session_manager,
            self.rate_limiter,
            timeout=scraping_config.get("request_timeout", 30),
            max_retries=scraping_config.get("max_retries", 3),
        )

        self.max_workers = scraping_config.get("max_workers", 5)
        self.sources = self._load_sources()

    def _load_sources(self) -> List[Dict[str, Any]]:
        """Load all sources from configuration."""
        sources = []
        sources_config = self.config.get("sources", {})

        for tier in ["tier1", "tier2", "tier3"]:
            tier_sources = sources_config.get(tier, [])
            sources.extend(tier_sources)

        logger.info(f"Loaded {len(sources)} sources from configuration")
        return sources

    def scrape_source(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape a single source and return structured data."""
        name = source.get("name")
        url = source.get("url")

        logger.info(f"Starting scrape for {name}: {url}")

        try:
            # Try RSS feed first if available
            rss_url = source.get("rss")
            if rss_url:
                logger.info(f"Attempting RSS feed for {name}: {rss_url}")
                # RSS parsing will be implemented in processors module

            # Fetch HTML content
            html_content = self.content_fetcher.fetch(url)

            if not html_content:
                return {"source": name, "status": "failed", "articles": [], "error": "No content fetched"}

            # Parse HTML
            parser = HTMLParser(source.get("selectors", {}))
            articles = parser.parse(html_content, url)

            logger.success(f"Scraped {len(articles)} articles from {name}")

            return {
                "source": name,
                "status": "success",
                "articles": articles,
                "url": url,
                "priority": source.get("priority", "medium"),
            }

        except Exception as e:
            logger.error(f"Failed to scrape {name}: {e}")
            return {"source": name, "status": "failed", "articles": [], "error": str(e)}

    def scrape_all(self) -> List[Dict[str, Any]]:
        """Scrape all configured sources concurrently."""
        logger.info(f"Starting concurrent scraping of {len(self.sources)} sources")
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_source = {executor.submit(self.scrape_source, source): source for source in self.sources}

            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Exception for {source.get('name')}: {e}")
                    results.append({"source": source.get("name"), "status": "error", "articles": [], "error": str(e)})

        logger.info(f"Completed scraping. Total results: {len(results)}")
        return results

    def cleanup(self):
        """Cleanup resources."""
        self.session_manager.close_all()
        logger.info("Scraper cleanup completed")
