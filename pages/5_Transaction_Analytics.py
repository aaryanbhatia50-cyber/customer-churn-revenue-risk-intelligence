
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.styling import apply_theme
from utils.database import run_query

apply_theme()

st.markdown(
    "<p class='eyebrow'>CUSTOMER INTELLIGENCE / TRANSACTION ANALYSIS</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='hero-title'>Transaction Analytics</div>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class='hero-subtitle'>
    Explore transaction patterns, customer activity and historical
    transaction value to understand how customers interact with the platform.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

try:

    date_range = run_query("""
        SELECT
            MIN(date)::DATE AS min_date,
            MAX(date)::DATE AS max_date
        FROM transactions
    """)

    if date_range.empty or pd.isna(date_range.iloc[0]["min_date"]):
        st.warning("No transaction records are available.")
        st.stop()

    min_date = pd.to_datetime(
        date_range.iloc[0]["min_date"]
    ).date()

    max_date = pd.to_datetime(
        date_range.iloc[0]["max_date"]
    ).date()

    date_col1, date_col2 = st.columns(2)

    with date_col1:
        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

    with date_col2:
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    if start_date > end_date:
        st.error("Start date cannot be later than end date.")
        st.stop()

    start_date_sql = start_date.isoformat()
    end_date_sql = end_date.isoformat()

    transaction_kpis = run_query(f"""
        SELECT
            COUNT(*) AS total_transactions,
            COUNT(DISTINCT customer_id) AS active_customers,
            COALESCE(SUM(amount), 0) AS total_transaction_value,
            COALESCE(AVG(amount), 0) AS average_transaction_value
        FROM transactions
        WHERE date::DATE BETWEEN
            DATE '{start_date_sql}' AND DATE '{end_date_sql}'
    """)

    monthly_data = run_query(f"""
        SELECT
            DATE_TRUNC('month', date)::DATE AS transaction_month,
            COUNT(*) AS transaction_count,
            COUNT(DISTINCT customer_id) AS active_customers,
            SUM(amount) AS transaction_value,
            AVG(amount) AS average_amount
        FROM transactions
        WHERE date::DATE BETWEEN
            DATE '{start_date_sql}' AND DATE '{end_date_sql}'
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY transaction_month
    """)

    daily_data = run_query(f"""
        SELECT
            date::DATE AS transaction_date,
            COUNT(*) AS transaction_count,
            SUM(amount) AS transaction_value
        FROM transactions
        WHERE date::DATE BETWEEN
            DATE '{start_date_sql}' AND DATE '{end_date_sql}'
        GROUP BY date::DATE
        ORDER BY transaction_date
    """)

    top_customers = run_query(f"""
        SELECT
            customer_id,
            COUNT(*) AS transaction_count,
            SUM(amount) AS total_transaction_value,
            AVG(amount) AS average_transaction_value
        FROM transactions
        WHERE date::DATE BETWEEN
            DATE '{start_date_sql}' AND DATE '{end_date_sql}'
        GROUP BY customer_id
        ORDER BY total_transaction_value DESC
        LIMIT 10
    """)

    transaction_distribution = run_query(f"""
        SELECT
            CASE
                WHEN amount < 0 THEN 'Negative Amount'
                WHEN amount = 0 THEN 'Zero Amount'
                ELSE 'Positive Amount'
            END AS amount_category,
            COUNT(*) AS transaction_count,
            SUM(ABS(amount)) AS absolute_transaction_value
        FROM transactions
        WHERE date::DATE BETWEEN
            DATE '{start_date_sql}' AND DATE '{end_date_sql}'
        GROUP BY amount_category
        ORDER BY transaction_count DESC
    """)

    type_columns = run_query("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'transactions'
        ORDER BY ordinal_position
    """)

    available_columns = (
        type_columns["column_name"].tolist()
        if not type_columns.empty else []
    )

    possible_type_columns = [
        "transaction_type",
        "type",
        "transaction_category"
    ]

    type_column = next(
        (
            column for column in possible_type_columns
            if column in available_columns
        ),
        None
    )

    type_data = pd.DataFrame()

    if type_column:

        type_data = run_query(f"""
            SELECT
                COALESCE(
                    NULLIF(TRIM({type_column}::TEXT), ''),
                    'Unknown'
                ) AS transaction_type,
                COUNT(*) AS transaction_count,
                SUM(amount) AS transaction_value
            FROM transactions
            WHERE date::DATE BETWEEN
                DATE '{start_date_sql}' AND DATE '{end_date_sql}'
            GROUP BY 1
            ORDER BY transaction_count DESC
        """)

    total_transactions = int(
        transaction_kpis.iloc[0]["total_transactions"]
    )

    active_customers = int(
        transaction_kpis.iloc[0]["active_customers"]
    )

    total_value = float(
        transaction_kpis.iloc[0]["total_transaction_value"]
    )

    average_value = float(
        transaction_kpis.iloc[0]["average_transaction_value"]
    )

    st.markdown(
        "<p class='eyebrow'>TRANSACTION LANDSCAPE</p>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Transactions",
        f"{total_transactions:,}"
    )

    col2.metric(
        "Active Customers",
        f"{active_customers:,}"
    )

    col3.metric(
        "Total Transaction Value",
        f"{total_value:,.0f}"
    )

    col4.metric(
        "Average Transaction Value",
        f"{average_value:,.2f}"
    )

    st.caption(
        f"Showing transaction records from {start_date} to {end_date}. "
        "Transaction value is historical transaction activity, "
        "not company revenue or profit."
    )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>TRANSACTION ACTIVITY TRENDS</p>",
        unsafe_allow_html=True
    )

    st.subheader("Monthly Transaction Performance")

    if not monthly_data.empty:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=monthly_data["transaction_month"],
                y=monthly_data["transaction_value"],
                mode="lines+markers",
                name="Transaction Value",
                line=dict(color="#B22222", width=3),
                marker=dict(size=8),
                fill="tozeroy",
                fillcolor="rgba(178,34,34,0.12)",
                customdata=monthly_data[
                    ["transaction_count", "active_customers"]
                ],
                hovertemplate=(
                    "<b>%{x|%B %Y}</b><br>"
                    "Transaction Value: %{y:,.2f}<br>"
                    "Transactions: %{customdata[0]:,}<br>"
                    "Active Customers: %{customdata[1]:,}"
                    "<extra></extra>"
                )
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#191714",
            plot_bgcolor="#191714",
            font=dict(color="#E8DFD1"),
            height=410,
            margin=dict(l=20, r=20, t=25, b=20),
            yaxis_title="Transaction Value",
            xaxis_title=None,
            hovermode="x unified",
            showlegend=False
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#39332D")

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        left, right = st.columns(2)

        with left:

            fig = px.bar(
                monthly_data,
                x="transaction_month",
                y="transaction_count",
                color_discrete_sequence=["#B22222"],
                text="transaction_count"
            )

            fig.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside",
                hovertemplate=(
                    "<b>%{x|%B %Y}</b><br>"
                    "Transactions: %{y:,}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#191714",
                plot_bgcolor="#191714",
                font=dict(color="#E8DFD1"),
                height=350,
                margin=dict(l=15, r=15, t=25, b=15),
                xaxis_title=None,
                yaxis_title="Transaction Count",
                showlegend=False
            )

            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#39332D")

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        with right:

            fig = px.bar(
                monthly_data,
                x="transaction_month",
                y="active_customers",
                color_discrete_sequence=["#8B7D72"],
                text="active_customers"
            )

            fig.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside",
                hovertemplate=(
                    "<b>%{x|%B %Y}</b><br>"
                    "Active Customers: %{y:,}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#191714",
                plot_bgcolor="#191714",
                font=dict(color="#E8DFD1"),
                height=350,
                margin=dict(l=15, r=15, t=25, b=15),
                xaxis_title=None,
                yaxis_title="Active Customers",
                showlegend=False
            )

            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#39332D")

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    else:
        st.info("No monthly transaction data is available for this period.")

    st.divider()

    st.markdown(
        "<p class='eyebrow'>TRANSACTION COMPOSITION</p>",
        unsafe_allow_html=True
    )

    if not type_data.empty:

        st.subheader("Transaction Activity by Type")

        left, right = st.columns(2)

        with left:

            fig = px.pie(
                type_data,
                names="transaction_type",
                values="transaction_count",
                hole=0.65,
                color_discrete_sequence=[
                    "#B22222",
                    "#8B7D72",
                    "#D8CBB9",
                    "#6F554B"
                ]
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Transactions: %{value:,}<br>"
                    "Share: %{percent}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#191714",
                plot_bgcolor="#191714",
                font=dict(color="#E8DFD1"),
                height=370,
                margin=dict(l=15, r=15, t=20, b=15)
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        with right:

            fig = px.bar(
                type_data,
                x="transaction_type",
                y="transaction_value",
                color="transaction_type",
                color_discrete_sequence=[
                    "#B22222",
                    "#8B7D72",
                    "#D8CBB9",
                    "#6F554B"
                ],
                text="transaction_value"
            )

            fig.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside",
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Transaction Value: %{y:,.2f}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#191714",
                plot_bgcolor="#191714",
                font=dict(color="#E8DFD1"),
                height=370,
                margin=dict(l=15, r=25, t=20, b=15),
                showlegend=False,
                xaxis_title=None,
                yaxis_title="Transaction Value"
            )

            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#39332D")

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    else:
        st.info(
            "No recognised transaction-type column was found. "
            "Transaction type charts are therefore not displayed."
        )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>CUSTOMER CONTRIBUTION</p>",
        unsafe_allow_html=True
    )

    st.subheader("Top 10 Customers by Transaction Value")

    if not top_customers.empty:

        fig = px.bar(
            top_customers.sort_values(
                "total_transaction_value",
                ascending=True
            ),
            x="total_transaction_value",
            y="customer_id",
            orientation="h",
            color="total_transaction_value",
            color_continuous_scale=["#8B7D72", "#B22222"],
            text="total_transaction_value"
        )

        fig.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            hovertemplate=(
                "<b>Customer: %{y}</b><br>"
                "Transaction Value: %{x:,.2f}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#191714",
            plot_bgcolor="#191714",
            font=dict(color="#E8DFD1"),
            height=470,
            margin=dict(l=20, r=70, t=25, b=20),
            coloraxis_showscale=False,
            xaxis_title="Historical Transaction Value",
            yaxis_title=None
        )

        fig.update_xaxes(gridcolor="#39332D")
        fig.update_yaxes(showgrid=False)

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        display_top = top_customers.copy()

        display_top.columns = [
            "Customer ID",
            "Transaction Count",
            "Total Transaction Value",
            "Average Transaction Value"
        ]

        st.dataframe(
            display_top,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No customer transaction records found.")

    st.divider()

    st.markdown(
        "<p class='eyebrow'>TRANSACTION VALUE DISTRIBUTION</p>",
        unsafe_allow_html=True
    )

    st.subheader("Transaction Amount Composition")

    if not transaction_distribution.empty:

        fig = px.pie(
            transaction_distribution,
            names="amount_category",
            values="transaction_count",
            hole=0.68,
            color="amount_category",
            color_discrete_map={
                "Positive Amount": "#8B7D72",
                "Negative Amount": "#B22222",
                "Zero Amount": "#D8CBB9"
            }
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Transactions: %{value:,}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#191714",
            plot_bgcolor="#191714",
            font=dict(color="#E8DFD1"),
            height=370,
            margin=dict(l=20, r=20, t=25, b=20),
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

    st.divider()

    st.markdown(
        "<p class='eyebrow'>TRANSACTION INTELLIGENCE FINDINGS</p>",
        unsafe_allow_html=True
    )

    with st.container(border=True):

        st.caption("PERIOD SUMMARY")

        st.subheader(
            f"{total_transactions:,} transactions "
            f"across {active_customers:,} active customers."
        )

        st.markdown(
            f"### Average transaction value: {average_value:,.2f}"
        )

        if not monthly_data.empty:

            highest_month = monthly_data.loc[
                monthly_data["transaction_value"].idxmax()
            ]

            st.write(
                f"The highest transaction value was recorded in "
                f"{pd.to_datetime(highest_month['transaction_month']).strftime('%B %Y')}, "
                f"with a historical transaction value of "
                f"{highest_month['transaction_value']:,.2f}."
            )

        st.write(
            "Use the customer contribution and transaction composition "
            "charts to identify activity concentration and investigate "
            "unusual transaction patterns."
        )

    st.caption(
        "All transaction metrics are calculated from the transactions "
        "table for the selected date range. Historical transaction "
        "amounts should not be interpreted as company revenue or profit."
    )

except Exception as error:

    st.error("Unable to load Transaction Analytics.")
    st.exception(error)
