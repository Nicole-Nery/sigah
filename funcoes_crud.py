from db import supabase
import streamlit as st

def cadastrar_registro (nome_tabela: str, dados: dict):
    try:
        response = supabase.table(nome_tabela).insert(dados).execute()
        return response
    except Exception as e:
        st.error(f"Erro no cadastro: {e}")

def buscar_registro (nome_tabela: str, ordenar_por: str, colunas=None):
    try:
        colunas_str = ", ".join(colunas) if colunas else "*"
        return supabase.table(nome_tabela).select(colunas_str).order(ordenar_por).execute().data
    except Exception as e:
        st.error(f"Erro na visualização: {e}")
        return None

def atualizar_registro(nome_tabela: str, id_registro: int, novos_dados: dict):
    try:
        response = supabase.table(nome_tabela).update(novos_dados).eq("id", id_registro).execute()
        return response
    except Exception as e:
        st.error(f"Erro na atualização: {e}")
        return None

def deletar_registro(nome_tabela: str, id_registro: int):
    try:
        response = supabase.table(nome_tabela).delete().eq("id", id_registro).execute()
        return response
    except Exception as e:
        st.error(f"Erro ao deletar: {e}")
        return None
    
def update_config(chave, valor):
        resp = supabase.table("configuracoes").upsert({
            "chave": chave,
            "valor": int(valor)
        }).execute()