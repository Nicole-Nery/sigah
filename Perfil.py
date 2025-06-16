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
nome_atual = usuario["nome_usuario"]
