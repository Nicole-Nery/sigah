import streamlit as st
from db import supabase
from cabecalho import conexao_e_cabecalho
from funcoes_formatacao import *
from funcoes_crud import *
import pandas as pd

conexao_e_cabecalho()

tabs_fornecedores = st.tabs(["Cadastrar", "Consultar", "Atualizar ou Excluir"])

with tabs_fornecedores[0]:
    with st.form("form_cadastro_fornecedores", clear_on_submit=False, border=True):
        st.html("<div class='subtitle'>Informações do Fornecedor</div>")

        nome_fornecedor = st.text_input("Nome do Fornecedor")

        col1, col2 = st.columns([1,2])
        with col1:
            cnpj = st.text_input("CNPJ (formato: 00.000.000/0000-00)")
        with col2:
            email = st.text_input("E-mail")
        
        endereco = st.text_input("Endereço")
        col1, col2 = st.columns([2,1])
        with col1:
            telefone = st.text_input("Telefone")
        with col2:
            cep = st.text_input("CEP (formato = 00.000-000)", max_chars=10)
        
        nome_formatado, telefone_formatado, endereco_formatado = formatar_dados_fornecedor(nome_fornecedor, telefone, endereco)
        dados_fornecedor = {
            "nome": nome_formatado,
            "cnpj": cnpj,
            "email": email,
            "endereco": endereco_formatado,
            "cep": cep,
            "telefone": telefone_formatado}
        
        submit = st.form_submit_button("Cadastrar Fornecedor")

        if submit:
            valido, msg = validar_dados_fornecedor(nome_fornecedor, cnpj, cep)
            if not valido:
                st.error(msg)
            
            if cnpj_existe(cnpj):
                st.warning("⚠️ Já existe um fornecedor cadastrado com esse CNPJ.")

            try:
                resp = cadastrar_registro("fornecedores", dados_fornecedor)
                if resp:
                    st.success(f"Fornecedor '{nome_formatado}' cadastrado com sucesso!")
                    

            except Exception as e:
                st.error(f"Erro ao cadastrar fornecedor: {e}")

with tabs_fornecedores[1]:
    try:
        fornecedores_result = buscar_registro("fornecedores", "nome")

        if fornecedores_result:
            df_fornecedores = pd.DataFrame(fornecedores_result)
            df_fornecedores = df_fornecedores.drop(columns=["id"]).rename(columns={
                "nome": "Nome",
                "cnpj": "CNPJ",
                "email": "E-mail",
                "endereco": "Endereço",
                "cep": "CEP",
                "telefone": "Telefone"
            })
            st.dataframe(df_fornecedores, height=500)
        else:
            st.info("Nenhum fornecedor cadastrado.")
    except Exception as e:
        st.error(f"Erro ao buscar fornecedor: {e}")

with tabs_fornecedores[2]:
    try:
        fornecedores_data = buscar_registro("fornecedores", "id")
        fornecedores_dict = {f["nome"]: f["id"] for f in fornecedores_data}
        fornecedores_nomes = ["Selecione"] + list(fornecedores_dict.keys())

        fornecedor_selecionado = st.selectbox("Escolha um fornecedor", fornecedores_nomes)
        
        if fornecedor_selecionado != "Selecione":
            fornecedor_id = fornecedores_dict[fornecedor_selecionado]
            fornecedor_info = next((f for f in fornecedores_data if f["id"] == fornecedor_id), None)

            if fornecedor_info:
                with st.form("form_editar_fornecedor", border=True):
                    novo_nome = st.text_input("Nome do Fornecedor", value=fornecedor_info["nome"])

                    col1, col2 = st.columns([1,2])
                    with col1:
                        novo_cnpj = st.text_input("CNPJ (formato: 00.000.000/0000-00)", value=fornecedor_info["cnpj"])
                    with col2:
                        novo_email = st.text_input("E-mail", value=fornecedor_info["email"])
                    
                    novo_endereco = st.text_input("Endereço", value=fornecedor_info["endereco"])
                    col1, col2 = st.columns([2,1])
                    with col1:
                        novo_telefone = st.text_input("Telefone", value=fornecedor_info["telefone"])
                    with col2:
                        novo_cep = st.text_input("CEP (formato = 00.000-000)", max_chars=10, value=fornecedor_info["cep"])

                    novo_nome_formatado, novo_telefone_formatado, novo_endereco_formatado = formatar_dados_fornecedor(novo_nome, novo_telefone, novo_endereco)
                    dados_fornecedor_atualizados = {
                        "nome": novo_nome_formatado,
                        "cnpj": novo_cnpj,
                        "email": novo_email,
                        "endereco": novo_endereco_formatado,
                        "cep": novo_cep,
                        "telefone": novo_telefone_formatado}

                    col1, col2 = st.columns([1,2], border=True)
                    with col1:
                        atualizar = st.form_submit_button("Atualizar Fornecedor")
                    with col2:
                        confirmar_exclusao_fornecedor = st.checkbox("Desejo excluir esse fornecedor.")
                        excluir_fornecedor = st.form_submit_button("❌ Excluir Fornecedor")
            

                    if atualizar:
                        valido, msg = validar_dados_fornecedor(novo_nome, novo_cnpj, novo_cep)
                        if not valido:
                            st.error(msg)
                        
                        try:
                            response = atualizar_registro("fornecedores", fornecedor_id, dados_fornecedor_atualizados)
                            if response:
                                st.rerun()
                                st.success(f"Fornecedor {novo_nome.upper()} atualizado com sucesso!")
                                
                        except Exception as e:
                            st.error(f"Erro ao atualizar fornecedor: {e}")
        
                    if excluir_fornecedor and not confirmar_exclusao_fornecedor:
                        st.warning("Confirme a exclusão do fornecedor.")
                    elif excluir_fornecedor and confirmar_exclusao_fornecedor:
                        try:
                            response = deletar_registro("fornecedores", fornecedor_id)
                            if response:
                                st.rerun()
                                st.success("Fornecedor excluído com sucesso.")
                        except Exception as e:
                            st.error(f"Erro ao excluir fornecedor.")
                
    except Exception as e:
        st.error(f"Erro ao carregar fornecedores: {e}")
