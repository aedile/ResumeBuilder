"""Shared constants for resume generators."""

# All visual styles supported by the HTML (and transitively PDF) generator.
# Update this list when adding new Jinja2 templates to resume_builder/templates/.
SUPPORTED_STYLES: frozenset[str] = frozenset({"classic", "modern", "tech", "ats"})
