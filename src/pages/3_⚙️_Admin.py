import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Tenta importar a conexão do banco
try:
    from db import get_database
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from db import get_database

st.set_page_config(page_title="Painel Administrativo", page_icon="⚙️", layout="wide")

# --- 🔒 Verificação de Segurança ---
if "logged_in" not in st.session_state or st.session_state["user_role"] != "admin":
    st.warning("🔒 Acesso restrito para Administradores.")
    st.stop()

st.markdown("# ⚙️ Painel de Controle (Super Admin)")
st.markdown("Gerencie todo o ecossistema: Usuários, Vagas e Candidatos.")

db = get_database()
if db is None:
    st.error("Erro de conexão com o banco.")
    st.stop()

# --- Estrutura em 4 Abas ---
tab_dash, tab_users, tab_vagas, tab_candidatos = st.tabs([
    "📊 Visão Geral", 
    "🔑 Gerenciar Usuários", 
    "🏢 Gerenciar Vagas", 
    "👥 Gerenciar Currículos"
])

# ==============================================================================
# ABA 1: DASHBOARD (VISUALIZAÇÃO)
# ==============================================================================
with tab_dash:
    st.subheader("Indicadores de Performance")
    
    total_vagas = db.vagas.count_documents({})
    total_candidatos = db.candidatos.count_documents({})
    total_users = db.usuarios.count_documents({})

    col1, col2, col3 = st.columns(3)
    col1.metric("Vagas Totais", total_vagas)
    col2.metric("Candidatos Totais", total_candidatos)
    col3.metric("Usuários do Sistema", total_users)
    
    st.divider()
    
    vagas_dados = list(db.vagas.find({}, {"_id": 0, "tipo": 1}))
    if vagas_dados:
        df = pd.DataFrame(vagas_dados)
        if "tipo" in df.columns:
            fig = px.pie(df, names="tipo", title="Distribuição de Vagas por Modelo")
            st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# ABA 2: GERENCIAR USUÁRIOS (LOGIN) - NOVO!
# ==============================================================================
with tab_users:
    st.subheader("🔑 Cadastro de Usuários (Acesso ao Sistema)")
    st.info("Aqui você cria os logins para que as pessoas possam acessar o sistema.")
    
    with st.expander("➕ Criar Novo Usuário", expanded=True):
        with st.form("form_create_user_admin"):
            c1, c2 = st.columns(2)
            u_nome = c1.text_input("Nome Completo")
            u_role = c2.selectbox("Perfil de Acesso", ["candidato", "empregador", "admin"])
            
            c3, c4 = st.columns(2)
            u_login = c3.text_input("Usuário (Login)")
            u_senha = c4.text_input("Senha", type="password")
            
            if st.form_submit_button("Cadastrar Usuário"):
                if not u_login or not u_senha or not u_nome:
                    st.warning("Preencha todos os campos.")
                else:
                    # Verifica duplicidade
                    if db.usuarios.find_one({"username": u_login}):
                        st.error(f"O usuário '{u_login}' já existe!")
                    else:
                        novo_usuario = {
                            "nome": u_nome,
                            "username": u_login,
                            "senha": u_senha,
                            "role": u_role,
                            "data_criacao": datetime.now()
                        }
                        db.usuarios.insert_one(novo_usuario)
                        st.success(f"Usuário **{u_login}** ({u_role}) criado com sucesso!")
                        st.rerun()

    st.divider()
    st.write("### 📋 Usuários Cadastrados")
    
    users_list = list(db.usuarios.find({}, {"_id": 0, "senha": 0})) # Esconde a senha na listagem
    if users_list:
        st.dataframe(pd.DataFrame(users_list), use_container_width=True)
    else:
        st.info("Nenhum usuário encontrado.")

# ==============================================================================
# ABA 3: GERENCIAR VAGAS
# ==============================================================================
with tab_vagas:
    st.subheader("🏢 Controle de Vagas")
    
    with st.expander("➕ Cadastrar Nova Vaga (Modo Admin)"):
        with st.form("admin_form_vaga"):
            a_titulo = st.text_input("Título")
            a_empresa = st.text_input("Empresa")
            
            c1, c2 = st.columns(2)
            a_local = c1.text_input("Local")
            a_tipo = c2.selectbox("Modelo", ["Remoto", "Híbrido", "Presencial"])
            
            a_desc = st.text_area("Descrição")
            a_req = st.text_area("Requisitos (Skills)")
            
            # Ajuste de salário e senioridade que faltava antes
            c3, c4 = st.columns(2)
            a_salario = c3.text_input("Salário")
            a_senioridade = c4.selectbox("Senioridade", ["Júnior", "Pleno", "Sênior"])

            if st.form_submit_button("Criar Vaga"):
                nova_vaga = {
                    "titulo": a_titulo,
                    "empresa": a_empresa,
                    "local": a_local,
                    "tipo": a_tipo,
                    "salario": a_salario,
                    "senioridade": a_senioridade,
                    "descricao": a_desc,
                    "requisitos": a_req,
                    "data_criacao": datetime.now(),
                    "criado_por": "ADMIN"
                }
                db.vagas.insert_one(nova_vaga)
                st.success("Vaga criada pelo Admin!")
                st.rerun()

    st.write("### 📋 Todas as Vagas no Banco")
    todas_vagas = list(db.vagas.find({}, {"_id": 0}))
    if todas_vagas:
        st.dataframe(pd.DataFrame(todas_vagas), use_container_width=True)

# ==============================================================================
# ABA 4: GERENCIAR CURRÍCULOS
# ==============================================================================
with tab_candidatos:
    st.subheader("👥 Controle de Currículos (Perfis)")
    
    with st.expander("➕ Cadastrar Novo Currículo (Modo Admin)"):
        with st.form("admin_form_cand"):
            c_nome = st.text_input("Nome Completo")
            c_email = st.text_input("Email (Fictício)") # Mantido como campo extra
            
            c1, c2 = st.columns(2)
            c_formacao = c1.selectbox("Formação", ["Ensino Médio", "Superior", "Pós/Mestrado"])
            c_idiomas = c2.text_input("Idiomas")

            c_skills = st.text_area("Habilidades")
            c_resumo = st.text_area("Resumo Profissional")
            c_exp = st.text_area("Experiência")
            
            # Vínculo com usuário de login existente (Opcional, mas recomendado)
            c_username = st.text_input("Vincular ao usuário de login (Opcional)", placeholder="Digite o login do usuário se existir")

            if st.form_submit_button("Salvar Currículo"):
                novo_candidato = {
                    "nome": c_nome,
                    "email": c_email,
                    "formacao": c_formacao,
                    "idiomas": c_idiomas,
                    "skills": c_skills,
                    "resumo": c_resumo,
                    "experiencia": c_exp,
                    "data_atualizacao": datetime.now(),
                    "username_vinculo": c_username if c_username else None,
                    "criado_por": "ADMIN"
                }
                db.candidatos.update_one(
                    {"nome": c_nome}, 
                    {"$set": novo_candidato}, 
                    upsert=True
                )
                st.success("Currículo salvo pelo Admin!")
                st.rerun()

    st.write("### 📋 Todos os Currículos no Banco")
    todos_cands = list(db.candidatos.find({}, {"_id": 0}))
    if todos_cands:
        st.dataframe(pd.DataFrame(todos_cands), use_container_width=True)