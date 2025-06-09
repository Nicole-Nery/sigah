import streamlit as st
from db import supabase
from cabecalho import conexao_e_cabecalho
from funcoes_formatacao import *
from funcoes_crud import *
import pandas as pd
from datetime import date

conexao_e_cabecalho()

tabs_empenhos = st.tabs(["Empenhar", "Consultar", "Atualizar ou Excluir"])

with tabs_empenhos[0]:
    categorias_selecionadas = st.multiselect("Escolha a(s) categoria(s)", ["Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"], placeholder="Selecione", key="selecionar_categoria_empenho_atualizar")

    atas_cadastradas, atas_dict = selecionar_categoria_para_empenho(categorias_selecionadas)
    ata_nome = st.selectbox("Selecione a Ata", atas_cadastradas, key="selecione_ata_nome_empenho")

    if ata_nome != "Selecione":
        ata_id = atas_dict[ata_nome]["id"]
        ata_validade = atas_dict[ata_nome]["data_validade"]

        try:
            # Buscar equipamentos com saldo > 0
            response = supabase.table("equipamentos").select("id, especificacao, saldo_disponivel").eq("ata_id", ata_id).gt("saldo_disponivel", 0).execute()
            equipamentos_result = response.data

            if equipamentos_result:
                equipamentos_dict = {e["especificacao"]: (e["id"], e["saldo_disponivel"]) for e in equipamentos_result}
                equip_opcoes = ["Selecione"] + list(equipamentos_dict.keys())

                equipamento_nome = st.selectbox("Selecione o Equipamento", equip_opcoes, key="selecione_equipamento_nome")

                if equipamento_nome != "Selecione":
                    equipamento_id, saldo_disp = equipamentos_dict[equipamento_nome]

                    with st.form("form_registrar_empenho", border=True):
                        quantidade = st.number_input("Quantidade empenhada", min_value=1, max_value=saldo_disp, step=1)
                        data_empenho = st.date_input("Data do Empenho", format="DD/MM/YYYY")
                        observacao = st.text_input("Observação (opcional)")

                        registrar_empenho = st.form_submit_button("Empenhar")    
                        if registrar_empenho:
                            ata_validade_date = date.fromisoformat(ata_validade)
                            if data_empenho > ata_validade_date:
                                ata_validade_formatada = date.fromisoformat(ata_validade).strftime("%d/%m/%Y")
                                st.error(f"A data do empenho é posterior à validade da Ata (vencida em {ata_validade_formatada}). Cadastro não permitido.")
                            else:
                                try:
                                    dados_empenho= {
                                        "equipamento_id": equipamento_id,
                                        "quantidade_empenhada": quantidade,
                                        "data_empenho": data_empenho.isoformat(),
                                        "observacao": observacao
                                    }
                                    
                                    cadastrar_registro("empenhos", dados_empenho)

                                    # Atualizar saldo do equipamento
                                    supabase.table("equipamentos").update({
                                        "saldo_disponivel": saldo_disp - quantidade
                                    }).eq("id", equipamento_id).execute()

                                    st.success("Empenho realizado com sucesso!")
                                except Exception as e:
                                    st.error(f"Erro ao cempenhar: {e}")
            else:
                st.warning("Nenhum item com saldo disponível para esta Ata.")
        except Exception as e:
            st.error(f"Erro ao buscar equipamentos: {e}")

