import streamlit as st
import bcrypt
from PIL import Image
import io
import uuid
from db import supabase
from cabecalho import conexao_e_cabecalho
from funcoes_crud import buscar_registro, atualizar_registro, deletar_registro

conexao_e_cabecalho()

usuario_auth = st.session_state.get("usuario")

if not usuario_auth:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

email = usuario_auth.get("email")


# Buscar dados do usuário
usuarios = buscar_registro(nome_tabela="usuarios", ordenar_por="id", colunas=["id", "nome", "email", "senha"])

usuario = next((u for u in usuarios if u["email"] == email), None)

if not usuario:
    st.error("Usuário não encontrado no banco.")
    st.stop()

usuario_id = usuario["id"]
nome_atual = usuario["nome"]


# --- Layout ---

st.subheader("Editar Informações")
novo_nome = st.text_input("Nome", value=nome_atual)
st.text_input("Email", value=email, disabled=True)

with st.expander("🔐 Alterar senha"):
    nova_senha = st.text_input("Nova senha", type="password")
    confirmar_senha = st.text_input("Confirmar nova senha", type="password")

if st.button("💾 Salvar alterações"):
    atualizacoes = {"nome_usuario": novo_nome}
    if nova_senha:
        if nova_senha != confirmar_senha:
            st.error("As senhas não coincidem.")
            st.stop()
        nova_senha_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        atualizacoes["senha"] = nova_senha_hash

    resultado = atualizar_registro("usuarios", usuario_id, atualizacoes)
    if resultado:
        st.success("Perfil atualizado com sucesso!")

st.markdown("---")
st.subheader("⚠️ Excluir Conta")

with st.expander("🗑️ Deseja excluir sua conta permanentemente?"):
    confirmacao = st.text_input("Digite CONFIRMAR para excluir sua conta:")
    if st.button("Excluir conta", type="primary"):
        if confirmacao == "CONFIRMAR":
            deletar = deletar_registro("usuarios", usuario_id)
            if deletar:
                st.success("Conta excluída com sucesso.")
                st.session_state.clear()
                st.experimental_rerun()
        else:
            st.error("Confirmação incorreta. Digite exatamente CONFIRMAR para prosseguir.")
