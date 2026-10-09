"""Reusable UI components, banners, placeholders, and state views for EconLens AI."""

from __future__ import annotations

from typing import Optional

import streamlit as st

from src.dashboard.layout import PAGES


def render_status_badge(
    label: str, badge_type: str = "planned"
) -> str:
    """Generates HTML snippet for a status badge.

    Args:
        label: Text to display inside badge.
        badge_type: 'active', 'planned', or 'synthetic'.

    Returns:
        str: HTML representation of badge.
    """
    class_name = f"badge-{badge_type}"
    return f'<span class="status-badge {class_name}">{label}</span>'


def render_disclaimer_banner(title: str, message: str) -> None:
    """Renders a prominent analytical transparency / disclaimer banner."""
    st.markdown(
        f"""
        <div class="econlens-disclaimer">
            <strong>⚠️ {title}:</strong> {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_state() -> None:
    """Renders informative welcome state when no verified datasets are ingested."""
    st.markdown(
        """
        <div class="econlens-card">
            <h3>👋 Welcome to EconLens AI</h3>
            <p>
                EconLens AI is an open, evidence-grounded regional economic intelligence platform designed to 
                discover potential economic opportunities and structural bottlenecks across geographical districts.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="econlens-card">
                <h4>🎯 Core Principles</h4>
                <ul>
                    <li><strong>Evidence-Based:</strong> Findings are strictly derived from verified empirical data.</li>
                    <li><strong>No Fabricated Data:</strong> The system will never silently substitute fake statistics when real data is missing.</li>
                    <li><strong>Explainable Scores:</strong> Opportunity scores and bottleneck findings provide clear factor decompositions.</li>
                    <li><strong>Non-Causal Humility:</strong> Distinguishes statistical associations from unproven causal claims.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="econlens-card">
                <h4>📊 Planned Ingestion Domains</h4>
                <ul>
                    <li><strong>Socioeconomic:</strong> Demographics, income, literacy, poverty indicators.</li>
                    <li><strong>Labor & Skills:</strong> Workforce participation, skill pools, sector employment.</li>
                    <li><strong>Infrastructure:</strong> Transport connectivity, power reliability, digital access.</li>
                    <li><strong>Business & Finance:</strong> Enterprise density, credit depth, industrial clusters.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_disclaimer_banner(
        "Current System Status (Stage 1)",
        "The project skeleton, configuration, logging, and test suites are initialized. "
        "Verified district-level datasets will be integrated in Stage 2 once the study geography is finalized.",
    )


def render_module_placeholder(page_name: str) -> None:
    """Renders a structured placeholder for future modules."""
    meta = PAGES.get(page_name, {})
    icon = meta.get("icon", "📌")
    stage = meta.get("stage", "Future Stage")
    desc = meta.get("description", "Planned intelligence module.")

    st.markdown(
        f"""
        <div class="econlens-hero">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h2>{icon} {page_name}</h2>
                <span class="status-badge badge-planned">{stage}</span>
            </div>
            <p class="econlens-subtitle">{desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="econlens-card">
            <h4>📋 Implementation Status</h4>
            <p>
                This module's architectural contracts and interfaces are defined in the source tree, 
                and its algorithmic implementation is scheduled for subsequent development stages.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if page_name == "Opportunity Explorer":
        st.info(
            "**Scheduled Capabilities:** Multi-dimensional opportunity indexing, "
            "district ranking, dimension decomposition charts, and choropleth maps."
        )
    elif page_name == "Bottleneck Analysis":
        st.info(
            "**Scheduled Capabilities:** Benchmark gap analysis, infrastructure deficits, "
            "skilling bottlenecks, and diagnostic priority scoring."
        )
    elif page_name == "Forecasting":
        st.info(
            "**Scheduled Capabilities:** Longitudinal time-series forecasting with historical "
            "grounding, confidence bounds, and explicit model assumption documentation."
        )
    elif page_name == "Scenario Simulator":
        st.info(
            "**Scheduled Capabilities:** What-if policy and capital investment shocks, "
            "sensitivity simulations, and comparative regional delta projections."
        )
    elif page_name == "Data and Sources":
        st.info(
            "**Scheduled Capabilities:** Dataset schema validation, geographic boundary alignment, "
            "data dictionary viewer, and data quality reports."
        )
