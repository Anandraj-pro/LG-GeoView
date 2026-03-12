"""Chart builders using Plotly."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


STRENGTH_COLORS = {
    "Strong": "#00b894",
    "Medium": "#fdcb6e",
    "Weak": "#e17055",
}

# Light mode layout — white bg, dark text, prints as-is
LIGHT_LAYOUT = dict(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font=dict(color="#333333", size=12),
    title_font=dict(color="#222222", size=16),
    xaxis=dict(
        gridcolor="#e0e0e0",
        tickfont=dict(color="#444444"),
        title_font=dict(color="#333333"),
    ),
    yaxis=dict(
        gridcolor="#e0e0e0",
        tickfont=dict(color="#444444"),
        title_font=dict(color="#333333"),
    ),
    legend=dict(font=dict(color="#333333")),
)


def members_by_area_chart(df: pd.DataFrame) -> go.Figure:
    """Stacked bar chart: families + individuals by area."""
    area_data = df.groupby("area").agg(
        families=("families", "sum"),
        individuals=("individuals", "sum"),
        total=("members", "sum"),
    ).sort_values("total", ascending=True).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=area_data["area"], x=area_data["families"],
        name="Families", orientation="h",
        marker_color="#00b894",
    ))
    fig.add_trace(go.Bar(
        y=area_data["area"], x=area_data["individuals"],
        name="Individuals", orientation="h",
        marker_color="#74b9ff",
    ))

    fig.update_layout(
        barmode="stack",
        title="Families & Individuals by Area",
        **LIGHT_LAYOUT,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig.update_layout(legend=dict(orientation="h", y=-0.15, font=dict(color="#333333")))
    return fig


def groups_by_area_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart: care group count by area."""
    area_data = df.groupby("area")["lg_group"].count().sort_values(ascending=True).reset_index()
    area_data.columns = ["area", "groups"]

    fig = px.bar(
        area_data,
        x="groups",
        y="area",
        orientation="h",
        title="Care Groups by Area",
        color="groups",
        color_continuous_scale=["#fdcb6e", "#00b894"],
    )
    fig.update_layout(
        **LIGHT_LAYOUT,
        showlegend=False,
        coloraxis_showscale=False,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def strength_pie_chart(df: pd.DataFrame) -> go.Figure:
    """Pie chart: Strong / Medium / Weak distribution."""
    strength_counts = df["strength"].value_counts().reset_index()
    strength_counts.columns = ["strength", "count"]

    fig = px.pie(
        strength_counts,
        values="count",
        names="strength",
        title="Group Strength Distribution",
        color="strength",
        color_discrete_map=STRENGTH_COLORS,
        hole=0.4,
    )
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#333333", size=12),
        title_font=dict(color="#222222", size=16),
        legend=dict(font=dict(color="#333333")),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig.update_traces(textfont=dict(color="#333333"))
    return fig


def meeting_day_chart(df: pd.DataFrame) -> go.Figure:
    """Donut chart: distribution of meeting days across care groups."""
    day_counts = df[df["meeting_day"].str.strip() != ""].groupby("meeting_day").size().reset_index()
    day_counts.columns = ["day", "count"]
    day_counts = day_counts.sort_values("count", ascending=False)

    day_colors = ["#00b894", "#74b9ff", "#a29bfe", "#fdcb6e", "#fab1a0", "#ff7675", "#55efc4"]

    fig = px.pie(
        day_counts,
        values="count",
        names="day",
        title="Meeting Day Distribution",
        hole=0.4,
        color_discrete_sequence=day_colors,
    )
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#333333", size=12),
        title_font=dict(color="#222222", size=16),
        legend=dict(font=dict(color="#333333")),
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig.update_traces(textfont=dict(color="#333333"))
    return fig


def top_bottom_groups_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar showing top 5 and bottom 5 care groups by members."""
    sorted_df = df.sort_values("members", ascending=False)
    top5 = sorted_df.head(5)
    bottom5 = sorted_df.tail(5)
    combined = pd.concat([bottom5, top5])

    colors = ["#e17055"] * len(bottom5) + ["#00b894"] * len(top5)

    fig = go.Figure(go.Bar(
        y=combined["leader_name"] + " (" + combined["area"] + ")",
        x=combined["members"],
        orientation="h",
        marker_color=colors,
        text=combined["members"],
        textposition="auto",
        textfont=dict(color="#ffffff"),
    ))
    fig.update_layout(
        title="Top 5 & Bottom 5 Groups by Members",
        **LIGHT_LAYOUT,
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
    )
    return fig


def leader_members_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart: total members managed by each leader."""
    leader_data = df.groupby("leader_name").agg(
        members=("members", "sum"),
        groups=("lg_group", "count"),
    ).sort_values("members", ascending=True).reset_index()

    fig = go.Figure(go.Bar(
        y=leader_data["leader_name"],
        x=leader_data["members"],
        orientation="h",
        marker_color="#a29bfe",
        text=leader_data["members"],
        textposition="auto",
        textfont=dict(color="#ffffff"),
    ))
    fig.update_layout(
        title="Total Members per Leader",
        **LIGHT_LAYOUT,
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
    )
    return fig


def area_detail_table(df: pd.DataFrame, area: str) -> pd.DataFrame:
    """Return filtered dataframe for drill-down display."""
    area_df = df[df["area"] == area][[
        "lg_group", "leader_name", "families", "individuals", "members", "meeting_day", "strength"
    ]].copy()
    area_df.columns = ["Care Group", "Leader", "Families", "Individuals", "Total", "Meeting Day", "Strength"]
    return area_df.sort_values("Total", ascending=False).reset_index(drop=True)
