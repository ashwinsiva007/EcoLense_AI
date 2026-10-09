"""EconLens AI - Main Streamlit Application Entry Point.

Regional Economic Intelligence and Opportunity Analysis Platform.
Stage 1: Engineering Foundation and Project Skeleton.
"""

from __future__ import annotations

import streamlit as st

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

# Configure Streamlit page settings
st.set_page_config(
    page_title="EconLens AI — Regional Economic Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    """Main application loop and router."""
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


if __name__ == "__main__":
    main()
