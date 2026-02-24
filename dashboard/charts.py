"""Pure functions that turn DataFrames into Plotly figures."""

import plotly.express as px
import plotly.graph_objects as go


def create_unemployment_chart(unrate):
    """Build the U.S. Unemployment Rate interactive Plotly figure.

    Parameters
    ----------
    unrate : pandas.DataFrame
        Must contain ``date`` (datetime) and ``value`` (float) columns.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    fig = px.line(unrate, x="date", y="value", title="U.S. Unemployment Rate")

    # Highlight the most recent data point
    latest_date = unrate["date"].iloc[-1]
    latest_value = unrate["value"].iloc[-1]

    fig.add_trace(
        go.Scatter(
            x=[latest_date],
            y=[latest_value],
            mode="markers+text",
            marker=dict(color="red", size=12),
            text=[f"{latest_value:.1f}%"],
            textposition="top center",
            showlegend=False,
        )
    )

    # 3-month rolling average trend line
    if len(unrate) >= 3:
        rolling_3 = unrate["value"].rolling(3).mean()
        fig.add_trace(
            go.Scatter(
                x=unrate["date"],
                y=rolling_3,
                mode="lines",
                line=dict(dash="dash", color="blue"),
                name="3-Month Rolling Avg",
            )
        )

    fig.update_layout(
        template="plotly_white",
        title={"text": "U.S. Unemployment Rate (Monthly)", "x": 0.5, "xanchor": "center"},
        xaxis_title="Date",
        yaxis_title="Unemployment Rate (%)",
        font=dict(family="Arial", size=14, color="#2a3f5f"),
        xaxis=dict(showgrid=True, gridcolor="#e6e6e6", tickformat="%b %Y"),
        yaxis=dict(showgrid=True, gridcolor="#e6e6e6", ticksuffix="%"),
        margin=dict(l=60, r=40, t=80, b=60),
        hovermode="x unified",
        dragmode=False,
        hoverlabel=dict(bgcolor="white", font_size=13),
    )

    return fig
