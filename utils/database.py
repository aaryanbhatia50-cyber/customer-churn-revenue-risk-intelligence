
import streamlit as st
import pandas as pd

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


@st.cache_resource
def get_engine():
    settings = st.secrets["postgres"]

    connection_url = URL.create(
        "postgresql+psycopg2",
        username=settings["user"],
        password=settings["password"],
        host=settings["host"],
        port=int(settings["port"]),
        database=settings["database"]
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True
    )


def run_query(query, params=None):
    engine = get_engine()

    with engine.connect() as connection:
        return pd.read_sql(
            text(query),
            connection,
            params=params
        )
