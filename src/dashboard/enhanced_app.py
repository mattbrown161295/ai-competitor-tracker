"""
Enhanced Flask-based web dashboard with source cards and visual tracking.
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
                    "tier": tier.replace("tier", "Tier ")
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

            # Determine status
            if len(articles_list) > 0:
                status = "success"
                status_text = f"{len(articles_list)} articles"
            else:
                status = "no_data"
                status_text = "No articles found"

            source_stats[source_name] = {
                "article_count": len(articles_list),
                "status": status,
                "status_text": status_text,
                "priority": source_info["priority"],
                "tier": source_info["tier"],
                "url": source_info["url"],
                "articles": articles_list[:7]  # Last 7 days worth
            }

        return render_template_string(
            ENHANCED_DASHBOARD_TEMPLATE,
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

    return app


ENHANCED_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300">
    <title>AI Competitive Intelligence Dashboard</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: #f0f2f5;
            min-height: 100vh;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .header .subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #2ecc71;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 2s infinite;
            box-shadow: 0 0 10px #2ecc71;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.1); }
        }

        /* Container */
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px 20px;
        }

        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            background: white;
            padding: 10px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .tab {
            padding: 12px 24px;
            background: transparent;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            color: #7f8c8d;
            transition: all 0.2s;
        }
        .tab:hover {
            background: #f8f9fa;
            color: #2c3e50;
        }
        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        /* Tab Content */
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }

        /* Metrics Grid */
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        }
        .metric-card h3 {
            color: #7f8c8d;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            font-weight: 600;
        }
        .metric-card .value {
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* Source Cards Grid */
        .sources-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
        }
        .source-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            border-left: 4px solid #95a5a6;
            cursor: pointer;
        }
        .source-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
        .source-card.tier-1 { border-left-color: #e74c3c; }
        .source-card.tier-2 { border-left-color: #f39c12; }
        .source-card.tier-3 { border-left-color: #3498db; }

        .source-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        .source-title {
            font-size: 18px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .source-tier {
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .source-tier.tier-1 { background: #fee; color: #e74c3c; }
        .source-tier.tier-2 { background: #fef5e7; color: #f39c12; }
        .source-tier.tier-3 { background: #ebf5fb; color: #3498db; }

        .source-status {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 15px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .status-indicator.success { background: #2ecc71; box-shadow: 0 0 10px rgba(46, 204, 113, 0.4); }
        .status-indicator.no_data { background: #95a5a6; }
        .status-indicator.error { background: #e74c3c; animation: pulse 2s infinite; }

        .source-stats {
            font-size: 14px;
            color: #7f8c8d;
        }
        .article-count {
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
            margin-right: 5px;
        }

        .source-url {
            font-size: 12px;
            color: #95a5a6;
            text-decoration: none;
            display: block;
            margin-top: 10px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .source-url:hover {
            color: #667eea;
        }

        .view-articles-btn {
            margin-top: 15px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: opacity 0.2s;
        }
        .view-articles-btn:hover {
            opacity: 0.9;
        }
        .view-articles-btn:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }

        /* Article List */
        .article-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .article-item {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 3px solid #667eea;
            transition: all 0.2s;
        }
        .article-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        .article-item.critical { border-left-color: #e74c3c; }
        .article-item.high { border-left-color: #f39c12; }
        .article-item.medium { border-left-color: #3498db; }

        .article-title {
            font-size: 15px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .article-title a {
            color: inherit;
            text-decoration: none;
        }
        .article-title a:hover {
            color: #667eea;
        }
        .article-meta {
            font-size: 12px;
            color: #95a5a6;
            margin-bottom: 8px;
        }
        .article-summary {
            font-size: 13px;
            color: #7f8c8d;
            line-height: 1.5;
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .empty-state-icon {
            font-size: 64px;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        .empty-state-title {
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .empty-state-text {
            font-size: 14px;
            color: #7f8c8d;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 30px 20px;
            color: #95a5a6;
            font-size: 13px;
        }
        .auto-refresh-badge {
            display: inline-block;
            background: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            color: #667eea;
            font-weight: 600;
            margin-top: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><span class="live-indicator"></span>AI Competitive Intelligence Dashboard</h1>
        <p class="subtitle">Real-time monitoring • Last updated: just now</p>
    </div>

    <div class="container">
        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="switchTab('overview')">📊 Overview</button>
            <button class="tab" onclick="switchTab('sources')">🎯 Sources</button>
            <button class="tab" onclick="switchTab('recent')">📰 Recent Activity</button>
        </div>

        <!-- Overview Tab -->
        <div id="overview-tab" class="tab-content active">
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
                    <div class="value">{{ '%0.0f' | format((stats.get('successful_sources', 0) / stats.get('total_sources', 1) * 100) if stats.get('total_sources', 0) > 0 else 0) }}%</div>
                </div>
            </div>

            {% if articles|length > 0 %}
            <h2 style="margin-bottom: 20px; color: #2c3e50; font-size: 22px;">Recent Developments</h2>
            <div class="article-list">
                {% for article in articles[:10] %}
                <div class="article-item {{ article.get('priority', 'medium') }}">
                    <div class="article-title">
                        <a href="{{ article.get('link', '#') }}" target="_blank">{{ article.get('title', 'No Title') }}</a>
                    </div>
                    <div class="article-meta">
                        {{ article.get('source', 'Unknown') }} • {{ article.get('date_formatted', 'Date unknown') }}
                    </div>
                    <div class="article-summary">{{ article.get('summary', '')[:200] }}...</div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <div class="empty-state-title">No Articles Yet</div>
                <div class="empty-state-text">The system is running but hasn't collected articles yet. This may be due to CSS selector configuration or source availability.</div>
            </div>
            {% endif %}
        </div>

        <!-- Sources Tab -->
        <div id="sources-tab" class="tab-content">
            <h2 style="margin-bottom: 25px; color: #2c3e50; font-size: 22px;">All Intelligence Sources</h2>
            <div class="sources-grid">
                {% for source in all_sources %}
                {% set stats_data = source_stats.get(source.name, {}) %}
                <div class="source-card tier-{{ source.tier[-1] }}">
                    <div class="source-header">
                        <div>
                            <div class="source-title">{{ source.name }}</div>
                            <span class="source-tier tier-{{ source.tier[-1] }}">{{ source.tier }}</span>
                        </div>
                    </div>

                    <div class="source-status">
                        <span class="status-indicator {{ stats_data.get('status', 'no_data') }}"></span>
                        <span class="source-stats">{{ stats_data.get('status_text', 'No data') }}</span>
                    </div>

                    {% if stats_data.get('article_count', 0) > 0 %}
                    <div style="margin: 15px 0;">
                        <span class="article-count">{{ stats_data.get('article_count', 0) }}</span>
                        <span style="color: #7f8c8d; font-size: 14px;">articles found</span>
                    </div>
                    {% endif %}

                    <a href="{{ source.url }}" target="_blank" class="source-url" title="{{ source.url }}">
                        🔗 {{ source.url }}
                    </a>

                    <button class="view-articles-btn" onclick="viewSourceArticles('{{ source.name }}')"
                            {% if stats_data.get('article_count', 0) == 0 %}disabled{% endif %}>
                        {% if stats_data.get('article_count', 0) > 0 %}
                        View Articles (Last 7 Days)
                        {% else %}
                        No Articles Available
                        {% endif %}
                    </button>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Recent Activity Tab -->
        <div id="recent-tab" class="tab-content">
            <h2 style="margin-bottom: 25px; color: #2c3e50; font-size: 22px;">Recent Activity Stream</h2>

            {% if articles|length > 0 %}
            {% for source, source_articles in articles_by_source.items() %}
            <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                <h3 style="color: #2c3e50; margin-bottom: 15px; font-size: 18px;">
                    {{ source }}
                    <span style="color: #95a5a6; font-size: 14px; font-weight: normal;">({{ source_articles|length }} articles)</span>
                </h3>
                <div class="article-list">
                    {% for article in source_articles[:5] %}
                    <div class="article-item {{ article.get('priority', 'medium') }}">
                        <div class="article-title">
                            <a href="{{ article.get('link', '#') }}" target="_blank">{{ article.get('title', 'No Title') }}</a>
                        </div>
                        <div class="article-meta">{{ article.get('date_formatted', 'Date unknown') }}</div>
                        <div class="article-summary">{{ article.get('summary', '')[:150] }}...</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
            {% else %}
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <div class="empty-state-title">Activity Stream Empty</div>
                <div class="empty-state-text">No recent activity to display. Articles will appear here as they are collected.</div>
            </div>
            {% endif %}
        </div>

        <div class="footer">
            <p>AI Competitive Intelligence Tracker • Enterprise-Grade Monitoring System</p>
            <div class="auto-refresh-badge">⟳ Auto-refresh every 5 minutes</div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            // Hide all tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');

            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        function viewSourceArticles(sourceName) {
            // Switch to recent activity tab and scroll to source
            switchTab('recent');
            setTimeout(() => {
                const heading = Array.from(document.querySelectorAll('h3')).find(h => h.textContent.includes(sourceName));
                if (heading) {
                    heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    heading.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    heading.style.color = 'white';
                    heading.style.padding = '10px 15px';
                    heading.style.borderRadius = '8px';
                    setTimeout(() => {
                        heading.style.background = '';
                        heading.style.color = '';
                        heading.style.padding = '';
                    }, 2000);
                }
            }, 100);
        }
    </script>
</body>
</html>
"""


def launch_dashboard(config: Dict[str, Any], data: Dict[str, Any]):
    """Launch the enhanced web dashboard."""
    dashboard_config = config.get("dashboard", {})

    host = dashboard_config.get("host", "127.0.0.1")
    port = dashboard_config.get("port", 5000)
    debug = dashboard_config.get("debug", False)

    app = create_app(config, data)

    print(f"\nEnhanced Dashboard available at: http://{host}:{port}")
    print("Press Ctrl+C to stop the server\n")

    app.run(host=host, port=port, debug=debug)
