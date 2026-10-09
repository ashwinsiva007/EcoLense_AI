"""Dashboard presentation and UI component package for EconLens AI."""

from src.dashboard.components import (
    render_disclaimer_banner,
    render_module_placeholder,
    render_status_badge,
    render_welcome_state,
)
from src.dashboard.layout import (
    PAGES,
    apply_custom_styles,
    render_app_footer,
    render_app_header,
    render_sidebar_navigation,
)

__all__ = [
    "PAGES",
    "apply_custom_styles",
    "render_app_header",
    "render_app_footer",
    "render_sidebar_navigation",
    "render_welcome_state",
    "render_module_placeholder",
    "render_status_badge",
    "render_disclaimer_banner",
]
