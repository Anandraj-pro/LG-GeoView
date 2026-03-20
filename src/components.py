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
        '<div class="hero-scripture">'
        '"The harvest is plentiful, but the workers are few.'
        ' Ask the Lord of the harvest to send out workers'
        ' into his harvest field."'
        '<br>- Matthew 9:37-38'
        '</div>'
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
            '<div style="font-family: \'Cormorant Garamond\', serif;'
            ' font-size: 0.85rem; color: var(--text-muted); font-style: italic;'
            f' margin-bottom: 12px;">"{verse}"{ref_part}</div>'
        )
    return (
        '<div style="font-family: \'Cinzel\', serif; font-size: 1.1rem;'
        ' color: var(--text-heading); letter-spacing: 2px; margin-bottom: 4px;">'
        f'    {icon} {title}</div>'
        f'{verse_html}'
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
        '    <div style="font-family: \'Cormorant Garamond\', serif;'
        '         font-size: 0.9rem; color: var(--text-muted); font-style: italic;'
        '         max-width: 500px; margin: 0 auto; line-height: 1.5;">'
        '        "The harvest is plentiful, but the workers are few.'
        '        Ask the Lord of the harvest to send out workers'
        '        into his harvest field."'
        '        <br><span style="font-size: 0.8rem; color: var(--text-muted);">'
        '        - Matthew 9:37-38</span>'
        '    </div>'
        '    <div style="width: 60px; height: 1px;'
        '         background: linear-gradient(90deg, transparent, #D4AF37, transparent);'
        '         margin: 12px auto;"></div>'
        '    <div style="font-family: \'Cinzel\', serif;'
        '         color: var(--text-muted); font-size: 0.75rem; letter-spacing: 2px;">'
        '        TKT Kingdom v1.2 &#183; West Campus &#183; Hyderabad'
        '    </div>'
        '</div>'
    )
