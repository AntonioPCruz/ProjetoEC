"""Ponto de entrada da aplicação Streamlit DrHouseGPT."""

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from db_connection import test_nosql, test_sql, test_vector

load_dotenv()

# Recursos estáticos em src/assets/
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

st.set_page_config(page_title="DrHouseGPT", page_icon="💉", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "landing"

if "messages" not in st.session_state:
    st.session_state.messages = []


def landing_page():
    st.title("DrHouseGPT")
    st.subheader("Um chatbot inteligente para diagnosticar doenças e outras mazelas")
    image_path = ASSETS_DIR / "Dr.House_S4E3_15.png"
    if image_path.exists():
        image = Image.open(image_path)
        st.image(image, use_container_width=True)
    else:
        st.caption("(Imagem não encontrada)")

    st.markdown(
        """
        O uso deste chatbot não substitui a consulta de um médico de verdade.
        """
    )

    if st.button("💬 Conversar com o DrHouseGPT", use_container_width=True):
        st.session_state.page = "chat"
        st.rerun()

    with st.expander("⚙️ Estado do sistema"):
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


def chat_page():
    st.title("👨🏻‍⚕️ DrHouseGPT")

    st.caption("Escreve uma mensagem para iniciar a conversa")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escreve aqui..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # ---- Aqui entra a lógica do chatbot (mock por agora) ----
        response = f"Recebi a tua mensagem: **{prompt}**"

        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(response)

    st.markdown("---")

    if st.button("⬅ Voltar"):
        st.session_state.page = "landing"
        st.rerun()


if st.session_state.page == "landing":
    landing_page()
else:
    chat_page()
