import streamlit as st
from db import supabase
from cabecalho import conexao_e_cabecalho
from funcoes_formatacao import *
from funcoes_crud import *
import pandas as pd

conexao_e_cabecalho()

tabs_atas = st.tabs(["Cadastrar", "Consultar", "Atualizar ou Excluir"])

with tabs_atas[0]:
    try:
        fornecedores_result = buscar_registro("fornecedores", "nome", ["id", "nome", "cnpj"])

        # Exibir no selectbox como "Nome (CNPJ)"
        fornecedores_dict = {
            f"{f['nome']} ({f['cnpj']})": f["id"]
            for f in fornecedores_result
        }

        fornecedores_cadastrados = ["Selecione"] + list(fornecedores_dict.keys())

    except Exception as e:
        st.error(f"Erro ao buscar fornecedores: {e}")
        fornecedores_cadastrados = ["Selecione"]
        fornecedores_dict = {}

    # Formulário para cadastrar nova Ata
    with st.form("nova_ata", border=True):
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            num_ata = st.text_input("Número da Ata (ex: 12/2024, 1234/2025)")
        with col2:
            categoria_ata = st.selectbox("Categoria", ["Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"], key="selecione_categoria_ata")
        with col3:
            ata_renovavel = st.radio("Ata renovável?", options=["Sim", "Não"], horizontal=True)
            renovavel_bool = ata_renovavel == "Sim"

        fornecedor_selecionado = st.selectbox("Fornecedor", fornecedores_cadastrados, key="selecione_fornecedor_nome", help="Digite o nome ou CNPJ para localizar o fornecedor.")
        if fornecedor_selecionado != "Selecione":
            fornecedor_id = fornecedores_dict[fornecedor_selecionado]
        else:
            fornecedor_id = None

        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            data_ata = st.date_input("Data da Ata", format="DD/MM/YYYY")
        with col2:
            validade_ata = st.date_input("Validade da Ata", min_value=data_ata, format="DD/MM/YYYY")
        with col3:
            link_ata = st.text_input("Número do Protocolo SEI")

        submit_ata = st.form_submit_button("Cadastrar Ata")

        if submit_ata:
            if re.fullmatch(r'\d{1,5}/\d{4}', num_ata):
                try:
                    dados_atas = {
                        "nome": num_ata,
                        "data_inicio": data_ata.isoformat(),
                        "data_validade": validade_ata.isoformat(),
                        "fornecedor_id": fornecedor_id, 
                        "link_ata": link_ata,
                        "categoria_ata": categoria_ata,
                        "ata_renovavel": renovavel_bool
                    }
                    result = cadastrar_registro("atas", dados_atas)
                    if result:
                        st.success(f"Ata '{num_ata}' cadastrada com sucesso!")
                        st.session_state["num_ata"] = ""
                        st.session_state["data_ata"] = ""
                        st.session_state["validade_ata"] = ""
                        st.session_state["fornecedor_id"] = ""
                        st.session_state["link_ata"] = ""
                except Exception as e:
                    st.error(f"Erro ao cadastrar ata: {e}")
            else:
                st.error("Formato inválido. Use o padrão: 1234/2024")  


    # Adicionar Item na Ata --------------------------------------------
    st.html("<div class='subtitle'>Adicionar Item a uma Ata</div>")
    categorias_selecionadas = st.multiselect("Escolha a(s) categoria(s)", ["Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"], placeholder="Selecione", key="selecionar_categoria_item")
    atas_opcoes, atas_dict = selecionar_categoria(categorias_selecionadas)
    atas_result = buscar_registro("atas", "nome",["id", "nome"])

    ata_nome = st.selectbox("Selecione a Ata", atas_opcoes, key="selecione_ata_nome")

    if ata_nome != "Selecione":
        ata_id = atas_dict[ata_nome]
        with st.expander("Adicionar Item", expanded=True, icon=":material/construction:"):
            with st.form("novo_item", border=True):
                col1, col2 = st.columns([1,1])
                with col1:
                    especificacao = st.text_input("Especificação")
                    especificacao_formatado = ' '.join(especificacao.split()).upper()
                with col2:
                    marca_modelo = st.text_input("Marca/Modelo")
                
                col1, col2, col3 = st.columns([1,1,1])
                with col1:
                    quantidade = st.number_input("Quantidade", min_value=1, step=1)
                with col2:
                    saldo_disponivel = st.number_input("Saldo disponível", min_value=0, step=1)
                with col3:
                    valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.4f")
                valor_total = valor_unitario * quantidade

                submit_item = st.form_submit_button("Adicionar Item")
                dados_equip = {
                    "especificacao":especificacao_formatado, 
                    "ata_id": ata_id,
                    "marca_modelo":marca_modelo, 
                    "quantidade":quantidade, 
                    "saldo_disponivel":saldo_disponivel, 
                    "valor_unitario":valor_unitario,
                    "valor_total": valor_total
                }
                if submit_item:
                    try:
                        result = cadastrar_registro("equipamentos", dados_equip)
                        if result:
                            st.success(f"Item {especificacao} cadastrado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao cadastrar item: {e}")
            
