import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- CSS para cor dos ícones da barra lateral (azul) ---
st.markdown(
    """
    <style>
    /* Barra lateral largura */
    [data-testid="stSidebar"] {
        min-width: 200px;
        max-width: 600px;
    }

    /* Ícones azuis viram brancos */
    [data-testid="stSidebar"] svg {
        fill: white !important;
    }

    /* Tags selecionadas do multiselect — de vermelho para azul */
    .st-emotion-cache-1r6slb0, .st-emotion-cache-16idsys {
        background-color: #1E90FF !important; /* Azul DodgerBlue */
        color: white !important; /* Texto branco */
        border: none !important;
    }

    /* Hover das tags */
    .st-emotion-cache-1r6slb0:hover, .st-emotion-cache-16idsys:hover {
        background-color: #187bcd !important; /* Azul mais escuro */
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)


# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados)) 
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Gráficos ---
if not df_filtrado.empty:
    # Top 10 cargos por salário médio
    top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
    grafico_cargos = px.bar(
        top_cargos,
        x='usd',
        y='cargo',
        orientation='h',
        title="Top 10 cargos por salário médio",
        labels={'usd': 'Média salarial anual (USD)', 'cargo': ''},
        color='usd',
        color_continuous_scale='teal'
    )
    grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(grafico_cargos, use_container_width=True)

    # Distribuição de salários anuais
    grafico_hist = px.histogram(
        df_filtrado,
        x='usd',
        nbins=30,
        title="Distribuição de salários anuais",
        labels={'usd': 'Faixa salarial (USD)', 'count': ''},
        color_discrete_sequence=['#20B2AA']
    )
    grafico_hist.update_layout(title_x=0.1)
    st.plotly_chart(grafico_hist, use_container_width=True)

    # Proporção dos tipos de trabalho
    remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
    remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
    grafico_remoto = px.pie(
        remoto_contagem,
        names='tipo_trabalho',
        values='quantidade',
        title='Proporção dos tipos de trabalho',
        hole=0.5,
        color_discrete_sequence=['#20B2AA', '#76EEC6', '#008B8B']
    )
    grafico_remoto.update_traces(textinfo='percent+label')
    grafico_remoto.update_layout(title_x=0.1)
    st.plotly_chart(grafico_remoto, use_container_width=True)

    # Salário médio de Cientista de Dados por país
    df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
    media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
    grafico_paises = px.choropleth(
        media_ds_pais,
        locations='residencia_iso3',
        color='usd',
        color_continuous_scale='teal',
        title='Salário médio de Cientista de Dados por país',
        labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'}
    )
    grafico_paises.update_layout(title_x=0.1)
    st.plotly_chart(grafico_paises, use_container_width=True)

    # Evolução do salário médio ao longo dos anos
    graf_evolucao = px.line(
        df_filtrado.groupby('ano')['usd'].mean().reset_index(),
        x='ano',
        y='usd',
        title="Evolução do salário médio ao longo dos anos",
        markers=True,
        color_discrete_sequence=['#20B2AA']
    )
    graf_evolucao.update_layout(title_x=0.1)
    st.plotly_chart(graf_evolucao, use_container_width=True)

    # Salário médio por senioridade
    graf_senioridade = px.bar(
        df_filtrado.groupby('senioridade')['usd'].mean().reset_index(),
        x='senioridade',
        y='usd',
        title="Salário médio por senioridade",
        color='usd',
        color_continuous_scale='teal'
    )
    graf_senioridade.update_layout(title_x=0.1)
    st.plotly_chart(graf_senioridade, use_container_width=True)

    # Comparativo de salários por tipo de contrato
    graf_contrato = px.bar(
        df_filtrado.groupby('contrato')['usd'].mean().reset_index(),
        x='contrato',
        y='usd',
        title="Salário médio por tipo de contrato",
        color='usd',
        color_continuous_scale='teal'
    )
    graf_contrato.update_layout(title_x=0.1)
    st.plotly_chart(graf_contrato, use_container_width=True)

    # Top países com maior salário médio
    top_paises = df_filtrado.groupby('residencia_iso3')['usd'].mean().nlargest(10).reset_index()
    graf_top_paises = px.bar(
        top_paises,
        x='residencia_iso3',
        y='usd',
        title="Top 10 países com maior salário médio",
        color='usd',
        color_continuous_scale='teal'
    )
    graf_top_paises.update_layout(title_x=0.1)
    st.plotly_chart(graf_top_paises, use_container_width=True)

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)


