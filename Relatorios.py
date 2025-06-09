import streamlit as st
from db import supabase
from cabecalho import conexao_e_cabecalho
from funcoes_formatacao import *
from funcoes_crud import *
import pandas as pd
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

conexao_e_cabecalho()

relatorio_tabs = st.tabs(["Relatório de Consumo e Status", "Renovação de Atas"])

with relatorio_tabs[0]:
    try:
        # Buscar atas
        atas_response = buscar_registro("atas", "nome", ["id", "nome", "data_validade", "categoria_ata"])
        atas_data = {ata["id"]: ata for ata in atas_response}

        # Buscar equipamentos
        equipamentos_data = buscar_registro("equipamentos", "especificacao", ["especificacao", "quantidade", "saldo_disponivel", "ata_id", "valor_unitario"])

        if equipamentos_data:
            relatorio_consumo = []
            for eq in equipamentos_data:
                ata = atas_data.get(eq["ata_id"])

                if not ata:
                    continue

                saldo_utilizado = eq["quantidade"] - eq["saldo_disponivel"]
                valor_total = eq["quantidade"] * eq["valor_unitario"]
                valor_utilizado = saldo_utilizado * eq["valor_unitario"]
                percentual_utilizado = (saldo_utilizado / eq["quantidade"]) * 100 if eq["quantidade"] else 0
                percentual_disponivel = 100 - percentual_utilizado

                relatorio_consumo.append({
                    "Ata": ata["nome"],
                    "Ata ID": ata["id"],
                    "Categoria": ata["categoria_ata"],
                    "Equipamento": eq["especificacao"],
                    "Qtd Total": eq["quantidade"],
                    "Saldo Utilizado": saldo_utilizado,
                    "Saldo Disponível": eq["saldo_disponivel"],
                    "% Utilizado": f"{percentual_utilizado:.1f}%",
                    "% Disponível": f"{percentual_disponivel:.1f}%",
                    "Valor Total (R$)": valor_total,
                    "Valor Utilizado (R$)": valor_utilizado,
                    "Data de Validade": ata["data_validade"]
                })

            # Criar DataFrame
            relatorio_df = pd.DataFrame(relatorio_consumo)

            # Manter validade como datetime antes de formatar
            relatorio_df["Data de Validade"] = pd.to_datetime(relatorio_df["Data de Validade"])

            # Remover atas vencidas há mais de 30 dias
            hoje = pd.Timestamp.today()
            relatorio_df = relatorio_df[(relatorio_df["Data de Validade"] >= hoje - pd.Timedelta(days=30))]

            # Garantir que % utilizado é float antes de formatar
            relatorio_df["% Utilizado"] = (
                relatorio_df["% Utilizado"]
                .astype(str)
                .str.replace('%', '', regex=False)
                .str.replace(',', '.', regex=False)
                .astype(float)
            )

            # Formatações
            relatorio_df["Data de Validade"] = relatorio_df["Data de Validade"].dt.strftime('%d/%m/%Y')
            relatorio_df["Valor Total (R$)"] = relatorio_df["Valor Total (R$)"].apply(formatar_moeda)
            relatorio_df["Valor Utilizado (R$)"] = relatorio_df["Valor Utilizado (R$)"].apply(formatar_moeda)
            relatorio_df["% Utilizado"] = relatorio_df["% Utilizado"].map(lambda x: f"{x:.1f}%")

            categorias_selecionadas = st.multiselect("Escolha a(s) categoria(s)", ["Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"], placeholder="Selecione", key="selecionar_categoria_relatorio")
            
            if categorias_selecionadas:
                relatorio_df_filtrado = relatorio_df[relatorio_df["Categoria"].isin(categorias_selecionadas)]
                ata_ids_filtradas = set(relatorio_df_filtrado["Ata ID"].unique())

                relatorio_df_filtrado = relatorio_df_filtrado.drop(columns=["Ata ID"])
                st.dataframe(relatorio_df_filtrado, height=200)

                hoje = datetime.today().date()
                data_limite = hoje + timedelta(days=30)

                # Criar dicionário: ata_id -> saldo total disponível
                saldo_por_ata = {}
                for eq in equipamentos_data:
                    ata_id = eq["ata_id"]
                    saldo_por_ata[ata_id] = saldo_por_ata.get(ata_id, 0) + eq["saldo_disponivel"]

                atas_vencidas = [
                    ata for ata in atas_data.values()
                    if ata["id"] in ata_ids_filtradas and ata["data_validade"] and pd.to_datetime(ata["data_validade"]).date() < hoje
                ]

                atas_vencendo = [
                    ata for ata in atas_data.values()
                    if ata["id"] in ata_ids_filtradas and ata["data_validade"] and hoje < pd.to_datetime(ata["data_validade"]).date() <= data_limite
                ]

                with st.container(border=True):
                    st.markdown("""
                        <div style='background-color:#f7f090; padding:17px; border-radius:7px; position:relative; margin-bottom:1em'>
                            ⚠️ Atas vencendo nos próximos 30 dias:
                        </div>
                        """, unsafe_allow_html=True)
                    if atas_vencendo:
                        for ata in sorted(atas_vencendo, key=lambda x: x["data_validade"]):
                            validade = pd.to_datetime(ata["data_validade"]).strftime('%d/%m/%Y')
                            saldo = saldo_por_ata.get(ata["id"], 0)
                            st.write(f"**Ata:** {ata['nome']} — **Validade:** {validade}")
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• **Saldo restante:** {saldo}")
                    else:
                        st.write("Não há atas vencendo nos próximos 30 dias.")

            
                with st.container(border=True):
                    st.markdown("""
                            <div style='background-color:#f8d7da; padding:17px; border-radius:7px; position:relative; margin-bottom:1em'>
                                ❌    Atas vencidas:
                                <span style='float:right; cursor:help;' title='Atas com renovação vencida há mais de 30 dias não são mostradas.'>ℹ️</span>
                            </div>
                            """, unsafe_allow_html=True)
                    if atas_vencidas:
                        for ata in sorted(atas_vencidas, key=lambda x: x["data_validade"]):
                            validade_dt = pd.to_datetime(ata["data_validade"])
                            dias_vencida = (pd.Timestamp.today() - validade_dt).days

                            if 0 < dias_vencida <= 30:
                                validade = validade_dt.strftime('%d/%m/%Y')
                                saldo = saldo_por_ata.get(ata["id"], 0)
                                st.write(f"**Ata:** {ata['nome']} — **Vencida em:** {validade}")
                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• **Saldo restante:** {saldo}")
                    else:
                        st.write("Não há atas vencidas nos últimos 30 dias.")

        else:
            st.info("Nenhum consumo cadastrado ainda.")


    except Exception as e:
        st.error(f"Erro ao gerar relatório: {e}")

