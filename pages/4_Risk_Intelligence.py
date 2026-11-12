
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from utils.styling import apply_theme

apply_theme()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RISK_PATH = PROJECT_ROOT / "reports" / "risk_intelligence_summary.csv"

st.markdown(
    "<p class='eyebrow'>CUSTOMER INTELLIGENCE / RISK ANALYSIS</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='hero-title'>Risk Intelligence</div>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class='hero-subtitle'>
    Identify high-priority customer segments and understand
    where historical transaction activity is concentrated.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

if not RISK_PATH.exists():
    st.error(f"Risk intelligence file not found: {RISK_PATH}")
    st.stop()

try:
    risk_df = pd.read_csv(RISK_PATH)

    required_columns = [
        "risk_category",
        "customer_count",
        "average_churn_score",
        "historical_transaction_value",
        "average_transaction_value",
        "total_transactions",
        "customer_percentage",
        "transaction_value_percentage"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in risk_df.columns
    ]

    if missing_columns:
        st.error(f"Missing columns: {missing_columns}")
        st.write("Available columns:", risk_df.columns.tolist())
        st.stop()

    numeric_columns = [
        "customer_count",
        "average_churn_score",
        "historical_transaction_value",
        "average_transaction_value",
        "total_transactions",
        "customer_percentage",
        "transaction_value_percentage"
    ]

    for col in numeric_columns:
        risk_df[col] = pd.to_numeric(
            risk_df[col],
            errors="coerce"
        )

    risk_df = risk_df.dropna(
        subset=numeric_columns
    ).copy()

    risk_order = ["Low Risk", "Medium Risk", "High Risk"]

    risk_df["risk_category"] = (
        risk_df["risk_category"]
        .astype(str)
        .str.strip()
        .replace({
            "Low": "Low Risk",
            "Medium": "Medium Risk",
            "High": "High Risk"
        })
    )

    risk_df = risk_df[
        risk_df["risk_category"].isin(risk_order)
    ].copy()

    risk_df["risk_category"] = pd.Categorical(
        risk_df["risk_category"],
        categories=risk_order,
        ordered=True
    )

    risk_df = risk_df.sort_values(
        "risk_category"
    ).reset_index(drop=True)

    if risk_df.empty:
        st.warning("No valid risk segment data available.")
        st.stop()

    risk_colors = {
        "High Risk": "#B22222",
        "Medium Risk": "#8B7D72",
        "Low Risk": "#D8CBB9"
    }

    total_customers = int(
        risk_df["customer_count"].sum()
    )

    total_transactions = int(
        risk_df["total_transactions"].sum()
    )

    high_risk = risk_df[
        risk_df["risk_category"] == "High Risk"
    ]

    if high_risk.empty:
        st.warning("High-risk segment is missing.")
        st.stop()

    high_risk_customers = int(
        high_risk["customer_count"].sum()
    )

    high_risk_percentage = (
        high_risk_customers / total_customers * 100
        if total_customers else 0
    )

    high_risk_transaction_share = float(
        high_risk["transaction_value_percentage"].sum()
    )

    weighted_average_churn_score = (
        risk_df["average_churn_score"]
        * risk_df["customer_count"]
    ).sum() / total_customers

    st.markdown(
        "<p class='eyebrow'>THE RISK LANDSCAPE</p>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Customers Analysed",
        f"{total_customers:,}"
    )

    col2.metric(
        "High-Risk Customers",
        f"{high_risk_customers:,}"
    )

    col3.metric(
        "90-Day Transactions",
        f"{total_transactions:,}"
    )

    col4.metric(
        "Average Churn Score",
        f"{weighted_average_churn_score:.3f}"
    )

    st.caption(
        "Average churn score is a model output, not a calibrated probability."
    )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>CUSTOMER RISK SEGMENTATION</p>",
        unsafe_allow_html=True
    )

    st.subheader("Customer Distribution Across Risk Levels")

    left, right = st.columns(2)

    with left:

        fig = px.pie(
            risk_df,
            names="risk_category",
            values="customer_count",
            hole=0.68,
            color="risk_category",
            color_discrete_map=risk_colors
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            pull=[
                0.07 if str(category) == "High Risk" else 0
                for category in risk_df["risk_category"]
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
            height=380,
            margin=dict(l=20, r=20, t=25, b=20),
            legend=dict(
                orientation="h",
                y=-0.12,
                x=0.5,
                xanchor="center"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    with right:

        fig = px.bar(
            risk_df,
            x="risk_category",
            y="customer_count",
            color="risk_category",
            color_discrete_map=risk_colors,
            text="customer_count"
        )

        fig.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Customers: %{y:,}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#191714",
            plot_bgcolor="#191714",
            font=dict(color="#E8DFD1"),
            height=380,
            showlegend=False,
            margin=dict(l=20, r=30, t=25, b=20)
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#39332D")

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>TRANSACTION VALUE ANALYSIS</p>",
        unsafe_allow_html=True
    )

    st.subheader("Historical Transaction Value by Risk Segment")

    fig = px.bar(
        risk_df,
        x="risk_category",
        y="historical_transaction_value",
        color="risk_category",
        color_discrete_map=risk_colors,
        text="historical_transaction_value"
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Historical Transaction Value: %{y:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#191714",
        plot_bgcolor="#191714",
        font=dict(color="#E8DFD1"),
        height=420,
        showlegend=False,
        margin=dict(l=20, r=60, t=30, b=25)
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#39332D")

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>CUSTOMER SHARE VS TRANSACTION VALUE SHARE</p>",
        unsafe_allow_html=True
    )

    st.subheader("Customer Concentration vs Transaction Value")

    comparison_df = risk_df.melt(
        id_vars="risk_category",
        value_vars=[
            "customer_percentage",
            "transaction_value_percentage"
        ],
        var_name="measure",
        value_name="percentage"
    )

    comparison_df["measure"] = comparison_df["measure"].replace({
        "customer_percentage": "Share of Customers",
        "transaction_value_percentage": "Share of Transaction Value"
    })

    fig = px.bar(
        comparison_df,
        x="risk_category",
        y="percentage",
        color="measure",
        barmode="group",
        text="percentage",
        color_discrete_map={
            "Share of Customers": "#8B7D72",
            "Share of Transaction Value": "#B22222"
        },
        category_orders={
            "risk_category": risk_order
        }
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{fullData.name}: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#191714",
        plot_bgcolor="#191714",
        font=dict(color="#E8DFD1"),
        height=430,
        margin=dict(l=20, r=30, t=30, b=25),
        legend=dict(
            orientation="h",
            y=1.12,
            x=0.5,
            xanchor="center"
        )
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(
        gridcolor="#39332D",
        ticksuffix="%"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>RISK INTELLIGENCE FINDING</p>",
        unsafe_allow_html=True
    )

    with st.container(border=True):

        st.caption("RETENTION PRIORITY")

        st.subheader(
            f"{high_risk_customers:,} customers "
            f"({high_risk_percentage:.1f}%)"
        )

        st.markdown(
            f"### {high_risk_transaction_share:.1f}% of historical "
            "transaction value belongs to the high-risk segment."
        )

        st.write(
            "These customers should be prioritised for further "
            "retention investigation based on their relative churn "
            "scores and historical transaction activity."
        )

    st.caption(
        "Risk categories are relative quantile-based segments. "
        "Transaction value represents historical customer transaction "
        "activity, not company revenue or profit. "
        "Model churn scores are not calibrated probabilities."
    )

    st.divider()

    st.markdown(
        "<div class='section-heading'>Risk Segment Summary</div>",
        unsafe_allow_html=True
    )

    display_df = risk_df[
        [
            "risk_category",
            "customer_count",
            "average_churn_score",
            "historical_transaction_value",
            "average_transaction_value",
            "total_transactions",
            "customer_percentage",
            "transaction_value_percentage"
        ]
    ].copy()

    display_df.columns = [
        "Risk Segment",
        "Customers",
        "Average Churn Score",
        "Historical Transaction Value",
        "Average Transaction Value",
        "Total Transactions",
        "Customer Share (%)",
        "Transaction Value Share (%)"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

except Exception as error:
    st.error("Unable to load Risk Intelligence.")
    st.exception(error)
