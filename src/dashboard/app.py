"""
Flask-based web dashboard for real-time intelligence viewing.
"""

from flask import Flask, render_template_string, jsonify
from typing import Dict, Any
from datetime import datetime, timedelta


def create_app(config: Dict[str, Any], data: Dict[str, Any]) -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)

    @app.route("/")
    def index():
        """Render main dashboard."""
        articles = data.get("articles", [])
        stats = data.get("stats", {})

        # Get all configured sources from config
        all_sources = []
        sources_config = config.get("sources", {})
        for tier in ["tier1", "tier2", "tier3"]:
            for source in sources_config.get(tier, []):
                all_sources.append({
                    "name": source.get("name"),
                    "url": source.get("url"),
                    "priority": source.get("priority", "medium"),
                    "tier": tier
                })

        # Group articles by source
        articles_by_source = {}
        for article in articles:
            source = article.get("source", "Unknown")
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)

        # Calculate source stats
        source_stats = {}
        for source_info in all_sources:
            source_name = source_info["name"]
            articles_list = articles_by_source.get(source_name, [])
            source_stats[source_name] = {
                "article_count": len(articles_list),
                "status": "active" if len(articles_list) > 0 else "no_data",
                "priority": source_info["priority"],
                "tier": source_info["tier"],
                "url": source_info["url"],
                "articles": articles_list
            }

        return render_template_string(
            DASHBOARD_TEMPLATE,
            articles=articles,
            stats=stats,
            articles_by_source=articles_by_source,
            all_sources=all_sources,
            source_stats=source_stats
        )

    @app.route("/health")
    def health():
        """Health check endpoint."""
        return {"status": "healthy", "articles_count": len(data.get("articles", []))}

    @app.route("/api/sources")
    def api_sources():
        """API endpoint for source statistics."""
        sources_config = config.get("sources", {})
        all_sources = []
        for tier in ["tier1", "tier2", "tier3"]:
            for source in sources_config.get(tier, []):
                all_sources.append({
                    "name": source.get("name"),
                    "url": source.get("url"),
                    "priority": source.get("priority", "medium"),
                    "tier": tier
                })
        return jsonify({"sources": all_sources})

    return app


DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300">
    <title>AI Competitive Intelligence - Live Dashboard</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .header .subtitle {
            color: #7f8c8d;
            font-size: 16px;
        }
        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #2ecc71;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-card h3 {
            color: #7f8c8d;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        .metric-card .value {
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }
        .content-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }
        .source-section {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .source-section h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        .article {
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #95a5a6;
            transition: all 0.2s;
        }
        .article:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        .article.critical { border-left-color: #e74c3c; }
        .article.high { border-left-color: #f39c12; }
        .article.medium { border-left-color: #3498db; }
        .article-title {
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 8px;
        }
        .article-title a {
            color: #2c3e50;
            text-decoration: none;
        }
        .article-title a:hover {
            color: #667eea;
        }
        .article-meta {
            font-size: 12px;
            color: #7f8c8d;
            margin-bottom: 8px;
        }
        .priority-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            margin-left: 10px;
        }
        .priority-critical { background: #e74c3c; color: white; }
        .priority-high { background: #f39c12; color: white; }
        .priority-medium { background: #3498db; color: white; }
        .priority-low { background: #95a5a6; color: white; }
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
        }
        .auto-refresh {
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 8px;
            display: inline-block;
            margin-top: 10px;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="live-indicator"></span>AI Competitive Intelligence Dashboard</h1>
            <p class="subtitle">Real-time monitoring of AI industry developments</p>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <h3>Sources Monitored</h3>
                <div class="value">{{ stats.get('successful_sources', 0) }}/{{ stats.get('total_sources', 0) }}</div>
            </div>
            <div class="metric-card">
                <h3>New Articles</h3>
                <div class="value">{{ stats.get('articles_after_deduplication', 0) }}</div>
            </div>
            <div class="metric-card">
                <h3>Duplicates Removed</h3>
                <div class="value">{{ stats.get('duplicates_removed', 0) }}</div>
            </div>
            <div class="metric-card">
                <h3>Success Rate</h3>
                <div class="value">{{ '%0.1f' | format((stats.get('successful_sources', 0) / stats.get('total_sources', 1) * 100) if stats.get('total_sources', 0) > 0 else 0) }}%</div>
            </div>
        </div>

        <div class="content-grid">
            {% for source, source_articles in articles_by_source.items() %}
            <div class="source-section">
                <h2>{{ source }} <span style="color: #7f8c8d; font-size: 14px; font-weight: normal;">({{ source_articles|length }} articles)</span></h2>
                {% for article in source_articles[:10] %}
                <div class="article {{ article.get('priority', 'medium') }}">
                    <div class="article-title">
                        <a href="{{ article.get('link', '#') }}" target="_blank">{{ article.get('title', 'No Title') }}</a>
                        <span class="priority-badge priority-{{ article.get('priority', 'medium') }}">{{ article.get('priority', 'medium') }}</span>
                    </div>
                    <div class="article-meta">{{ article.get('date_formatted', 'Date unknown') }}</div>
                    <div class="article-summary">{{ article.get('summary', '')[:200] }}...</div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>

        <div class="footer">
            <p>AI Competitive Intelligence Tracker | Enterprise-Grade Monitoring System</p>
            <div class="auto-refresh">Auto-refresh every 5 minutes</div>
        </div>
    </div>
</body>
</html>
"""


def launch_dashboard(config: Dict[str, Any], data: Dict[str, Any]):
    """Launch the web dashboard."""
    dashboard_config = config.get("dashboard", {})

    host = dashboard_config.get("host", "127.0.0.1")
    port = dashboard_config.get("port", 5000)
    debug = dashboard_config.get("debug", False)

    app = create_app(config, data)

    print(f"\nDashboard available at: http://{host}:{port}")
    print("Press Ctrl+C to stop the server\n")

    app.run(host=host, port=port, debug=debug)