with relatorio_tabs[1]:
    resposta = supabase.table('configuracoes').select("valor").eq("chave", "prazo_renovacao_ata").single().execute()

    # Extrair e converter o valor para inteiro (meses)
    valor_str = resposta.data["valor"]
    try:
        prazo_renovacao_ata = int(valor_str)
    except ValueError:
        prazo_renovacao_ata = 12  # valor padrão de segurança

    # Mostrar o prazo atual
        prazo_placeholder = st.empty()
        prazo_placeholder.markdown(f"**Prazo padrão de renovação:** {prazo_renovacao_ata} meses")

        # Formulário para alterar o prazo
        with st.expander("Alterar prazo de renovação"):
            with st.form("form_alterar_prazo", border=False):
                novo_prazo = st.number_input(
                    "Novo prazo de renovação (meses)",
                    min_value=1,
                    max_value=96,
                    value=prazo_renovacao_ata
                )
                submitted = st.form_submit_button("Salvar novo prazo")
                if submitted:
                    update_config('prazo_renovacao_ata', str(novo_prazo))  # salvando como string no banco
                    st.success(f"Prazo atualizado para {novo_prazo} meses!")
                    st.rerun()

        st.markdown("---")

        try:
            # Buscar atas
            atas_response = buscar_registro("atas", "nome", ["id", "nome", "data_inicio", "categoria_ata"])
            atas_data = {ata["id"]: ata for ata in atas_response}

            if atas_data:
                # Inicialização
                relatorio_renovacao = []
                alertas_90 = []
                alertas_30 = []
                alertas_vencidas = []

                # Preenchendo os dados brutos
                for ata in atas_data.values():
                    if not ata:
                        continue

                    data_inicio = date.fromisoformat(ata["data_inicio"])
                    data_renovacao = data_inicio + relativedelta(months=prazo_renovacao_ata)
                    dias_para_renovacao = (data_renovacao - date.today()).days

                    relatorio_renovacao.append({
                        "Ata": ata["nome"],
                        "Categoria": ata["categoria_ata"],
                        "Data Início": data_inicio.strftime('%d/%m/%Y'),
                        "Data Renovação": data_renovacao.strftime('%d/%m/%Y'),
                        "Dias para renovação": dias_para_renovacao
                    })

                    alerta = {
                        "nome": ata["nome"],
                        "dias": dias_para_renovacao,
                        "categoria": ata["categoria_ata"]
                    }

                    if dias_para_renovacao < 0 and dias_para_renovacao >= -30:
                        alertas_vencidas.append(alerta)
                    elif dias_para_renovacao > 0 and dias_para_renovacao <= 30:
                        alertas_30.append(alerta)
                    elif dias_para_renovacao > 30 and dias_para_renovacao <= 90:
                        alertas_90.append(alerta)

                # Criar DataFrame
                relatorio_df = pd.DataFrame(relatorio_renovacao)
                relatorio_df = relatorio_df[relatorio_df["Dias para renovação"] >= -30]
                

                # Seleção de categorias
                categorias = ["Todos", "Equipamentos médicos", "Infraestrutura hospitalar", "Suprimentos"]
                categorias_selecionadas = st.multiselect("Escolha a(s) categoria(s)", categorias, placeholder="Selecione", key="selecionar_categoria_renovacao")

                if categorias_selecionadas:
                    relatorio_filtrado = relatorio_df[relatorio_df["Categoria"].isin(categorias_selecionadas)]
                    st.dataframe(relatorio_filtrado, height=150)


                    def exibir_alertas(alertas):
                        alertas_filtrados = [a for a in alertas if a["categoria"] in categorias_selecionadas]
                        
                        if alertas_filtrados:
                            for a in alertas_filtrados:
                                if a["dias"] < 0:
                                    st.write(f"**Ata:** {a['nome']} — Vencida há {-a['dias']} dia(s)")
                                else:
                                    st.write(f"**Ata:** {a['nome']} — {a['dias']} dias restantes")
                        else:
                            st.write("Não há atas nesta condição.")


                    with st.container(border=True):
                        st.markdown("""
                            <div style='background-color:#aaee99; padding:17px; border-radius:7px; position:relative; margin-bottom:1em'>
                                🔔 Renovações nos próximos 90 dias:
                            </div>
                            """, unsafe_allow_html=True)
                        exibir_alertas(alertas_90)
                    
                    with st.container(border=True):
                        st.markdown("""
                            <div style='background-color:#f7f090; padding:17px; border-radius:7px; position:relative; margin-bottom:1em'>
                                ⚠️ Renovações nos próximos 30 dias:
                            </div>
                            """, unsafe_allow_html=True)
                        exibir_alertas(alertas_30)

                    with st.container(border=True):
                        st.markdown("""
                            <div style='background-color:#f8d7da; padding:17px; border-radius:7px; position:relative; margin-bottom:1em'>
                                ❌ Atas com renovação vencida:
                                <span style='float:right; cursor:help;' title='Atas com renovação vencida há mais de 30 dias não são mostradas.'>ℹ️</span>
                            </div>
                            """, unsafe_allow_html=True)
                        exibir_alertas(alertas_vencidas)
                        
                    
            else:
                st.info("Nenhuma ata cadastrada ainda.")

        except Exception as e:
            st.error(f"Erro ao gerar relatório: {e}")