import streamlit as st
from auth.funcoes_auth import *
from login_page import mostrar_tela_login_ou_cadastro

# Configurações visuais
st.set_page_config(
    page_title="SIGAH",
    page_icon="assets/icon.svg",
    layout="wide"
)

# Estilo CSS
with open("style/main.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Login obrigatório antes da navegação
if "usuario" not in st.session_state:
    mostrar_tela_login_ou_cadastro()
    st.stop()

pages = [
    st.Page("Relatorios.py", title="Relatórios", icon=":material/notifications_active:"),
    st.Page("Fornecedores.py", title="Fornecedores", icon=":material/group_add:"),
    st.Page("Atas.py", title="Atas", icon=":material/description:"),
    st.Page("Empenhos.py", title="Empenhos", icon=":material/request_quote:"),
    st.Page("Historico.py", title="Histórico de Empenhos", icon=":material/bar_chart:"),
    st.Page("Perfil.py", title="Perfil", icon=":material/account_circle:"),
    st.Page("Sair.py", title="Sair", icon=":material/logout:")
]

# Navegação entre páginas (só acessível após login)
page = st.navigation(pages)
page.run()