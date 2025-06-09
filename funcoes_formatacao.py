import re
from db import supabase
import streamlit as st
from funcoes_crud import *

# Funções para formatação
def formatar_moeda(valor):
    try:
        valor_float = float(str(valor).replace(',', '.'))
        return f"R$ {valor_float:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except:
        return valor


def formatar_telefone(numero: str) -> str:
    """Formata um número de telefone brasileiro"""
    numero_limpo = re.sub(r'\D', '', numero)  # Remove tudo que não for dígito

    if len(numero_limpo) == 11:
        # Com DDD + celular (ex: 34991234567)
        return f"({numero_limpo[:2]}) {numero_limpo[2:7]}-{numero_limpo[7:]}"
    elif len(numero_limpo) == 10:
        # Com DDD + fixo (ex: 3421234567)
        return f"({numero_limpo[:2]}) {numero_limpo[2:6]}-{numero_limpo[6:]}"
    elif len(numero_limpo) == 9:
        # Celular sem DDD (ex: 991234567)
        return f"{numero_limpo[:5]}-{numero_limpo[5:]}"
    elif len(numero_limpo) == 8:
        # Fixo sem DDD (ex: 21234567)
        return f"{numero_limpo[:4]}-{numero_limpo[4:]}"
    else:
        return numero  # Retorna como veio se não bater com formatos esperados
    

def validar_dados_fornecedor(nome, cnpj, cep):
    padrao_cnpj = r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$"
    padrao_cep = r"\d{2}\.\d{3}-\d{3}"

    if not nome or not cnpj:
        return False, "Preencha todos os campos obrigatórios."
    elif not re.match(padrao_cnpj, cnpj):
        return False, "❌ CNPJ inválido. Use o formato 00.000.000/0000-00."
    elif cep and not re.fullmatch(padrao_cep, cep):
        return False, "❌ CEP inválido. Use o formato 00.000-000."
    return True, ""

def formatar_dados_fornecedor(nome, telefone, endereco):
    nome_formatado = ' '.join(nome.split()).upper()
    endereco_formatado = ' '.join(endereco.split()).upper()
    telefone_formatado = formatar_telefone(telefone)
    return nome_formatado, telefone_formatado, endereco_formatado

def cnpj_existe(cnpj):
    resultado = supabase.table("fornecedores").select("id").eq("cnpj", cnpj).execute()
    return bool(resultado.data)

def selecionar_categoria(categorias_selecionadas):      
    try:
        atas_result = buscar_registro("atas", "nome")

        if categorias_selecionadas:
            atas_filtradas = [ata for ata in atas_result if ata["categoria_ata"] in categorias_selecionadas]
        else:
            atas_filtradas = atas_result

        atas_dict = {a["nome"]: a["id"] for a in atas_filtradas}
        atas_opcoes = ["Selecione"] + list(atas_dict.keys())

    except Exception as e:
        st.error(f"Erro ao buscar atas: {e}")
        atas_opcoes = ["Selecione"]
        atas_dict = {}
    
    return [atas_opcoes, atas_dict]

def selecionar_categoria_para_empenho(categorias_selecionadas):
    try:       
        atas_result = buscar_registro("atas", "nome")

        if categorias_selecionadas:
            atas_filtradas = [ata for ata in atas_result if ata["categoria_ata"] in categorias_selecionadas]
        else:
            atas_filtradas = atas_result

        atas_dict = {a["nome"]: {"id": a["id"], "data_validade":a["data_validade"]} for a in atas_filtradas}
        atas_cadastradas = ["Selecione"] + list(atas_dict.keys())

    except Exception as e:
        st.error(f"Erro ao buscar atas: {e}")
        atas_cadastradas = ["Selecione"]
        atas_dict = {}
    
    return [atas_cadastradas, atas_dict]