with tabs_empenhos[1]:
    categorias_selecionadas = st.multiselect("Escolha a(s) categoria(s)", ["Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"], placeholder="Selecione", key="selecionar_categoria_item")

    atas_cadastradas, atas_dict = selecionar_categoria_para_empenho(categorias_selecionadas)
    ata_nome = st.selectbox("Selecione a Ata para consultar empenhos", atas_cadastradas, key="selecione_ata_nome_empenho_consulta")

    if ata_nome != "Selecione":
        ata_id = atas_dict[ata_nome]["id"]
        
        try:
            response = supabase.rpc("empenhos_por_ata", {"ata_id_param": ata_id}).execute()
            empenhos = response.data

            if empenhos: 
                empenhos_df = pd.DataFrame(empenhos).drop(columns=['id'])
                empenhos_df['data_empenho'] = pd.to_datetime(empenhos_df['data_empenho']).dt.strftime('%d/%m/%Y')

                empenhos_df = empenhos_df.rename(columns={
                    'data_empenho': 'Data do Empenho',
                    'especificacao': 'Especificação',
                    'quantidade_empenhada': 'Quantidade Empenhada',
                    'observacao':'Observação'
                })

                st.dataframe(empenhos_df, height=400)

            else:
                st.info("Nenhum empenho cadastrado para esta Ata.")
        except Exception as e:
            st.error(f"Erro ao buscar empenhos: {e}")

with tabs_empenhos[2]:
    categorias_selecionadas = st.multiselect("Escolha a(s) categoria(s)", ["Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"], placeholder="Selecione", key="selecionar_categoria_empenho")

    atas_cadastradas, atas_dict = selecionar_categoria_para_empenho(categorias_selecionadas)
    ata_nome = st.selectbox("Selecione a Ata para atualizar empenhos", atas_cadastradas, key="selecione_ata_nome_empenho_atualizar")

    if ata_nome != "Selecione":
        ata_id = atas_dict[ata_nome]["id"]
        ata_validade = atas_dict[ata_nome]["data_validade"]

        try:
            response = supabase.rpc("empenhos_por_ata", {"ata_id_param": ata_id}).execute()
            empenhos = response.data

            if empenhos:
                for emp in empenhos:
                    with st.expander(f"Empenho de {emp['quantidade_empenhada']}x {emp['especificacao']} em {pd.to_datetime(emp['data_empenho']).strftime('%d/%m/%Y')}", icon=":material/request_quote:"):
                        with st.form(f"form_emp_{emp['id']}", border=False):
                            nova_quantidade = st.number_input("Quantidade", min_value=1, value=emp["quantidade_empenhada"], key=f"qtd_{emp['id']}")
                            nova_data = st.date_input("Data do Empenho", format="DD/MM/YYYY",value=pd.to_datetime(emp["data_empenho"]).date(), key=f"data_{emp['id']}")
                            nova_obs = st.text_input("Observação", value=emp["observacao"] or "", key=f"obs_{emp['id']}")

                            col1, col2 = st.columns([1,1], border=True)
                            with col1:
                                atualizar = st.form_submit_button("Atualizar Empenho")
                            with col2:
                                confirmar_exclusao_empenho = st.checkbox("Desejo excluir esse empenho.")
                                excluir_empenho = st.form_submit_button("❌ Excluir Empenho")

                        if atualizar:
                            ata_validade_date = date.fromisoformat(ata_validade)
                            if nova_data > ata_validade_date:
                                    ata_validade_formatada = date.fromisoformat(ata_validade).strftime("%d/%m/%Y")
                                    st.error(f"A data do empenho é posterior à validade da Ata (vencida em {ata_validade_formatada}). Cadastro não permitido.")
                            else:
                                    try:
                                        supabase.table("empenhos").update({
                                            "quantidade_empenhada": nova_quantidade,
                                            "data_empenho": nova_data.isoformat(),
                                            "observacao": nova_obs
                                        }).eq("id", emp["id"]).execute()
                                        st.success("Empenho atualizado com sucesso.")
                                    except Exception as e:
                                        st.error(f"Erro ao atualizar empenho: {e}")

                        if excluir_empenho and not confirmar_exclusao_empenho:
                            st.warning("Confirme a exclusão do empenho.")
                        elif excluir_empenho and confirmar_exclusao_empenho:
                            try:
                                response = deletar_registro("empenhos", emp['id'])
                                if response:
                                    st.rerun()
                                    st.success("Empenho excluído com sucesso.")
                            except Exception as e:
                                st.error(f"Erro ao excluir empenho.")

            else:
                st.info("Nenhum empenho cadastrado para esta Ata.")
        except Exception as e:
            st.error(f"Erro ao buscar empenhos: {e}")