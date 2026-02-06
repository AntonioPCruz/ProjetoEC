import streamlit as st
from dotenv import load_dotenv
from utils.db_connection import test_sql, test_nosql, test_vector

load_dotenv()


# --- Interface Streamlit ---
st.header("Status da Infraestrutura")
col1, col2, col3 = st.columns(3)

with col1:
    if test_sql():
        st.success("SQL (PostgreSQL) - Conectado")
    else:
        st.error("SQL - Falha na Ligação")

with col2:
    if test_nosql():
        st.success("NoSQL (MongoDB) - Conectado")
    else:
        st.error("NoSQL - Falha na Ligação")

with col3:
    if test_vector():
        st.success("Vetorial (Chroma) - Conectado")
    else:
        st.warning("Vetorial - Offline ou em Setup")
