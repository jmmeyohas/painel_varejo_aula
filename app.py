import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página para parecer um dashboard profissional
st.set_page_config(page_title="Retail Sales Dashboard", layout="wide", initial_sidebar_state="expanded")

# Estilo CSS customizado para os KPIs
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Carregando e limpando os dados conforme as etapas anteriores
    df = pd.read_csv('online_retail.csv', encoding='ISO-8859-1')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df.dropna(subset=['Description', 'CustomerID'], inplace=True)
    df = df[df['Quantity'] > 0]
    df['Total_sales'] = df['Quantity'] * df['UnitPrice']
    df['MonthYear'] = df['InvoiceDate'].dt.strftime('%b %Y')
    df['MonthSort'] = df['InvoiceDate'].dt.to_period('M')
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.title("Filtros de Vendas")
country_list = sorted(df['Country'].unique())
selected_country = st.sidebar.multiselect("Países", country_list, default=country_list[:5])

# Filtragem
df_filtered = df[df['Country'].isin(selected_country)]

# --- DASHBOARD PRINCIPAL ---
st.title("📊 Dashboard Retail - Análise de Performance")
st.write(f"Análise baseada em {len(selected_country)} países selecionados.")

# --- LINHA 1: KPIs ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Faturamento Total", f"${df_filtered['Total_sales'].sum():,.2f}")
with col2:
    st.metric("Total de Pedidos", f"{df_filtered['InvoiceNo'].nunique():,}")
with col3:
    st.metric("Clientes Únicos", f"{df_filtered['CustomerID'].nunique():,}")
with col4:
    avg_ticket = df_filtered['Total_sales'].sum() / df_filtered['InvoiceNo'].nunique() if df_filtered['InvoiceNo'].nunique() > 0 else 0
    st.metric("Ticket Médio", f"${avg_ticket:,.2f}")

# --- LINHA 2: GRÁFICOS ---
st.markdown("--- ")
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📈 Evolução Mensal do Faturamento")
    temporal = df_filtered.groupby(['MonthSort', 'MonthYear'])['Total_sales'].sum().reset_index()
    temporal = temporal.sort_values('MonthSort')
    fig_line = px.line(temporal, x='MonthYear', y='Total_sales', markers=True, 
                       labels={'Total_sales': 'Vendas ($)', 'MonthYear': 'Mês'},
                       color_discrete_sequence=['#636EFA'])
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("🏆 Top 10 Produtos")
    top_p = df_filtered.groupby('Description')['Total_sales'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_bar = px.bar(top_p, x='Total_sales', y='Description', orientation='h',
                     labels={'Total_sales': 'Total ($)', 'Description': 'Produto'},
                     color='Total_sales', color_continuous_scale='Blues')
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("--- ")
st.caption("Dashboard desenvolvido para análise exploratória de dados de varejo online.")
