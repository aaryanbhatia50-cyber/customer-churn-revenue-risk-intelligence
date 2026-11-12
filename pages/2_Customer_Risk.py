
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.styling import apply_theme
from utils.model_utils import generate_customer_risk


apply_theme()

st.markdown(
    "<p class='eyebrow'>CUSTOMER INTELLIGENCE / RISK ANALYSIS</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='hero-title'>Customer Risk Analysis</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='hero-subtitle'>"
    "Identify customers with elevated model scores, explore behavioural "
    "patterns and prioritise retention opportunities."
    "</p>",
    unsafe_allow_html=True
)

st.divider()


try:
    df, metadata = generate_customer_risk()

    if df.empty:
        st.warning("No customer records are available.")
        st.stop()

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])

    threshold = float(metadata["classification_threshold"])

    total_customers = len(df)
    high_risk = int((df["risk_segment"] == "High").sum())
    medium_risk = int((df["risk_segment"] == "Medium").sum())
    low_risk = int((df["risk_segment"] == "Low").sum())
    predicted_churn = int(df["churn_prediction"].sum())
    avg_score = float(df["churn_score"].mean())

    st.markdown(
        "<p class='eyebrow'>THE RISK LANDSCAPE</p>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Customers Analysed", f"{total_customers:,}")
    col2.metric("High Relative Risk", f"{high_risk:,}")
    col3.metric("Predicted Churn", f"{predicted_churn:,}")
    col4.metric("Average Model Score", f"{avg_score:.1%}")

    st.caption(
        f"Model: {metadata['selected_model']} | "
        f"Classification threshold: {threshold:.2f} | "
        f"Snapshot: {df['snapshot_date'].max():%d %B %Y}"
    )

    st.divider()

    left, right = st.columns([1, 1.5])

    with left:
        st.subheader("Relative Risk Distribution")

        risk_counts = (
            df["risk_segment"]
            .value_counts()
            .reindex(["High", "Medium", "Low"], fill_value=0)
            .rename_axis("Risk Segment")
            .reset_index(name="Customers")
        )

        fig = px.pie(
            risk_counts,
            names="Risk Segment",
            values="Customers",
            hole=0.68,
            color="Risk Segment",
            color_discrete_map={
                "High": "#B22222",
                "Medium": "#8B7D72",
                "Low": "#D8CBB9"
            }
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            pull=[0.06, 0, 0],
            hovertemplate=(
                "<b>%{label} Risk</b><br>"
                "Customers: %{value:,.0f}<br>"
                "Share: %{percent}<extra></extra>"
            ),
            marker=dict(
                line=dict(color="#191714", width=3)
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#191714",
            plot_bgcolor="#191714",
            font=dict(color="#E8DFD1"),
            height=360,
            margin=dict(l=10, r=10, t=20, b=20),
            legend=dict(
                orientation="h",
                y=-0.1,
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
        st.subheader("Churn Score Distribution")

        fig = px.histogram(
            df,
            x="churn_score",
            nbins=35,
            color_discrete_sequence=["#B22222"],
            labels={
                "churn_score": "Model Churn Score"
            }
        )

        fig.add_vline(
            x=threshold,
            line_dash="dash",
            line_color="#E8DFD1",
            annotation_text=f"{threshold:.2f} threshold",
            annotation_position="top"
        )

        fig.update_traces(
            marker_line_color="#191714",
            marker_line_width=1,
            hovertemplate=(
                "Model Score: %{x:.2f}<br>"
                "Customers: %{y:,}<extra></extra>"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#191714",
            plot_bgcolor="#191714",
            font=dict(color="#E8DFD1"),
            height=360,
            margin=dict(l=15, r=15, t=30, b=20),
            showlegend=False,
            xaxis_title="Model Churn Score",
            yaxis_title="Number of Customers"
        )

        fig.update_xaxes(
            gridcolor="#39332D",
            range=[0, 1]
        )

        fig.update_yaxes(gridcolor="#39332D")

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>CUSTOMER SEGMENTATION</p>",
        unsafe_allow_html=True
    )

    segment_columns = st.columns(3)

    segment_details = [
        ("HIGH RISK", high_risk, "#B22222"),
        ("MEDIUM RISK", medium_risk, "#8B7D72"),
        ("LOW RISK", low_risk, "#D8CBB9")
    ]

    for column, (segment, count, color) in zip(
        segment_columns, segment_details
    ):
        with column:
            with st.container(border=True):
                st.markdown(
                    f"<span style='color:{color};"
                    f"font-size:13px;font-weight:700;"
                    f"letter-spacing:2px;'>{segment}</span>",
                    unsafe_allow_html=True
                )

                st.metric(
                    "Customers",
                    f"{count:,}",
                    label_visibility="collapsed"
                )

                st.caption(
                    f"{count / total_customers * 100:.1f}% of customers"
                )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>CUSTOMER EXPLORER</p>",
        unsafe_allow_html=True
    )

    filter1, filter2, filter3 = st.columns(3)

    with filter1:
        selected_risk = st.multiselect(
            "Risk Segment",
            ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"]
        )

    with filter2:
        locations = sorted(
            df["location"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_locations = st.multiselect(
            "Location",
            locations
        )

    with filter3:
        occupations = sorted(
            df["occupation"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_occupations = st.multiselect(
            "Occupation",
            occupations
        )

    filtered = df[
        df["risk_segment"].isin(selected_risk)
    ].copy()

    if selected_locations:
        filtered = filtered[
            filtered["location"]
            .astype(str)
            .isin(selected_locations)
        ]

    if selected_occupations:
        filtered = filtered[
            filtered["occupation"]
            .astype(str)
            .isin(selected_occupations)
        ]

    display_df = filtered.sort_values(
        "churn_score",
        ascending=False
    )

    st.write(f"**{len(display_df):,} customers found**")

    if not display_df.empty:
        customer_table = display_df[
            [
                "customer_id",
                "location",
                "occupation",
                "churn_score",
                "risk_segment",
                "churn_prediction"
            ]
        ].rename(
            columns={
                "customer_id": "Customer ID",
                "location": "Location",
                "occupation": "Occupation",
                "churn_score": "Churn Score",
                "risk_segment": "Risk Segment",
                "churn_prediction": "Predicted Churn"
            }
        )

        st.dataframe(
            customer_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Churn Score": st.column_config.ProgressColumn(
                    "Churn Score",
                    format="%.1f",
                    min_value=0,
                    max_value=1
                ),
                "Predicted Churn": st.column_config.NumberColumn(
                    "Predicted Churn",
                    format="%d"
                )
            }
        )

    else:
        st.info(
            "No customers match the selected filters. "
            "Adjust your selections to continue."
        )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>INDIVIDUAL CUSTOMER PROFILE</p>",
        unsafe_allow_html=True
    )

    if not filtered.empty:
        customer_options = (
            filtered["customer_id"]
            .astype(str)
            .tolist()
        )

        selected_customer = st.selectbox(
            "Select a customer to explore",
            customer_options
        )

        customer = filtered[
            filtered["customer_id"].astype(str)
            == selected_customer
        ].iloc[0]

        profile1, profile2, profile3 = st.columns(3)

        profile1.metric(
            "Customer ID",
            str(customer["customer_id"])
        )

        profile2.metric(
            "Model Churn Score",
            f"{customer['churn_score']:.1%}"
        )

        profile3.metric(
            "Relative Risk Segment",
            customer["risk_segment"]
        )

        st.subheader("Customer Behaviour Profile")

        behaviour_labels = {
            "tx_count_90d": "90-Day Transaction Count",
            "total_amount_90d": "Total Transaction Value (90 Days)",
            "avg_amount_90d": "Average Transaction Value",
            "active_days_90d": "Active Transaction Days",
            "days_since_last_tx": "Days Since Last Transaction",
            "avg_tx_per_active_day": "Transactions per Active Day"
        }

        behaviour_data = []

        for feature, label in behaviour_labels.items():
            if feature not in customer.index:
                continue

            value = customer[feature]

            if pd.isna(value):
                formatted_value = "Not Available"

            elif feature in [
                "total_amount_90d",
                "avg_amount_90d"
            ]:
                formatted_value = f"{value:,.2f}"

            elif feature == "avg_tx_per_active_day":
                formatted_value = f"{value:.2f}"

            else:
                formatted_value = f"{value:,.0f}"

            behaviour_data.append({
                "Behavioural Indicator": label,
                "Customer Value": formatted_value
            })

        behaviour_df = pd.DataFrame(behaviour_data)

        st.dataframe(
            behaviour_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "Select filters that return at least one customer "
            "to view an individual profile."
        )

    st.divider()

    with st.container(border=True):
        st.markdown(
            "<p class='eyebrow'>RISK INTELLIGENCE FINDING</p>",
            unsafe_allow_html=True
        )

        st.subheader(
            f"{high_risk:,} customers fall into the "
            "highest relative risk segment."
        )

        st.write(
            "These customers have the highest model churn scores "
            "relative to other customers in the latest snapshot. "
            "They can be prioritised for further retention investigation."
        )

    st.caption(
        "Scores are model outputs, not calibrated probabilities. "
        "Low, Medium and High categories are relative quantile-based "
        "segments. The classification threshold determines binary "
        "model predictions."
    )

except Exception as error:
    st.error("Unable to load Customer Risk Analysis.")
    st.exception(error)
