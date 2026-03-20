"""Reusable HTML component builders for the TKT Kingdom dashboard."""

from __future__ import annotations


def hero_banner_html(kpi: dict) -> str:
    """Generate the hero banner HTML with KPI values.

    Parameters
    ----------
    kpi : dict
        KPI metrics dict from ``compute_kpi_metrics`` containing keys
        ``num_areas``, ``total_groups``, ``total_members``,
        ``strong_count``, and ``weak_count``.

    Returns
    -------
    str
        Complete hero banner HTML string.
    """
    return (
        '<div class="hero-banner" role="banner"'
        ' aria-label="TKT Kingdom dashboard hero banner">'
        '<div class="hero-shape hero-shape-1"></div>'
        '<div class="hero-shape hero-shape-2"></div>'
        '<div class="hero-shape hero-shape-3"></div>'
        '<div class="hero-shape hero-shape-4"></div>'
        '<div class="hero-content">'
        '<div class="hero-badge">'
        '<div class="hero-badge-dot"></div>'
        '<span class="hero-badge-text">West Campus &#183; Hyderabad</span>'
        '</div>'
        '<div class="hero-title-line1">TKT Kingdom</div>'
        '<div class="hero-title-line2">Expanding His Territory</div>'
        f'{typewriter_verse_html()}'
        '</div>'
        '<div class="hero-kpis">'
        '<div class="hero-kpi">'
        '<div class="hero-kpi-icon">&#x25A0;</div>'
        f'<div class="hero-kpi-value">{kpi["num_areas"]}</div>'
        '<div class="hero-kpi-label">Territories</div>'
        '</div>'
        '<div class="hero-kpi">'
        '<div class="hero-kpi-icon">&#x2666;</div>'
        f'<div class="hero-kpi-value">{kpi["total_groups"]}</div>'
        '<div class="hero-kpi-label">Shepherds</div>'
        '</div>'
        '<div class="hero-kpi">'
        '<div class="hero-kpi-icon">&#x2022;</div>'
        f'<div class="hero-kpi-value">{kpi["total_members"]}</div>'
        '<div class="hero-kpi-label">Souls Gathered</div>'
        '</div>'
        '<div class="hero-kpi">'
        '<div class="hero-kpi-icon">&#x2605;</div>'
        f'<div class="hero-kpi-value">{kpi["strong_count"]}</div>'
        '<div class="hero-kpi-label">Strong Groups</div>'
        '</div>'
        '<div class="hero-kpi">'
        '<div class="hero-kpi-icon">&#x25CB;</div>'
        f'<div class="hero-kpi-value">{kpi["weak_count"]}</div>'
        '<div class="hero-kpi-label">Emerging</div>'
        '</div>'
        '</div>'
        '</div>'
    )


def section_header_html(
    icon: str, title: str, verse: str = "", reference: str = ""
) -> str:
    """Generate a section header with optional scripture verse.

    Parameters
    ----------
    icon : str
        HTML entity or emoji for the section icon (e.g. ``"&#x2666;"``).
    title : str
        Section title text.
    verse : str, optional
        Scripture verse text to display below the title.
    reference : str, optional
        Scripture reference (e.g. ``"Matthew 6:21"``).

    Returns
    -------
    str
        Section header HTML string.
    """
    verse_html = ""
    if verse:
        ref_part = f" - {reference}" if reference else ""
        verse_html = (
            '<div class="typewriter-container" style="min-height:2em;">'
            '<div class="typewriter-verse tw-active tw-v1">'
            f'"{verse}"{ref_part}'
            '</div></div>'
        )
    return (
        '<div style="font-family: \'Cinzel\', serif; font-size: 1.1rem;'
        ' color: var(--text-heading); letter-spacing: 2px; margin-bottom: 4px;">'
        f'    {icon} {title}</div>'
        f'{verse_html}'
    )


SCRIPTURE_VERSES = [
    ("The harvest is plentiful, but the workers are few.",
     "Matthew 9:37"),
    ("Go and make disciples of all nations.",
     "Matthew 28:19"),
    ("Where two or three gather in my name, there am I.",
     "Matthew 18:20"),
    ("The earth is the Lord's, and everything in it.",
     "Psalm 24:1"),
]


def typewriter_verse_html() -> str:
    """Generate a cycling typewriter scripture verse component.

    Returns
    -------
    str
        HTML with 4 verses that type out and cycle via CSS animation.
    """
    verses_html = ""
    for i, (verse, ref) in enumerate(SCRIPTURE_VERSES):
        verses_html += (
            f'<div class="typewriter-verse tw-active tw-v{i + 1}">'
            f'"{verse}" - {ref}'
            f'</div>'
        )
    return (
        f'<div class="typewriter-container">{verses_html}</div>'
    )


def footer_html() -> str:
    """Generate the footer HTML.

    Returns
    -------
    str
        Footer HTML string with scripture and version info.
    """
    return (
        '<div style="text-align: center; padding: 16px 0 8px 0;">'
        f'    {typewriter_verse_html()}'
        '    <div style="width: 60px; height: 1px;'
        '         background: linear-gradient(90deg, transparent, #D4AF37, transparent);'
        '         margin: 12px auto;"></div>'
        '    <div style="font-family: \'Cinzel\', serif;'
        '         color: var(--text-muted); font-size: 0.75rem; letter-spacing: 2px;">'
        '        TKT Kingdom v1.2 &#183; West Campus &#183; Hyderabad'
        '    </div>'
        '</div>'
    )