with tabs_atas[1]:
    categorias_selecionadas = st.multiselect("Escolha a(s) categoria(s)", ["Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"], placeholder="Selecione", key="selecionar_categoria_consultar_ata")
    atas_opcoes, atas_dict = selecionar_categoria(categorias_selecionadas)
    atas_result = buscar_registro("atas", "nome")
    ata_visualizar = st.selectbox("Selecione uma Ata para consultar", atas_opcoes, key="selecione_ata_visualizar")

    if ata_visualizar != "Selecione":
        ata_id = atas_dict[ata_visualizar]

        # Buscar os dados da Ata selecionada
        ata_info = next((a for a in atas_result if a["id"] == ata_id), None)

        if ata_info:
            nome = ata_info["nome"]
            data_ata = ata_info["data_inicio"]
            validade_ata = ata_info["data_validade"]
            categoria_ata = ata_info["categoria_ata"]
            link_ata = ata_info.get("link_ata", "")

            fornecedores = buscar_registro("fornecedores", "nome", ["id", "nome"])
            fornecedores_dict = {f["id"]:f["nome"] for f in fornecedores}
            fornecedor_nome = fornecedores_dict[ata_info["fornecedor_id"]]

            ata_renovavel_bool = ata_info["ata_renovavel"]

            st.markdown(f"**Número:** {nome}")
            st.markdown(f"**Data da Ata:** {pd.to_datetime(data_ata).strftime('%d/%m/%Y')}")
            st.markdown(f"**Validade:** {pd.to_datetime(validade_ata).strftime('%d/%m/%Y')}")
            st.markdown(f"**Fornecedor:** {fornecedor_nome}")
            st.markdown(f"**Categoria:** {categoria_ata}")
            st.markdown(f"**N° Protocolo SEI:** {link_ata}")
            st.markdown(f"**Ata renovável?**: {'Sim' if ata_renovavel_bool else 'Não'}")

            # Buscar os equipamentos dessa ata
            try:
                response = supabase.table("equipamentos").select(
                    "especificacao, marca_modelo, quantidade, saldo_disponivel, valor_unitario, valor_total"
                ).eq("ata_id", ata_id).execute()
                equipamentos = response.data
                
                st.markdown("---")
                st.html("<div class='subtitle'>Itens dessa Ata</div>")

                if equipamentos:
                    df_equip = pd.DataFrame(equipamentos)
                    df_equip["valor_unitario"] = df_equip["valor_unitario"].apply(formatar_moeda)
                    df_equip["valor_total"] = df_equip["valor_total"].apply(formatar_moeda)

                    df_equip = df_equip.rename(columns={
                        "especificacao": "Especificação",
                        "marca_modelo": "Marca/Modelo",
                        "quantidade": "Quantidade",
                        "saldo_disponivel": "Saldo Disponível",
                        "valor_unitario": "Valor Unitário",
                        "valor_total": "Valor Total"
                    })
                    st.dataframe(df_equip, height=300)
                else:
                    st.info("Nenhum item cadastrado para esta Ata.")
            except Exception as e:
                st.error(f"Erro ao buscar itens: {e}")

