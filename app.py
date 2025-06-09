import streamlit as st
from auth.funcoes_auth import *
from login_page import *

# Configurações visuais
st.set_page_config(
    page_title="SIGAH",
    page_icon="assets/icon.svg",
    layout="wide"
)

# Estilo CSS
with open("style/main.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Verifica se o usuário está logado via autenticação interna ou Microsoft
usuario_logado = (
    "usuario" in st.session_state  # login do app
    or (hasattr(st, "user") and st.user.is_logged_in)  # login Microsoft
)

if not usuario_logado:
    login_screen()  # esta função mostrará os botões de login
    st.stop()

# Navegação entre páginas
pages = [
    st.Page("Relatorios.py", title="Relatórios", icon=":material/notifications_active:"),
    st.Page("Fornecedores.py", title="Fornecedores", icon=":material/group_add:"),
    st.Page("Atas.py", title="Atas", icon=":material/description:"),
    st.Page("Empenhos.py", title="Empenhos", icon=":material/request_quote:"),
    st.Page("Historico.py", title="Histórico de Empenhos", icon=":material/bar_chart:"),
    st.Page("Perfil.py", title="Perfil", icon=":material/account_circle:"),
    st.Page("Sair.py", title="Sair", icon=":material/logout:")
]

page = st.navigation(pages)
page.run()
