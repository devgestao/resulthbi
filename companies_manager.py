import json
from pathlib import Path
import streamlit as st

def load_companies():
    with open('companies.json', 'r') as file:
        return json.load(file)['companies']

def save_companies(companies_data):
    with open('companies.json', 'w') as file:
        json.dump({'companies': companies_data}, file, indent=4)

def get_company_by_cnpj(cnpj):
    companies = load_companies()
    return next((company for company in companies if company['cnpj'] == cnpj), None)

def add_company(company_data):
    companies = load_companies()
    companies.append(company_data)
    save_companies(companies)

def update_company(cnpj, company_data):
    companies = load_companies()
    for i, company in enumerate(companies):
        if company['cnpj'] == cnpj:
            companies[i] = company_data
            break
    save_companies(companies)

def delete_company(cnpj):
    companies = load_companies()
    companies = [c for c in companies if c['cnpj'] != cnpj]
    save_companies(companies)

def admin_settings():
    from users_manager import save_users, load_users
    
    st.title("Configurações de Administrador")
    
    tab_users, tab_companies = st.tabs(["Usuários", "Empresas"])
    
    with tab_users:
        users_data = load_users()
        companies = load_companies()
        
        # Formulário de novo usuário
        with st.expander("➕ Novo Usuário", expanded=False):
            with st.form("new_user_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_username = st.text_input("Username")
                    new_password = st.text_input("Password", type="password")
                    new_email = st.text_input("Email")
                    new_is_admin = st.checkbox("Administrador")
                
                with col2:
                    new_empresas = st.multiselect(
                        "Empresas vinculadas",
                        options=[company['cnpj'] for company in companies]
                    )
                
                if st.form_submit_button("Criar Usuário"):
                    new_user = {
                        "username": new_username,
                        "password": new_password,
                        "email": new_email,
                        "is_admin": new_is_admin,
                        "empresas_vinculos": new_empresas
                    }
                    users_data.append(new_user)
                    save_users(users_data)
                    st.success("Usuário criado com sucesso!")
                    st.rerun()
        
        st.subheader("Gerenciar Usuários")
        for i, user in enumerate(users_data):
            with st.expander(f"Usuário: {user['username']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    user['username'] = st.text_input("Username", user['username'], key=f"username_{i}")
                    user['password'] = st.text_input("Password", user['password'], type="password", key=f"password_{i}")
                    user['email'] = st.text_input("Email", user['email'], key=f"email_{i}")
                    user['is_admin'] = st.checkbox("Administrador", value=user.get('is_admin', False), key=f"is_admin_{i}")
                
                with col2:
                    user['empresas_vinculos'] = st.multiselect(
                        "Empresas vinculadas",
                        options=[company['cnpj'] for company in companies],
                        default=user['empresas_vinculos'],
                        key=f"empresas_{i}"
                    )
                
                if st.button("Excluir", key=f"delete_{i}"):
                    users_data.pop(i)
        
        st.divider()
        if 'show_user_success' in st.session_state and st.session_state.show_user_success:
            st.success("✅ Alterações nos usuários salvas com sucesso!")
            st.session_state.show_user_success = False
            
        if st.button("Salvar Alterações"):
            try:
                save_users(users_data)
                st.session_state.show_user_success = True
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar alterações nos usuários: {str(e)}")
    
    with tab_companies:
        companies_data = load_companies()
        
        # Formulário de nova empresa
        with st.expander("➕ Nova Empresa", expanded=False):
            with st.form("new_company_form"):
                new_company_nome = st.text_input("Nome")
                new_company_cnpj = st.text_input("CNPJ")
                new_company_urlapi = st.text_input("URL API")
                
                st.subheader("Configurações")
                new_config = {
                    "CCMercRevenda": st.text_input("CCMercRevenda"),
                    "CCMateriaPrima": st.text_input("CCMateriaPrima"),
                    "CCTransferencia": st.text_input("CCTransferencia"),
                    "CCCompraExtra": st.text_input("CCCompraExtra"),
                    "CCBuscaVencimento": st.text_input("CCBuscaVencimento"),
                    "CCFinanciamento": st.text_input("CCFinanciamento"),
                    "CCRetiradaSocios": st.text_input("CCRetiradaSocios"),
                    "DeducaoDespesa": st.text_input("DeducaoDespesa"),
                    "OutrasReceitas": st.text_input("OutrasReceitas"),
                    "ContaAgrupaCaixa.01": st.text_input("ContaAgrupaCaixa.01"),
                    "ContasBancarias.01": st.text_input("ContasBancarias.01"),
                    "ConsideraPDV": st.checkbox("ConsideraPDV"),
                    "DiferencaCentroCusto": st.number_input("DiferencaCentroCusto", value=0.01)
                }
                
                if st.form_submit_button("Criar Empresa"):
                    new_company = {
                        "nome": new_company_nome,
                        "cnpj": new_company_cnpj,
                        "urlapi": new_company_urlapi,
                        "config": new_config
                    }
                    companies_data.append(new_company)
                    save_companies(companies_data)
                    st.success("Empresa criada com sucesso!")
                    st.rerun()
        
        st.subheader("Gerenciar Empresas")
        for i, company in enumerate(companies_data):
            with st.expander(f"Empresa: {company['nome']}", expanded=False):
                company['nome'] = st.text_input("Nome", company['nome'], key=f"comp_nome_{i}")
                company['cnpj'] = st.text_input("CNPJ", company['cnpj'], key=f"comp_cnpj_{i}")
                company['urlapi'] = st.text_input("URL API", company['urlapi'], key=f"comp_url_{i}")
                
                st.subheader("Configurações")
                for key in company['config'].keys():
                    if isinstance(company['config'][key], bool):
                        company['config'][key] = st.checkbox(key, company['config'][key], key=f"config_{key}_{i}")
                    else:
                        company['config'][key] = st.text_input(key, company['config'][key], key=f"config_{key}_{i}")
                
                if st.button("Excluir Empresa", key=f"delete_company_{i}"):
                    companies_data.pop(i)
        
        st.divider()
        if 'show_company_success' in st.session_state and st.session_state.show_company_success:
            st.success("✅ Alterações nas empresas salvas com sucesso!")
            st.session_state.show_company_success = False
            
        if st.button("Salvar Alterações de Empresas"):
            try:
                save_companies(companies_data)
                st.session_state.show_company_success = True
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar alterações nas empresas: {str(e)}")
