import streamlit as st
import pandas as pd
import sqlite3
import time
import plotly.express as px
from datetime import datetime

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Dashboard de Usinagem CNC",
    page_icon="⚙️",
    layout="wide"
)

# Função para conectar ao banco e extrair dados usando Pandas
def load_data():
    conn = sqlite3.connect('usinagem.db')
    query = "SELECT * FROM producao ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    # Converter timestamp para datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Título do Dashboard
st.title("⚙️ Dashboard de Usinagem CNC - Tempo Real")
st.markdown("Análise de performance e KPIs das 8 máquinas CNC.")

# Container para o loop de "Tempo Real"
placeholder = st.empty()

# Loop de atualização contínua
while True:
    # 1. Carregar dados atualizados
    df_raw = load_data()

    # Filtrar para exibir as métricas baseadas no último registro de cada máquina
    df_latest = df_raw.sort_values('timestamp').groupby('maquina').last().reset_index()

    # 2. Cálculos dos KPIs solicitados
    # OEE Simplificado = Disponibilidade * Performance * Qualidade
    # Aqui calculamos de forma agregada para o dashboard:
    disponibilidade = df_latest['tempo_ativo'] / df_latest['tempo_total']
    qualidade = df_latest['pecas_boas'] / df_latest['pecas_totais']
    performance = 1.0  # Assumindo 100% de velocidade padrão para fins de simulação
    df_latest['OEE'] = (disponibilidade * performance * qualidade) * 100

    # Taxa de Utilização
    df_latest['taxa_utilizacao'] = (df_latest['tempo_ativo'] / df_latest['tempo_total']) * 100

    # Médias Gerais da Fábrica
    avg_setup = df_latest['tempo_setup'].mean()
    avg_lead_time = df_latest['lead_time'].mean()
    avg_oee = df_latest['OEE'].mean()
    total_wip = df_latest['wip'].sum()
    avg_ciclo = df_latest['tempo_ciclo'].mean()
    avg_utilizacao = df_latest['taxa_utilizacao'].mean()

    # 3. Renderizar os componentes dentro do placeholder para atualizar a tela sem dar flash
    with placeholder.container():
        # Linha 1: Cartões de KPIs Gerais da Fábrica
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        col1.metric(label="⏱️ Média Setup", value=f"{avg_setup:.1f} min")
        col2.metric(label="📦 Média Lead Time", value=f"{avg_lead_time:.1f} min")
        col3.metric(label="📊 OEE Médio", value=f"{avg_oee:.1f}%")
        col4.metric(label="🏭 WIP Total", value=f"{total_wip} pçs")
        col5.metric(label="🔄 Tempo de Ciclo", value=f"{avg_ciclo:.2f} min")
        col6.metric(label="⚡ Utilização Geral", value=f"{avg_utilizacao:.1f}%")

        st.markdown("---")

        # Linha 2: Visão Individual por Máquina CNC
        st.subheader("📊 Performance por Máquina CNC (Último Status)")

        # Criar duas colunas para gráficos do Plotly
        g_col1, g_col2 = st.columns(2)

        with g_col1:
            # Gráfico de Barras: OEE vs Taxa de Utilização por Máquina
            df_melted = df_latest.melt(id_vars='maquina', value_vars=['OEE', 'taxa_utilizacao'],
                                       var_name='Métrica', value_name='Porcentagem')
            fig_bar = px.bar(df_melted, x='maquina', y='Porcentagem', color='Métrica', barmode='group',
                             title="OEE vs Taxa de Utilização (%)",
                             color_discrete_sequence=px.colors.qualitative.Pastel)

            # CORREÇÃO DEFINITIVA: Adicionado um timestamp à chave do gráfico
            chave_grafico_1 = f"grafico_oee_utilizacao_{int(time.time())}"
            st.plotly_chart(fig_bar, use_container_width=True, key=chave_grafico_1)

        with g_col2:
            # Gráfico de Barras: WIP por Máquina
            fig_wip = px.bar(df_latest, x='maquina', y='wip', title="Trabalho em Processo (WIP) por CNC",
                             labels={'wip': 'Peças em Processo'}, color='wip',
                             color_continuous_scale=px.colors.sequential.Viridis)

            # CORREÇÃO DEFINITIVA: Adicionado um timestamp à chave do gráfico
            chave_grafico_2 = f"grafico_wip_maquinas_{int(time.time())}"
            st.plotly_chart(fig_wip, use_container_width=True, key=chave_grafico_2)

        # Linha 3: Tabela de Dados Atualizados
        st.subheader("📋 Visão Geral dos Dados")
        st.dataframe(
            df_latest[['maquina', 'tempo_setup', 'lead_time', 'tempo_ciclo', 'wip', 'taxa_utilizacao', 'OEE']]
            .style.format({'tempo_setup': '{:.1f} min', 'lead_time': '{:.1f} min', 'tempo_ciclo': '{:.2f} min',
                           'taxa_utilizacao': '{:.1f}%', 'OEE': '{:.1f}%'})
        )

        # Exibe o horário da última atualização do dashboard
        st.caption(f"Última atualização do sistema: {datetime.now().strftime('%H:%M:%S')}")

    # Intervalo de atualização (Ex: 5 segundos)
    time.sleep(5)