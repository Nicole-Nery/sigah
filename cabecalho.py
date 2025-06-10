from pathlib import Path
import streamlit as st

def conexao_e_cabecalho():
    usuario = st.session_state["usuario"]

    # Botão de sair
    with st.sidebar:
        st.logo(image="assets/logo-sigah.png", size='large')
        st.image("assets/logos.png", use_container_width=True)
        st.write("Sistema Integrado de Gestão de Atas Hospitalares")
        st.write("Versão 2.0")
    # Aplica o CSS
    with open("style/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Conteúdo do cabeçalho sobre a faixa
    with st.container():
        col1, col2 = st.columns([3,1])
        with col1:
            st.html(f"<h3 class='header-title'>Bem-vindo(a), {usuario['nome']}</h3>")
            st.write("Hospital de Clínicas de Uberlândia (HC-UFU)")
        with col2:
            st.write("SISTEMA INTEGRADO DE GESTÃO DE ATAS HOSPITALARES")


    
