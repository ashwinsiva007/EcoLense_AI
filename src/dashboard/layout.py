"""Layout, theming, and navigation management for the EconLens AI dashboard."""

from __future__ import annotations

from typing import Dict, List

import streamlit as st

from config.settings import get_settings

# Ordered navigation destinations with their icons and short summaries
PAGES: Dict[str, Dict[str, str]] = {
    "Overview": {
        "icon": "🌐",
        "description": "Platform architecture, study geography, and intelligence overview.",
        "stage": "Stage 1 (Foundation Active)",
    },
    "Opportunity Explorer": {
        "icon": "📈",
        "description": "Multi-dimensional regional scoring, comparative ranking, and index analysis.",
        "stage": "Stage 4 (Planned)",
    },
    "Bottleneck Analysis": {
        "icon": "🔍",
        "description": "Structural constraint detection, deficit diagnostics, and benchmark gaps.",
        "stage": "Stage 5 (Planned)",
    },
    "Forecasting": {
        "icon": "📊",
        "description": "Longitudinal indicator forecasting with statistical uncertainty bands.",
        "stage": "Future Milestone",
    },
    "Scenario Simulator": {
        "icon": "🎛️",
        "description": "Hypothetical what-if sensitivity analysis and policy shock simulations.",
        "stage": "Future Milestone",
    },
    "Data and Sources": {
        "icon": "📁",
        "description": "Ingested regional datasets, metadata registry, data dictionary, and validation logs.",
        "stage": "Stage 2 (Planned)",
    },
}


def apply_custom_styles() -> None:
    """Injects modern, dark-oriented CSS for a sleek and responsive UI."""
    st.markdown(
        """
        <style>
        /* Base typography and smooth rendering */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Glassmorphic cards */
        .econlens-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(10px);
            transition: border-color 0.2s ease, transform 0.2s ease;
        }
        .econlens-card:hover {
            border-color: rgba(99, 102, 241, 0.4);
        }

        /* Hero Header */
        .econlens-hero {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 14px;
            padding: 2rem;
            margin-bottom: 1.75rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        }

        .econlens-title {
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(90deg, #60A5FA, #A78BFA, #34D399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            padding: 0;
        }

        .econlens-subtitle {
            font-size: 1.05rem;
            color: #94A3B8;
            margin-top: 0.5rem;
            line-height: 1.5;
        }

        /* Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }
        .badge-active {
            background-color: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(52, 211, 153, 0.3);
        }
        .badge-planned {
            background-color: rgba(245, 158, 11, 0.15);
            color: #FBBF24;
            border: 1px solid rgba(251, 191, 36, 0.3);
        }
        .badge-synthetic {
            background-color: rgba(239, 68, 68, 0.15);
            color: #F87171;
            border: 1px solid rgba(248, 113, 113, 0.3);
        }

        /* Disclaimer Notice Box */
        .econlens-disclaimer {
            background-color: rgba(30, 41, 59, 0.5);
            border-left: 4px solid #F59E0B;
            padding: 1rem 1.25rem;
            border-radius: 0 8px 8px 0;
            font-size: 0.88rem;
            color: #CBD5E1;
            margin: 1.25rem 0;
        }

        /* Footer */
        .econlens-footer {
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            margin-top: 3rem;
            padding-top: 1.25rem;
            text-align: center;
            font-size: 0.85rem;
            color: #64748B;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_app_header() -> None:
    """Renders the top branding banner."""
    st.markdown(
        """
        <div class="econlens-hero">
            <div class="econlens-title">EconLens AI</div>
            <div class="econlens-subtitle">
                Regional Economic Intelligence &amp; Opportunity Analysis Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_navigation() -> str:
    """Renders sidebar controls and navigation selection.

    Returns:
        str: Selected page name.
    """
    settings = get_settings()

    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        selected_page = st.radio(
            "Select Module",
            options=list(PAGES.keys()),
            format_func=lambda page: f"{PAGES[page]['icon']} {page}",
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("### ⚙️ System Status")
        st.markdown(f"**Environment:** `{settings.app_env}`")
        st.markdown(f"**Version:** `v0.1.0 (Stage 1)`")
        st.markdown(f"**Log Level:** `{settings.log_level}`")

        st.markdown("---")
        st.markdown("### 📌 Stage 1 Foundation")
        st.caption(
            "Active Stage: Skeleton, Config, Logging, Tests, and Work Log. "
            "No unverified or fabricated datasets are loaded."
        )

    return selected_page


def render_app_footer() -> None:
    """Renders standardized application footer."""
    st.markdown(
        """
        <div class="econlens-footer">
            <strong>EconLens AI</strong> — Regional Economic Intelligence Platform &bull; Stage 1 Engineering Foundation
        </div>
        """,
        unsafe_allow_html=True,
    )
