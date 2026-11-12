
import streamlit as st

st.set_page_config(
    page_title="Customer Churn & Revenue Risk Intelligence",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

pages = [
    st.Page(
        "pages/1_Executive_Overview.py",
        title="Executive Overview",
        default=True
    ),
    st.Page(
        "pages/2_Customer_Risk.py",
        title="Customer Risk"
    ),
    st.Page(
        "pages/3_Model_Explainability.py",
        title="Model Explainability"
    ),
    st.Page(
        "pages/4_Risk_Intelligence.py",
        title="Risk Intelligence"
    ),
    st.Page(
        "pages/5_Transaction_Analytics.py",
        title="Transaction Analytics"
    )
]

navigation = st.navigation(
    pages,
    position="top"
)

navigation.run()
