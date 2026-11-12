
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from utils.styling import apply_theme
from utils.model_utils import generate_customer_risk

apply_theme()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SHAP_PATHS = [
    PROJECT_ROOT / "reports" / "shap_feature_importance.csv",
    PROJECT_ROOT.parent / "reports" / "shap_feature_importance.csv"
]

st.markdown(
    "<p class='eyebrow'>CUSTOMER INTELLIGENCE / MODEL INSIGHTS</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='hero-title'>Model Explainability</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='hero-subtitle'>"
    "Understand the behavioural signals behind churn predictions "
    "and examine what influences customer risk."
    "</p>",
    unsafe_allow_html=True
)

st.divider()

try:
    shap_path = next(
        (path for path in SHAP_PATHS if path.exists()),
        None
    )

    if shap_path is None:
        st.error(
            "SHAP importance file not found. "
            "Check the reports folder."
        )
        st.stop()

    shap_df = pd.read_csv(shap_path)

    required_columns = [
        "Feature",
        "Mean Absolute SHAP"
    ]

    if not all(col in shap_df.columns for col in required_columns):
        st.error("The SHAP CSV has an unexpected column structure.")
        st.stop()

    shap_df["Mean Absolute SHAP"] = pd.to_numeric(
        shap_df["Mean Absolute SHAP"],
        errors="coerce"
    )

    shap_df = shap_df.dropna(
        subset=["Feature", "Mean Absolute SHAP"]
    )

    shap_df = shap_df.sort_values(
        "Mean Absolute SHAP",
        ascending=False
    ).copy()

    shap_df["Feature Label"] = (
        shap_df["Feature"]
        .astype(str)
        .str.replace("_", " ", regex=False)
        .str.title()
    )

    if shap_df.empty:
        st.warning("No valid SHAP importance records found.")
        st.stop()

    df, metadata = generate_customer_risk()

    top_feature = shap_df.iloc[0]["Feature Label"]
    top_value = shap_df.iloc[0]["Mean Absolute SHAP"]

    st.markdown(
        "<p class='eyebrow'>MODEL PERFORMANCE</p>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Churn Cases Detected",
        "87.33%"
    )

    col2.metric(
        "Churn Alerts That Were Correct",
        "27.61%"
    )

    col3.metric(
        "Top Model Driver",
        top_feature
    )

    col4.metric(
        "Features Analysed",
        f"{len(shap_df):,}"
    )

    st.caption(
        "Performance figures are based on the held-out test dataset. "
        "The model prioritises identifying churn cases, even though "
        "some customers flagged as at risk will not churn."
    )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>GLOBAL FEATURE IMPORTANCE</p>",
        unsafe_allow_html=True
    )

    st.subheader("What Drives Customer Churn Predictions?")

    st.write(
        "The chart ranks customer characteristics by their average "
        "contribution magnitude to the model's predictions. "
        "Higher values indicate greater overall influence."
    )

    top_features = shap_df.head(10).sort_values(
        "Mean Absolute SHAP",
        ascending=True
    )

    fig = px.bar(
        top_features,
        x="Mean Absolute SHAP",
        y="Feature Label",
        orientation="h",
        text="Mean Absolute SHAP",
        color="Mean Absolute SHAP",
        color_continuous_scale=[
            "#8B7D72",
            "#B22222"
        ],
        labels={
            "Mean Absolute SHAP": "Feature Importance",
            "Feature Label": "Customer Behaviour"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.3f}",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Importance: %{x:.4f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#191714",
        plot_bgcolor="#191714",
        font=dict(color="#E8DFD1"),
        height=480,
        margin=dict(l=20, r=80, t=25, b=25),
        coloraxis_showscale=False,
        showlegend=False
    )

    fig.update_xaxes(
        gridcolor="#39332D"
    )

    fig.update_yaxes(
        showgrid=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.markdown(
        f"""
        <div class='insight-panel'>
            <div class='insight-label'>KEY MODEL FINDING</div>
            <div style="
                font-family:'Playfair Display',serif;
                font-size:27px;
                font-weight:600;
                color:#E8DFD1;
                margin-top:9px;">
                {top_feature} is the strongest model driver.
            </div>
            <div class='insight-text'>
                Its mean absolute SHAP value is {top_value:.3f},
                making it the most influential feature by average
                contribution magnitude in this analysis.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        "<p class='eyebrow'>FEATURE COMPARISON</p>",
        unsafe_allow_html=True
    )

    st.subheader("Which Features Have the Greatest Influence?")

    comparison_data = shap_df.head(5).copy()

    fig = px.pie(
        comparison_data,
        names="Feature Label",
        values="Mean Absolute SHAP",
        hole=0.65,
        color_discrete_sequence=[
            "#B22222",
            "#8B7D72",
            "#D8CBB9",
            "#A65B50",
            "#66564D"
        ]
    )

    fig.update_traces(
        textposition="outside",
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Importance: %{value:.4f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
        pull=[
            0.08, 0, 0, 0, 0
        ]
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#191714",
        plot_bgcolor="#191714",
        font=dict(color="#E8DFD1"),
        height=420,
        margin=dict(l=30, r=30, t=30, b=30),
        showlegend=True,
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

    st.divider()

    st.markdown(
        "<p class='eyebrow'>CUSTOMER SCORE DISTRIBUTION</p>",
        unsafe_allow_html=True
    )

    st.subheader("Distribution of Predicted Churn Scores")

    if "churn_score" in df.columns:

        fig = px.histogram(
            df,
            x="churn_score",
            nbins=35,
            color_discrete_sequence=["#B22222"],
            labels={
                "churn_score": "Predicted Churn Score",
                "count": "Number of Customers"
            }
        )

        threshold = float(
            metadata["classification_threshold"]
        )

        fig.add_vline(
            x=threshold,
            line_dash="dash",
            line_color="#E8DFD1",
            annotation_text=f"Decision Threshold: {threshold:.2f}",
            annotation_position="top"
        )

        fig.update_traces(
            marker_line_color="#191714",
            marker_line_width=1,
            hovertemplate=(
                "Churn Score: %{x:.3f}<br>"
                "Customers: %{y:,}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#191714",
            plot_bgcolor="#191714",
            font=dict(color="#E8DFD1"),
            height=390,
            margin=dict(l=20, r=20, t=35, b=25),
            showlegend=False
        )

        fig.update_xaxes(
            title="Predicted Churn Score",
            range=[0, 1],
            gridcolor="#39332D"
        )

        fig.update_yaxes(
            title="Number of Customers",
            gridcolor="#39332D"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    else:
        st.info(
            "Churn scores are unavailable in the current model output."
        )

    st.caption(
        "SHAP importance measures contribution magnitude, not direction "
        "or causation. Churn scores are model outputs and are not "
        "calibrated probabilities."
    )

except Exception as error:

    st.error("Unable to load Model Explainability.")

    st.exception(error)
