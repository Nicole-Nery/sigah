import streamlit as st
import bcrypt
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

with st.form('editar_info_perfil'):
    st.html("<div class='subtitle'>Editar Informações</div>")
    novo_nome = st.text_input("Nome", value=nome_atual)
    novo_email = st.text_input("Email", value=email, disabled=True)

    with st.expander("Alterar senha", icon=":material/lock:"):
        nova_senha = st.text_input("Nova senha", type="password")
        confirmar_senha = st.text_input("Confirmar nova senha", type="password")

    if st.form_submit_button("Salvar alterações"):
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
