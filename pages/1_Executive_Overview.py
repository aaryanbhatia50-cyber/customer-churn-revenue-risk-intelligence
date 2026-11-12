
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.styling import apply_theme
from utils.database import run_query

apply_theme()

st.markdown(
    "<p class='eyebrow'>CUSTOMER INTELLIGENCE / OVERVIEW</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='hero-title'>Customer Churn &<br>"
    "Revenue Risk Intelligence</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='hero-subtitle'>"
    "Understand customer behaviour. Identify churn patterns. "
    "Prioritise retention opportunities."
    "</p>",
    unsafe_allow_html=True
)

st.markdown("---")

try:
    kpi_data = run_query("""
        SELECT
            COUNT(*) AS total_customers,
            COALESCE(SUM(churn), 0) AS churned_customers,
            ROUND(
                100.0 * COALESCE(SUM(churn), 0)
                / NULLIF(COUNT(*), 0),
                2
            ) AS churn_rate
        FROM latest_customers
    """)

    transaction_data = run_query("""
        SELECT
            COUNT(*) AS total_transactions,
            COALESCE(SUM(amount), 0) AS transaction_value
        FROM transactions
        WHERE date > (
            SELECT MAX(snapshot_date) - INTERVAL '90 days'
            FROM customer_snapshots
        )
        AND date <= (
            SELECT MAX(snapshot_date)
            FROM customer_snapshots
        )
    """)

    monthly_data = run_query("""
        SELECT
            DATE_TRUNC('month', date)::DATE AS transaction_month,
            COUNT(*) AS transaction_count,
            SUM(amount) AS transaction_value
        FROM transactions
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY transaction_month
    """)

    churn_data = run_query("""
        SELECT
            CASE
                WHEN churn = 1 THEN 'Churned'
                ELSE 'Retained'
            END AS churn_status,
            COUNT(*) AS customer_count
        FROM latest_customers
        GROUP BY churn
    """)

    activity_data = run_query("""
        SELECT
            snapshot_date,
            COUNT(*) AS total_customers,
            COALESCE(SUM(churn), 0) AS churned_customers,
            COUNT(*) - COALESCE(SUM(churn), 0)
                AS retained_customers
        FROM customer_snapshots
        GROUP BY snapshot_date
        ORDER BY snapshot_date
    """)

    customers = int(kpi_data.iloc[0]["total_customers"])
    churned = int(kpi_data.iloc[0]["churned_customers"])
    churn_rate = float(kpi_data.iloc[0]["churn_rate"])

    transactions = int(
        transaction_data.iloc[0]["total_transactions"]
    )

    transaction_value = float(
        transaction_data.iloc[0]["transaction_value"]
    )

    retained = customers - churned

    st.markdown(
        "<p class='eyebrow'>THE CUSTOMER LANDSCAPE</p>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Customers",
        f"{customers:,}"
    )

    col2.metric(
        "Churn Rate",
        f"{churn_rate:.2f}%"
    )

    col3.metric(
        "90-Day Transactions",
        f"{transactions:,}"
    )

    col4.metric(
        "90-Day Transaction Value",
        f"{transaction_value:,.0f}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1.6, 1])

    with left:
        st.markdown(
            "<div class='section-heading'>Transaction Activity</div>",
            unsafe_allow_html=True
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=monthly_data["transaction_month"],
                y=monthly_data["transaction_value"],
                mode="lines+markers",
                name="Transaction Value",
                line=dict(color="#B22222", width=3),
                marker=dict(size=7, color="#E8DFD1"),
                fill="tozeroy",
                fillcolor="rgba(178,34,34,0.12)",
                customdata=monthly_data[
                    ["transaction_count"]
                ],
                hovertemplate=(
                    "<b>%{x|%b %Y}</b><br>"
                    "Transaction Value: %{y:,.0f}<br>"
                    "Transactions: %{customdata[0]:,}"
                    "<extra></extra>"
                )
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#191714",
            plot_bgcolor="#191714",
            font=dict(color="#E8DFD1"),
            margin=dict(l=15, r=15, t=25, b=15),
            height=360,
            xaxis_title=None,
            yaxis_title="Transaction Value",
            showlegend=False,
            hovermode="x unified"
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#39332D")

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    with right:
        st.markdown(
            "<div class='section-heading'>Customer Distribution</div>",
            unsafe_allow_html=True
        )

        fig = px.pie(
            churn_data,
            names="churn_status",
            values="customer_count",
            hole=0.70,
            color="churn_status",
            color_discrete_map={
                "Churned": "#B22222",
                "Retained": "#8B7D72"
            }
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            textfont=dict(size=14, color="#FFFFFF"),
            marker=dict(
                line=dict(color="#191714", width=3)
            ),
            pull=[
                0.06 if status == "Churned" else 0
                for status in churn_data["churn_status"]
            ],
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Customers: %{value:,}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#191714",
            plot_bgcolor="#191714",
            font=dict(color="#E8DFD1"),
            margin=dict(l=10, r=10, t=20, b=10),
            height=360,
            legend=dict(
                orientation="h",
                y=-0.1,
                x=0.5,
                xanchor="center"
            ),
            showlegend=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    st.markdown(
        f"""
        <div class='insight-panel'>
            <div class='insight-label'>EXECUTIVE SNAPSHOT</div>
            <div style="
                font-family:'Playfair Display',serif;
                font-size:27px;
                font-weight:600;
                color:#E8DFD1;
                margin-top:9px;">
                {churned:,} customers are labelled as churned.
            </div>
            <div class='insight-text'>
                Out of {customers:,} customers in the latest snapshot,
                {retained:,} are labelled as retained.
                The observed churn rate is {churn_rate:.2f}%.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Customer metrics use the latest available snapshot. "
        "Transaction metrics use the 90 days ending on that snapshot date. "
        "Historical transaction value is not company revenue."
    )

    st.markdown("---")

    st.markdown(
        "<p class='eyebrow'>CUSTOMER ACTIVITY ANALYSIS</p>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-heading'>Monthly Customer Activity</div>",
        unsafe_allow_html=True
    )

    if not activity_data.empty:

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=activity_data["snapshot_date"],
                y=activity_data["retained_customers"],
                name="Retained Customers",
                marker_color="#8B7D72",
                hovertemplate=(
                    "<b>%{x|%d %b %Y}</b><br>"
                    "Retained Customers: %{y:,}"
                    "<extra></extra>"
                )
            )
        )

        fig.add_trace(
            go.Bar(
                x=activity_data["snapshot_date"],
                y=activity_data["churned_customers"],
                name="Churned Customers",
                marker_color="#B22222",
                hovertemplate=(
                    "<b>%{x|%d %b %Y}</b><br>"
                    "Churned Customers: %{y:,}"
                    "<extra></extra>"
                )
            )
        )

        fig.update_layout(
            barmode="stack",
            template="plotly_dark",
            paper_bgcolor="#191714",
            plot_bgcolor="#191714",
            font=dict(color="#E8DFD1"),
            height=420,
            margin=dict(l=20, r=20, t=35, b=20),
            xaxis_title=None,
            yaxis_title="Number of Customers",
            legend=dict(
                orientation="h",
                y=1.12,
                x=0.5,
                xanchor="center"
            ),
            hovermode="x unified"
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#39332D")

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        latest_activity = activity_data.iloc[-1]

        retained_percentage = (
            100 * latest_activity["retained_customers"]
            / latest_activity["total_customers"]
            if latest_activity["total_customers"] > 0
            else 0
        )

        churn_percentage = (
            100 * latest_activity["churned_customers"]
            / latest_activity["total_customers"]
            if latest_activity["total_customers"] > 0
            else 0
        )

        st.markdown(
            f"""
            <div class='insight-panel'>
                <div class='insight-label'>
                    CUSTOMER ACTIVITY FINDING
                </div>
                <div style="
                    font-family:'Playfair Display',serif;
                    font-size:27px;
                    font-weight:600;
                    color:#E8DFD1;
                    margin-top:10px;">
                    {int(latest_activity['retained_customers']):,}
                    retained customers
                </div>
                <div class='insight-text'>
                    In the latest snapshot, {retained_percentage:.2f}%
                    of customers were labelled as retained, while
                    {churn_percentage:.2f}% were labelled as churned.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.info("No customer activity data is available.")

    st.caption(
        "Each bar represents the customer composition of a snapshot. "
        "Customers may appear in multiple snapshots. "
        "These counts do not represent newly acquired or newly lost customers."
    )

except Exception as error:
    st.error("Unable to load the Executive Overview.")
    st.code(str(error))
    st.info(
        "Check your PostgreSQL connection, database credentials, "
        "latest_customers view, customer_snapshots table, "
        "and transactions table."
    )
