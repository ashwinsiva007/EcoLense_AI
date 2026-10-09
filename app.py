"""EconLens AI - Main Application Entry Point.

Regional Economic Intelligence and Opportunity Analysis Platform.
Supports native Streamlit execution and Vercel WSGI cloud gateway.
"""

from __future__ import annotations

import streamlit as st
from streamlit.runtime import exists as streamlit_runtime_exists

from config.settings import get_settings
from src.dashboard.components import (
    render_disclaimer_banner,
    render_module_placeholder,
    render_welcome_state,
)
from src.dashboard.layout import (
    apply_custom_styles,
    render_app_footer,
    render_app_header,
    render_sidebar_navigation,
)
from src.data.data_loader import DataLoader
from src.utils.logging_config import get_logger, setup_logging

# Initialize application logging and configuration
setup_logging()
logger = get_logger("app")
settings = get_settings()


def render_overview_page() -> None:
    """Renders the central Overview page."""
    render_welcome_state()

    st.markdown("### 🗺️ System Readiness &amp; Verification Status")

    data_loader = DataLoader(settings)
    raw_count = len(data_loader.list_available_raw_datasets())
    processed_count = len(data_loader.list_available_processed_datasets())
    sample_count = len(data_loader.list_available_sample_datasets())

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Verified Processed Datasets", f"{processed_count} files")
    with col2:
        st.metric("Raw Ingested Datasets", f"{raw_count} files")
    with col3:
        st.metric("Sample / Demo Datasets", f"{sample_count} files")

    if not data_loader.has_verified_datasets():
        st.info(
            "ℹ️ **No verified datasets ingested yet.**\n\n"
            "The system is currently operating in **Stage 1 (Engineering Foundation)** mode. "
            "To maintain strict analytical integrity, the dashboard will not display simulated or "
            "fabricated regional metrics until actual verified datasets are integrated in Stage 2."
        )


def main() -> None:
    """Main application loop and router for Streamlit."""
    try:
        # Ensure directories exist
        settings.ensure_directories()

        # Apply CSS styling
        apply_custom_styles()

        # Render Header
        render_app_header()

        # Render Sidebar & Navigation
        current_page = render_sidebar_navigation()
        logger.debug("Active navigation page: %s", current_page)

        # Route to selected page
        if current_page == "Overview":
            render_overview_page()
        else:
            render_module_placeholder(current_page)

        # Render Footer
        render_app_footer()

    except Exception as exc:
        logger.exception("Unexpected error during application execution: %s", exc)
        st.error(
            f"An error occurred while rendering the page: {exc}. "
            "Please check the application logs for detailed diagnostics."
        )


# ==============================================================================
# WSGI Serverless Handler for Vercel and Cloud Functions
# ==============================================================================
def handler(environ: dict, start_response: callable) -> list[bytes]:
    """WSGI compatibility handler for serverless deployments like Vercel."""
    status = "200 OK"
    response_headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Cache-Control", "public, max-age=0, must-revalidate"),
    ]
    start_response(status, response_headers)

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EconLens AI — Regional Economic Intelligence</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b0f19;
            --surface: #111827;
            --card: rgba(17, 24, 39, 0.85);
            --border: rgba(255, 255, 255, 0.08);
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --text-primary: #f9fafb;
            --text-secondary: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            background-image: 
                radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.1) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.1) 0px, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .container {
            max-width: 800px;
            width: 100%;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 48px;
            backdrop-filter: blur(16px);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            text-align: center;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--accent-glow);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: var(--accent);
            padding: 6px 16px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 24px;
            letter-spacing: 0.02em;
        }
        h1 {
            font-size: 2.4rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 16px;
            background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p.subtitle {
            font-size: 1.05rem;
            color: var(--text-secondary);
            line-height: 1.6;
            margin-bottom: 36px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 36px;
            text-align: left;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
        }
        .status-card h4 {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }
        .status-card p {
            font-size: 1.1rem;
            font-weight: 700;
            color: #38bdf8;
        }
        .btn-group {
            display: flex;
            gap: 16px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .btn-primary {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #0284c7;
            color: white;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s ease;
            box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.4);
        }
        .btn-primary:hover {
            background: #0369a1;
            transform: translateY(-2px);
        }
        .btn-secondary {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-primary);
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s ease;
        }
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }
        .footer-note {
            margin-top: 32px;
            font-size: 0.85rem;
            color: #6b7280;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">🌐 EconLens AI Gateway</div>
        <h1>Regional Economic Intelligence</h1>
        <p class="subtitle">Evidence-grounded opportunity scoring, bottleneck diagnostics, and longitudinal simulation engine for regional economic growth.</p>
        
        <div class="status-grid">
            <div class="status-card">
                <h4>System Architecture</h4>
                <p>Modular Monolith</p>
            </div>
            <div class="status-card">
                <h4>Foundation State</h4>
                <p>Stage 1 Active</p>
            </div>
            <div class="status-card">
                <h4>Analytics Engine</h4>
                <p>Zero-Fabrication</p>
            </div>
        </div>

        <div class="btn-group">
            <a href="https://github.com/ashwinsiva007/EcoLense_AI" target="_blank" class="btn-primary">
                📂 View GitHub Repository
            </a>
            <a href="https://share.streamlit.io" target="_blank" class="btn-secondary">
                🚀 Deploy Streamlit Cloud
            </a>
        </div>

        <div class="footer-note">
            EconLens AI Platform &bull; Built with Python & Streamlit
        </div>
    </div>
</body>
</html>"""
    return [html_content.encode("utf-8")]


# Top-level exports expected by Vercel's Python Serverless builder
app = handler
application = handler


# Runtime Dispatcher: checks if executed inside Streamlit runtime
if streamlit_runtime_exists():
    st.set_page_config(
        page_title="EconLens AI — Regional Economic Intelligence",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    main()
elif __name__ == "__main__":
    main()
