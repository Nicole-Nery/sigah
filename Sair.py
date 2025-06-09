import streamlit as st

# Apaga apenas os dados do usuário logado
for chave in ["usuario", "token", "autenticado"]:
    st.session_state.pop(chave, None)

# Mensagem amigável de logout
st.success("Você saiu com sucesso.")
st.info("Clique em qualquer ícone da navegação à esquerda para retornar à tela de login.")