with tabs_atas[2]:
    categorias_selecionadas = st.multiselect("Escolha a(s) categoria(s)", ["Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"], placeholder="Selecione", key="selecionar_categoria_atualizar_ata")
    atas_opcoes, atas_dict = selecionar_categoria(categorias_selecionadas)
    atas_result = buscar_registro("atas", "nome")
    ata_selecionada = st.selectbox("Selecione uma Ata para atualizar dados", atas_opcoes)
    
    if ata_selecionada != "Selecione":
        ata_id = atas_dict[ata_selecionada]

        # Buscar os dados da Ata selecionada
        ata_info = next((a for a in atas_result if a["id"] == ata_id), None)

        try:
            fornecedores_result = buscar_registro("fornecedores", "nome", ["id", "nome", "cnpj"])

            # Exibir no selectbox como "Nome (CNPJ)"
            fornecedores_dict = {
                f"{f['nome']} ({f['cnpj']})": f["id"]
                for f in fornecedores_result
            }

            fornecedores_cadastrados = ["Selecione"] + list(fornecedores_dict.keys())

        except Exception as e:
            st.error(f"Erro ao buscar fornecedores: {e}")
            fornecedores_cadastrados = ["Selecione"]
            fornecedores_dict = {}
        
        categorias = ["Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"]
        categoria_atual = ata_info["categoria_ata"]


        with st.form("form_editar_ata", border=True):

            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                novo_nome = st.text_input("Nome da Ata", value=ata_info["nome"])
            with col2:
                nova_categoria_ata = st.selectbox("Categoria", categorias, key="selecione_nova_categoria_ata", index=categorias.index(categoria_atual) if categoria_atual else 0)
            with col3:
                nova_info_renovacao = st.radio("Ata renovável?", options=["Sim", "Não"], horizontal=True)
                nova_info_renovacao_bool = nova_info_renovacao == 'Sim'

            fornecedor_atual_id = ata_info["fornecedor_id"]
            fornecedor_atual_nome = next(
                (f"{f['nome']} ({f['cnpj']})" for f in fornecedores_result if f["id"] == fornecedor_atual_id),
                "Selecione"
            )

            novo_fornecedor_nome = st.selectbox(
                "Fornecedor",
                fornecedores_cadastrados,
                key="selecione_novo_fornecedor_nome",
                help="Digite o nome ou CNPJ para localizar o fornecedor.",
                index=fornecedores_cadastrados.index(fornecedor_atual_nome) if fornecedor_atual_nome in fornecedores_cadastrados else 0
            )

            if novo_fornecedor_nome != "Selecione":
                novo_fornecedor_id = fornecedores_dict[novo_fornecedor_nome]
            else:
                novo_fornecedor_id = None

            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                nova_data = st.date_input("Data da Ata", format="DD/MM/YYYY", value=pd.to_datetime(ata_info["data_inicio"]).date())
            with col2:
                nova_validade_ata = st.date_input("Validade da Ata", min_value=nova_data, format="DD/MM/YYYY", value=pd.to_datetime(ata_info["data_validade"]).date())
            with col3:
                novo_link_ata = st.text_input("Número do Protocolo SEI")

            dados_atualizados_atas = {
                "nome": novo_nome,
                "data_inicio": nova_data.isoformat(),
                "data_validade": nova_validade_ata.isoformat(),
                "fornecedor_id": novo_fornecedor_id,
                "categoria_ata": nova_categoria_ata,
                "link_ata": novo_link_ata,
                "ata_renovavel": nova_info_renovacao_bool
            }

            col1, col2 = st.columns([1,2], border=True)
            with col1:
                atualizar = st.form_submit_button("Atualizar Ata")
            with col2:
                confirmar_exclusao_ata = st.checkbox("Desejo excluir essa ata.")
                excluir_ata = st.form_submit_button("❌ Excluir Ata")
            
            if atualizar:
                try:
                    result = atualizar_registro("atas", ata_id,dados_atualizados_atas)
                    if result:
                        st.success("Ata atualizada com sucesso!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao atualizar a Ata: {e}")
        
            if excluir_ata and not confirmar_exclusao_ata:
                st.warning("Confirme a exclusão do ata.")
            elif excluir_ata and confirmar_exclusao_ata:
                try:
                    result = deletar_registro("atas", ata_id)
                    if result:
                        st.success("Ata excluída com sucesso.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir ata.") 


        # Buscar equipamentos vinculados à Ata
        st.html("<div class='subtitle'>Itens dessa Ata</div>")
        st.write("Clique no item que deseja atualizar informações")
    
        response_equip = supabase.table("equipamentos").select("*").eq("ata_id", ata_id).execute()
        equipamentos = response_equip.data

        if not equipamentos:
            st.info("Nenhum item cadastrado para essa Ata.")
        else:
            for equipamento in equipamentos:
                with st.expander(f"Item: {equipamento['especificacao']}", icon=":material/construction:"):
                    with st.form(f"form_equip_{equipamento['id']}", border=True):

                        col1, col2 = st.columns([1,1])
                        with col1:
                            nova_especificacao = st.text_input("Especificação", value=equipamento["especificacao"])
                        with col2:
                            nova_marca_modelo = st.text_input("Marca/Modelo", value=equipamento["marca_modelo"])
                        
                        col1, col2, col3 = st.columns([1,1,1])
                        with col1:
                            nova_qtd = st.number_input("Quantidade", value=equipamento["quantidade"], step=1)
                        with col2:
                            novo_saldo = st.number_input("Saldo Disponível", value=equipamento["saldo_disponivel"], step=1)
                        with col3:
                            novo_valor_unit = st.number_input("Valor Unitário (R$)", value=float(equipamento["valor_unitario"]), step=0.01, format="%.4f")       

                        # Valor total calculado automaticamente
                        novo_valor_total = nova_qtd * novo_valor_unit
                        st.text(f"Valor Total: R$ {novo_valor_total:.2f}")
                        nova_espeficicacao_formatada = ' '.join(nova_especificacao.split()).upper()
                        nova_marca_modelo_formatada = ' '.join(nova_marca_modelo.split()).upper()
                        
                        dados_atualizados_eq = {
                            "especificacao": nova_espeficicacao_formatada,
                            "marca_modelo": nova_marca_modelo_formatada,
                            "quantidade": nova_qtd,
                            "saldo_disponivel": novo_saldo,
                            "valor_unitario": novo_valor_unit,
                            "valor_total": novo_valor_total
                        }

                        col1, col2 = st.columns([1,2], border=True)
                        with col1:
                            atualizar = st.form_submit_button("Atualizar Item")
                        with col2:
                            confirmar_exclusao_item = st.checkbox("Desejo excluir esse item.")
                            excluir_item = st.form_submit_button("❌ Excluir Item")

                        if atualizar:
                            try:
                                response = atualizar_registro("equipamentos", equipamento['id'], dados_atualizados_eq)
                                if response:
                                    st.success(f"Item '{nova_espeficicacao_formatada}' atualizado com sucesso!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar item: {e}")    
                            
                        if excluir_item and not confirmar_exclusao_item:
                            st.warning("Confirme a exclusão do item.")
                        elif excluir_item and confirmar_exclusao_item:
                            try:
                                response = deletar_registro("equipamentos", equipamento['id'])
                                if response:
                                    st.success("Item excluído com sucesso.")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir item.")      

                                              


    
    

