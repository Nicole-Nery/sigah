import streamlit as st
from auth.funcoes_auth import autenticar_usuario, cadastrar_novo_usuario
from db import supabase

def tela_login():
    st.markdown("""
        <style>
            .block-container {
                padding-top: 5vh;
                max-width: 500px;
                margin: auto;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="login-title">Login</h1>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False, border=False):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

        if entrar:
            if not email or not senha:
                st.warning("Preencha todos os campos.")
            else:
                usuario_autenticado = autenticar_usuario(email, senha)
                if usuario_autenticado:
                    st.session_state.usuario = usuario_autenticado
                    st.rerun()
                else:
                    st.error("E-mail ou senha inválidos.")

    if st.button("Não tem conta? Cadastre-se aqui."):
        st.session_state["modo"] = "cadastro"
        st.rerun()

def tela_cadastro():
    st.markdown("""
        <style>
            .block-container {
                padding-top: 5vh;
                max-width: 900px;
                margin: auto;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="login-title">Cadastro de usuário</h1>', unsafe_allow_html=True)


    with st.form("cadastro_form", clear_on_submit=False):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        confirmar_senha = st.text_input("Confirmar Senha", type="password")

        cadastrar = st.form_submit_button("Cadastrar")

        if cadastrar:
            if not nome or not email or not senha or not confirmar_senha:
                st.warning("Preencha todos os campos.")
            elif senha != confirmar_senha:
                st.error("As senhas não coincidem.")
            elif len(senha) < 6:
                st.error("A senha deve conter pelo menos 6 dígitos.")
            else:
                sucesso, mensagem = cadastrar_novo_usuario(supabase, nome, email, senha)
                if sucesso:
                    st.success(mensagem)
                    st.session_state["modo"] = "login"
                    st.rerun()
                else:
                    st.error(mensagem)

    if st.button("← Voltar para o login"):
        st.session_state["modo"] = "login"
        st.rerun()

def login_screen():
    st.header("Este app é privado.")
    st.subheader("Entre com a sua conta Microsoft.")
    st.button("Entrar com Microsoft", on_click=st.login)

    st.markdown("---")
    st.write("Ou entre com seu e-mail:")

    if "modo" not in st.session_state:
        st.session_state["modo"] = "login"

    if st.session_state["modo"] == "login":
        tela_login()
    elif st.session_state["modo"] == "cadastro":
        tela_cadastro()

def main():
    if hasattr(st, "user") and st.user.is_logged_in:
        st.header(f"Bem-vindo, {st.user.name}!")
        if st.button("Logout"):
            st.logout()
            st.rerun()
    else:
        login_screen()

if __name__ == "__main__":
    main()
