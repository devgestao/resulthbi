import streamlit as st
import json
from pathlib import Path
import requests
from datetime import datetime, timedelta
import pandas as pd
from queries import VENDAS_QUERY, VENDAS_GRUPO_QUERY, PRODUTOS_MAIS_VENDIDOS_QUERY, DESPESAS_CAIXA_QUERY
import locale
from babel.numbers import format_currency
import plotly.graph_objects as go
import platform
from streamlit import container
import logging
from users_manager import authenticate
from companies_manager import get_company_by_cnpj, admin_settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_calls.log'),
        logging.StreamHandler()
    ]
)

def init_session_state():
    try:
        if platform.system() == "Windows":
            locale.setlocale(locale.LC_ALL, "Portuguese_Brazil.1252")
        else:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
    except locale.Error:
        # fallback
        locale.setlocale(locale.LC_ALL, "")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'login_form_submitted' not in st.session_state:
        st.session_state.login_form_submitted = False
    if 'last_query_params' not in st.session_state:
        st.session_state.last_query_params = None
    if 'show_admin' not in st.session_state:
        st.session_state.show_admin = False
    if 'company_data' not in st.session_state:
        st.session_state.company_data = None

def login_page():
    st.title("Login")
    
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            user = authenticate(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_data = user
                if user['empresas']:
                    st.session_state.company_data = user['empresas'][0]
                st.rerun()
            else:
                st.error("Invalid username or password")

def fetch_api_data(url, cnpj, data_inicial, data_final):
    start_time = datetime.now()
    logging.info(f"Iniciando consulta - CNPJ: {cnpj} | Período: {data_inicial} a {data_final}")
    
    # Buscar dados de vendas
    logging.info("Iniciando consulta da API de Vendas...")
    query_vendas = VENDAS_QUERY.replace("[DATA_INICIAL]", f"{data_inicial}").replace("[DATA_FINAL]", f"{data_final}").replace("[CNPJ_FILIAL]", f"{cnpj}")
    data_vendas = {
        'token': 'token',
        'query': query_vendas
    }
    vendas_start = datetime.now()
    response_vendas = requests.post(url, data=data_vendas)
    logging.info(f"API Vendas - Tempo de resposta: {(datetime.now() - vendas_start).total_seconds():.2f}s")
    
    # Buscar dados de grupos
    logging.info("Iniciando consulta da API de Grupos...")
    query_grupos = VENDAS_GRUPO_QUERY.replace("[DATA_INICIAL]", f"{data_inicial}").replace("[DATA_FINAL]", f"{data_final}").replace("[CNPJ_FILIAL]", f"{cnpj}")
    data_grupos = {
        'token': 'token',
        'query': query_grupos
    }
    grupos_start = datetime.now()
    response_grupos = requests.post(url, data=data_grupos)
    logging.info(f"API Grupos - Tempo de resposta: {(datetime.now() - grupos_start).total_seconds():.2f}s")
    
    # Buscar dados de produtos mais vendidos
    logging.info("Iniciando consulta da API de Produtos...")
    query_produtos = PRODUTOS_MAIS_VENDIDOS_QUERY.replace("[DATA_INICIAL]", f"{data_inicial}").replace("[DATA_FINAL]", f"{data_final}").replace("[CNPJ_FILIAL]", f"{cnpj}")
    data_produtos = {
        'token': 'token',
        'query': query_produtos
    }
    produtos_start = datetime.now()
    response_produtos = requests.post(url, data=data_produtos)
    logging.info(f"API Produtos - Tempo de resposta: {(datetime.now() - produtos_start).total_seconds():.2f}s")
    
    # Buscar dados de despesas
    logging.info("Iniciando consulta da API de Despesas...")
    query_despesas = DESPESAS_CAIXA_QUERY.replace("[DATA_INICIAL]", f"{data_inicial}").replace("[DATA_FINAL]", f"{data_final}").replace("[CNPJ_FILIAL]", f"{cnpj}")
    data_despesas = {
        'token': 'token',
        'query': query_despesas
    }
    despesas_start = datetime.now()
    response_despesas = requests.post(url, data=data_despesas)
    logging.info(f"API Despesas - Tempo de resposta: {(datetime.now() - despesas_start).total_seconds():.2f}s")
    
    logging.info(f"Tempo total de consulta: {(datetime.now() - start_time).total_seconds():.2f}s")
    
    return {
        'vendas': response_vendas.json(),
        'grupos': response_grupos.json(),
        'produtos': response_produtos.json(),
        'despesas': response_despesas.json()
    }

def create_metric_card(title, value, prefix="R$", delta=None, color="#00BFFF"):
    card_style = f"""
    <style>
        .metric-card {{
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            border-left: 5px solid {color};
            min-height: 100px;
        }}
        .metric-title {{
            color: #555;
            font-size: 0.9em;
            font-weight: 500;
        }}
        .metric-value {{
            color: #0f1f3d;
            font-size: 1.4em;
            font-weight: bold;
            margin-top: 10px;
        }}
        .block-container {{
            padding: 2rem 1rem 1rem !important;
            max-width: 100vw;
        }}
        .main {{
            padding: 1.5rem 1rem !important;
        }}
        div[data-testid="stVerticalBlock"] {{
            gap: 1rem !important;
            padding-top: 1rem !important;
        }}
    </style>
    """
    
    # Formatação do valor
    if isinstance(value, (int, float)):
        if prefix == "R$":
            formatted_value = format_currency(value, 'BRL', locale='pt_BR')
        else:
            formatted_value = f"{value:,.0f}"
    else:
        formatted_value = value

    # HTML do card
    card_html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{formatted_value}</div>
    </div>
    """
    
    st.markdown(card_style + card_html, unsafe_allow_html=True)

def create_payment_chart(data):
    payment_methods = {
        'Dinheiro': data['VALOR_VENDADINHEIRO'],
        'TEF': data['VALOR_VENDATEF'],
        'POS': data['VALOR_VENDAPOS'],
        'Cheque': data['VALOR_VENDACHEQUE'],
        'A Receber': data['VALOR_VENDARECEBER'],
        'Crédito': data['VALOR_CREDITOAPROVEITADO']
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(payment_methods.keys()),
            y=list(payment_methods.values()),
            text=[format_currency(val, 'BRL', locale='pt_BR') if val > 0 else 'R$ 0,00' for val in payment_methods.values()],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
    dragmode=False,
    xaxis=dict(fixedrange=True),
        title='Vendas por Forma de Pagamento',
        showlegend=False,
        plot_bgcolor='white',
        height=500,
        yaxis=dict(fixedrange=True,showgrid=True, gridwidth=1, gridcolor='LightGray'),
        margin=dict(l=10, r=10, t=40, b=20),
        paper_bgcolor='white',
    )
    
    return fig

def create_groups_chart(data):
    # Filtrar apenas grupos (excluir o Total) e ordenar por valor
    groups_data = [d for d in data if d['TEXTO_GRUPO'] != 'Total']
    groups_data.sort(key=lambda x: x['VALOR_GRUPO'], reverse=True)
    
    fig = go.Figure()
    
    # Adicionar barra de valores (eixo Y primário)
    fig.add_trace(go.Bar(
        name='Valor (R$)',
        x=[d['TEXTO_GRUPO'] for d in groups_data],
        y=[d['VALOR_GRUPO'] for d in groups_data],
        text=[format_currency(d['VALOR_GRUPO'], 'BRL', locale='pt_BR') for d in groups_data],
        textposition='auto',
        marker_color='#2E8B57',
        offsetgroup=0
    ))
    
    # Adicionar barra de quantidade (eixo Y secundário)
    fig.add_trace(go.Bar(
        name='Quantidade (Kg)',
        x=[d['TEXTO_GRUPO'] for d in groups_data],
        y=[d['QUANTIDADE_GRUPO'] for d in groups_data],
        text=[f"{d['QUANTIDADE_GRUPO']:,.2f} Kg" for d in groups_data],
        textposition='auto',
        marker_color='#4169E1',
        yaxis='y2',
        offsetgroup=1
    ))
    
    fig.update_layout(
    dragmode=False,
    xaxis=dict(fixedrange=True),
        title='Vendas por Grupo de Produtos',
        barmode='group',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        height=400,
        yaxis=dict(
            fixedrange=True,
            title="Valor (R$)",
            tickfont=dict(color="#2E8B57"),
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            side='left'
        ),
        yaxis2=dict(
            fixedrange=True,
            title="Quantidade (Kg)",
            tickfont=dict(color="#4169E1"),
            showgrid=False,
            side='right',
            overlaying='y'
        ),
        margin=dict(l=50, r=50, t=60, b=20),
        paper_bgcolor='white'
    )
    
    return fig

def create_top_products_chart(data):
    # Ordenar por valor de venda (assumindo que existe o campo VALOR_VENDA)
    sorted_data = sorted(data, key=lambda x: float(x['VALOR_VENDA']), reverse=True)[:10]
    
    fig = go.Figure()
    
    # Barra de valores (eixo Y primário)
    fig.add_trace(go.Bar(
        name='Valor (R$)',
        y=[d['TEXTO_PRODUTO'] for d in reversed(sorted_data)],
        x=[float(d['VALOR_VENDA']) for d in reversed(sorted_data)],
        orientation='h',
        text=[format_currency(float(d['VALOR_VENDA']), 'BRL', locale='pt_BR') for d in reversed(sorted_data)],
        textposition='auto',
        marker_color='#2E8B57',
        offsetgroup=0
    ))
    
    # Barra de quantidade (eixo Y secundário)
    fig.add_trace(go.Bar(
        name='Quantidade (Kg)',
        y=[d['TEXTO_PRODUTO'] for d in reversed(sorted_data)],
        x=[float(d['QUANTIDADE_VENDIDA']) for d in reversed(sorted_data)],
        orientation='h',
        text=[f"{float(d['QUANTIDADE_VENDIDA']):,.2f} Kg" for d in reversed(sorted_data)],
        textposition='auto',
        marker_color='#4169E1',
        offsetgroup=1,
        xaxis='x2'
    ))
    
    fig.update_layout(
        dragmode=False,
        yaxis=dict(fixedrange=True),
        title='Top 10 Produtos Mais Vendidos',
        barmode='group',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        height=600,
        xaxis=dict(
            fixedrange=True,
            title="Valor (R$)",
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            side='bottom'
        ),
        xaxis2=dict(
            fixedrange=True,
            title="Quantidade (Kg)",
            showgrid=False,
            side='top',
            overlaying='x'
        ),
        margin=dict(l=10, r=10, t=40, b=20),
        paper_bgcolor='white'
    )
    
    return fig

def create_expenses_chart(data):
    # Ordenar despesas por valor total e pegar as 15 maiores
    sorted_data = sorted(data, key=lambda x: float(x['TOTAL']), reverse=True)[:15]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=[f"{d['DESCRICAO']} ({d['CONTACX']})" for d in reversed(sorted_data)],  # Reversed para mostrar maior no topo
        x=[float(d['TOTAL']) for d in reversed(sorted_data)],
        orientation='h',
        text=[format_currency(float(d['TOTAL']), 'BRL', locale='pt_BR') for d in reversed(sorted_data)],
        textposition='auto',
        marker_color='#FF6B6B'
    ))
    
    fig.update_layout(
    dragmode=False,
    yaxis=dict(fixedrange=True),
        title='Top 15 Maiores Despesas',
        showlegend=False,
        plot_bgcolor='white',
        height=500,
        xaxis=dict(
            fixedrange=True,
            title="Valor (R$)",
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        ),
        margin=dict(l=10, r=10, t=40, b=20),
        paper_bgcolor='white'
    )
    
    return fig

def create_expenses_table(data):
    # Criar DataFrame com todas as despesas e ordenar por valor
    df = pd.DataFrame(data)
    df['TOTAL'] = pd.to_numeric(df['TOTAL'])  # Converter para número
    df = df.sort_values('TOTAL', ascending=False)  # Ordenar por valor
    df['TOTAL'] = df['TOTAL'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df = df.rename(columns={
        'CONTACX': 'Conta',
        'DESCRICAO': 'Descrição',
        'TOTAL': 'Valor'
    })
    return df

def main_page():
    with st.sidebar:
        st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            width: 300px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        st.title("Menu")
        user_data = st.session_state.user_data
        st.write(f"Welcome, {user_data['username']}!")
        
        selected_company = st.selectbox(
            "Selecione a Empresa:",
            options=[emp['nome'] for emp in st.session_state.user_data['empresas']],
            key='company_selector'
        )
        
        # Update company data when selection changes
        for company in st.session_state.user_data['empresas']:
            if company['nome'] == selected_company:
                st.session_state.company_data = company
                break
                
        col1, col2 = st.columns(2)
        with col1:
            data_inicial = st.date_input(
                "Data Inicial",
                value=datetime.now(),
                format="DD/MM/YYYY"
            )
        with col2:
            data_final = st.date_input(
                "Data Final",
                value=datetime.now(),
                format="DD/MM/YYYY"
            )
        
        if st.button("Consultar"):
            current_params = {
                'cnpj': st.session_state.company_data['cnpj'],
                'data_inicial': data_inicial.strftime('%Y-%m-%d'),
                'data_final': data_final.strftime('%Y-%m-%d')
            }
            
            if (st.session_state.last_query_params != current_params):
                with st.spinner('Consultando dados...'):
                    try:
                        data = fetch_api_data(st.session_state.company_data['urlapi'], st.session_state.company_data['cnpj'], 
                                            data_inicial.strftime('%Y-%m-%d'), 
                                            data_final.strftime('%Y-%m-%d'))
                        st.session_state.api_data = data
                        st.session_state.last_query_params = current_params
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro na consulta: {str(e)}")
            else:
                st.warning("Consulta com mesmos parâmetros já realizada")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.rerun()

        # Adicionar botão de admin para usuário admin
        if st.session_state.user_data['username'] == 'admin':
            st.divider()
            if st.button("Configurações Admin"):
                st.session_state.show_admin = not st.session_state.show_admin
    
    # Mostrar painel admin ou dashboard normal
    if st.session_state.show_admin and st.session_state.user_data['is_admin']:
        admin_settings()
    else:
        # Main content area
        st.markdown("""
            <style>
            .main .block-container {
                max-width: 100% !important;
                padding-top: 2rem !important;
                padding-right: 1rem !important;
                padding-left: 1rem !important;
                padding-bottom: 1rem !important;
            }
            .stMarkdown {
                margin-top: 1rem !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        if 'api_data' in st.session_state and st.session_state.api_data:
            data_vendas = st.session_state.api_data['vendas'][0]
            data_grupos = st.session_state.api_data['grupos']
            data_produtos = st.session_state.api_data['produtos']
            
            # Título do Dashboard com nome da filial
            st.header(f"Dashboard - {data_vendas['TEXTO_FILIAL']}")
            
            # Criar abas
            tab_receitas, tab_despesas = st.tabs(["Receitas", "Despesas"])
            
            # Aba de Receitas
            with tab_receitas:            
                # Primeira seção - Cards e gráfico de formas de pagamento
                left_col, right_col = st.columns([0.6, 0.4])
                
                with left_col:
                    # Primeira linha - 3 cards principais
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        create_metric_card("Vendas Totais", data_vendas['VALOR_TOTALVENDAS'], color="#2E8B57")
                    with col2:
                        create_metric_card("Ticket Médio", data_vendas['VALOR_TICKETMEDIO'], color="#4169E1")
                    with col3:
                        create_metric_card("Qtd. Vendas", data_vendas['TEXTO_QUANTIDADEVENDAS'], prefix="", color="#8A2BE2")
                    
                    # Segunda linha - 3 cards
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        create_metric_card("Vendas Dinheiro", data_vendas['VALOR_VENDADINHEIRO'], color="#20B2AA")
                    with col2:
                        create_metric_card("Vendas TEF", data_vendas['VALOR_VENDATEF'], color="#FF6347")
                    with col3:
                        create_metric_card("Vendas POS", data_vendas['VALOR_VENDAPOS'], color="#DAA520")
                    
                    # Terceira linha - 3 cards
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        create_metric_card("Vendas Cheque", data_vendas['VALOR_VENDACHEQUE'], color="#FF4500")
                    with col2:
                        create_metric_card("Vendas a Receber", data_vendas['VALOR_VENDARECEBER'], color="#4682B4")
                    with col3:
                        create_metric_card("Crédito Aproveitado", data_vendas['VALOR_CREDITOAPROVEITADO'], color="#6B8E23")
                
                with right_col:
                    st.plotly_chart(
                        create_payment_chart(data_vendas),
                        use_container_width=True,
                        config={'displayModeBar': False}
                    )
                
                # Segunda seção - Gráfico de grupos
                st.plotly_chart(
                    create_groups_chart(data_grupos),
                    use_container_width=True,
                    config={'displayModeBar': False}
                )
                
                # Terceira seção - Gráfico de produtos mais vendidos
                st.plotly_chart(
                    create_top_products_chart(data_produtos),
                    use_container_width=True,
                    config={'displayModeBar': False}
                )
            
            # Aba de Despesas
            with tab_despesas:
                if 'api_data' in st.session_state and 'despesas' in st.session_state.api_data:
                    data_despesas = st.session_state.api_data['despesas']
                    
                    # Gráfico das 15 maiores despesas
                    st.plotly_chart(
                        create_expenses_chart(data_despesas),
                        use_container_width=True,
                        config={'displayModeBar': False}
                    )
                    
                    # Tabela com todas as despesas
                    st.subheader("Todas as Despesas")
                    df_despesas = create_expenses_table(data_despesas)
                    st.dataframe(
                        df_despesas,
                        use_container_width=True,
                        hide_index=True
                    )


def main():
    init_session_state()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        main_page()

if __name__ == "__main__":
    main()


