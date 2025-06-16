import streamlit as st
from db import supabase
from cabecalho import conexao_e_cabecalho
from funcoes_formatacao import *
from funcoes_crud import *
import pandas as pd
import plotly.express as px
import textwrap

conexao_e_cabecalho()

historico_tabs = st.tabs(["Histórico de Empenhos"])

with historico_tabs[0]:
    try:
        # Filtrar por categoria
        categorias = ["Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"]
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            categoria_filtro = st.multiselect("Filtrar por Categoria", categorias, key="selecione_categoria_filtro", placeholder="Selecione")

        # Buscar atas
        atas_data = buscar_registro("atas", "nome", ["id", "nome", "categoria_ata"])

        # Filtrar atas pelas categorias selecionadas
        if not categoria_filtro:
            atas_filtradas = atas_data
        else:
            atas_filtradas = [ata for ata in atas_data if ata["categoria_ata"] in categoria_filtro]   

        # Construir opções de atas
        atas_dict = {ata["nome"]: ata["id"] for ata in atas_filtradas}
        atas_opcoes = ["Todas"] + list(atas_dict.keys())

        with col2:
            # Filtrar por ata
            ata_filtro = st.multiselect("Filtrar por Ata", atas_opcoes, key="selecione_ata_filtro", placeholder="Selecione", )
        equipamentos_data = buscar_registro("equipamentos", "especificacao", ["id", "especificacao", "ata_id"])

        if not ata_filtro or "Todas" in ata_filtro:
            # Quando a categoria está filtrada mas a ata não, buscar todos os equipamentos das atas dessa categoria
            if categoria_filtro:
                ata_ids_filtradas = [ata["id"] for ata in atas_filtradas]
                equipamentos_filtrados = [eq for eq in equipamentos_data if eq["ata_id"] in ata_ids_filtradas]
            else:
                equipamentos_filtrados = equipamentos_data
        else:
            ata_id_selecionada = [atas_dict[nome_ata] for nome_ata in ata_filtro if nome_ata != "Todas"]
            equipamentos_filtrados = [equip for equip in equipamentos_data if equip["ata_id"] in ata_id_selecionada] 

        equipamentos_dict = {eq["id"]: eq for eq in equipamentos_filtrados}
        equipamentos_opcoes = ["Todos"] + sorted(list(set(eq["especificacao"] for eq in equipamentos_filtrados)))
        with col3:
            equipamento_filtro = st.multiselect("Filtrar por Item", equipamentos_opcoes, key="filtro_equipamento", placeholder="Selecione")

        # Considera todos se estiver vazio ou se "Todos" estiver selecionado
        if not equipamento_filtro or "Todos" in equipamento_filtro:
            equipamentos_selecionados = equipamentos_filtrados
        else:
            equipamentos_selecionados = [eq for eq in equipamentos_filtrados if eq["especificacao"] in equipamento_filtro]

        # Filtro de data
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data inicial", value=pd.to_datetime("2024-01-01"), format= 'DD/MM/YYYY', key="data_inicio_filtro")
        with col2:
            data_fim = st.date_input("Data final", value=pd.to_datetime("today"), format= 'DD/MM/YYYY', key="data_fim_filtro")

        # Buscar empenhos
        st.html("<div class='subtitle'>Empenhos realizados</div>")
        empenhos_response = supabase.table("empenhos").select("*").order("data_empenho", desc=True).execute()
        empenhos_data = empenhos_response.data

        empenhos_filtrados = []
        for emp in empenhos_data:
            equipamento = equipamentos_dict.get(emp["equipamento_id"])
            if not equipamento:
                continue

            ata_id = equipamento["ata_id"]
            ata = next((a for a in atas_data if a["id"] == ata_id), None)
            if not ata:
                continue

            especificacao = equipamento["especificacao"]
            data_empenho = pd.to_datetime(emp["data_empenho"])
            categoria = ata["categoria_ata"]
            ata_nome = ata["nome"]

            # Filtros por categoria (multiselect)
            if categoria_filtro and "Todas" not in categoria_filtro and categoria not in categoria_filtro:
                continue

            # Filtros por ata (multiselect)
            if ata_filtro and "Todas" not in ata_filtro and ata_nome not in ata_filtro:
                continue

            # Filtros por equipamento (multiselect)
            if equipamento_filtro and "Todos" not in equipamento_filtro and especificacao not in equipamento_filtro:
                continue

            # Filtro de data
            if not (data_inicio <= data_empenho.date() <= data_fim):
                continue

            empenhos_filtrados.append({
                "Ata": ata_nome,
                "Categoria": categoria,
                "Item": especificacao,
                "Quantidade": emp["quantidade_empenhada"],
                "Data do Empenho": data_empenho.strftime('%d/%m/%Y'),
                "Observação": emp["observacao"]
            })

        if empenhos_filtrados:
            df_empenhos = pd.DataFrame(empenhos_filtrados)
            st.dataframe(df_empenhos, height=200)

            especificacoes_empenhadas = set(df_empenhos["Item"])
            especificacoes_filtradas = set(eq["especificacao"] for eq in equipamentos_selecionados)

            especificacoes_nao_empenhadas = especificacoes_filtradas - especificacoes_empenhadas

            if especificacoes_nao_empenhadas:
                st.markdown("**Itens desta(s) Ata(s) ainda não empenhados:**")
                for especificacao in sorted(especificacoes_nao_empenhadas):
                    st.write(f"- {especificacao}")

            col1, col2 = st.columns([1,2], border=True)
            cores_personalizadas = ["#97bf29", "#1f144e", "#4e79a7", "#9c9e9f", "#d3d4d5"]
            with col1:
                total_por_categoria = df_empenhos.groupby("Categoria")["Quantidade"].sum().reset_index()
                fig_categoria = px.pie(total_por_categoria, names="Categoria", values="Quantidade", title="Empenhos por categoria", color_discrete_sequence=cores_personalizadas)
                fig_categoria.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',  # fundo externo
                    plot_bgcolor='rgba(0,0,0,0)',   # fundo do gráfico
                )
                st.plotly_chart(fig_categoria, use_container_width=True)

            with col2:
                # Garante que é datetime pra gerar o AnoMes
                df_empenhos["Data do Empenho"] = pd.to_datetime(df_empenhos["Data do Empenho"], dayfirst=True)

                # Cria coluna formatada tipo 'Abr/2025'
                df_empenhos["AnoMes"] = df_empenhos["Data do Empenho"].dt.strftime('%b/%Y')

                # Agrupa por essa nova coluna
                quantidade_mensal = df_empenhos.groupby("AnoMes")["Quantidade"].sum().reset_index()

                # Cria gráfico com eixo categórico
                fig_mensal = px.line(
                    quantidade_mensal,
                    x="AnoMes",
                    y="Quantidade",
                    markers=True,
                    title="Quantidade Empenhada por Mês",
                    color_discrete_sequence=cores_personalizadas
                )

                fig_mensal.update_xaxes(type="category", title_text="Ano/Mês")
                #fig_mensal.update_yaxes(dtick=50)
                fig_mensal.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',  # fundo externo
                    plot_bgcolor='rgba(0,0,0,0)',   # fundo do gráfico
                )

                st.plotly_chart(fig_mensal, use_container_width=True)

        else:
            st.info("Nenhum empenho encontrado com os filtros selecionados.")
    except Exception as e:
        st.error(f"Erro ao buscar empenhos: {e}")
