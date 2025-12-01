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
st.markdown("Gerencie todo o ecossistema: Dashboard, Vagas e Candidatos.")

db = get_database()
if db is None:
    st.error("Erro de conexão com o banco.")
    st.stop()

# --- Estrutura em Abas ---
tab_dash, tab_vagas, tab_candidatos = st.tabs(["📊 Visão Geral", "🏢 Gerenciar Vagas", "👥 Gerenciar Candidatos"])

# ==============================================================================
# ABA 1: DASHBOARD (VISUALIZAÇÃO)
# ==============================================================================
with tab_dash:
    st.subheader("Indicadores de Performance")
    
    # Busca dados atuais
    total_vagas = db.vagas.count_documents({})
    total_candidatos = db.candidatos.count_documents({})
    total_users = db.usuarios.count_documents({})

    col1, col2, col3 = st.columns(3)
    col1.metric("Vagas Totais", total_vagas)
    col2.metric("Candidatos Totais", total_candidatos)
    col3.metric("Usuários do Sistema", total_users)
    
    st.divider()
    
    # Gráfico simples
    vagas_dados = list(db.vagas.find({}, {"_id": 0, "tipo": 1}))
    if vagas_dados:
        df = pd.DataFrame(vagas_dados)
        if "tipo" in df.columns:
            fig = px.pie(df, names="tipo", title="Distribuição de Vagas por Modelo")
            st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# ABA 2: GERENCIAR VAGAS (CADASTRAR E VISUALIZAR)
# ==============================================================================
with tab_vagas:
    st.subheader("🏢 Controle de Vagas")
    
    with st.expander("➕ Cadastrar Nova Vaga (Modo Admin)"):
        with st.form("admin_form_vaga"):
            st.write("Preencha os dados para criar uma vaga manualmente:")
            a_titulo = st.text_input("Título")
            a_empresa = st.text_input("Empresa")
            
            c1, c2 = st.columns(2)
            a_local = c1.text_input("Local")
            a_tipo = c2.selectbox("Modelo", ["Remoto", "Híbrido", "Presencial"])
            
            a_desc = st.text_area("Descrição")
            a_req = st.text_area("Requisitos (Skills)")
            
            if st.form_submit_button("Criar Vaga"):
                nova_vaga = {
                    "titulo": a_titulo,
                    "empresa": a_empresa,
                    "local": a_local,
                    "tipo": a_tipo,
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
    else:
        st.info("Nenhuma vaga encontrada.")

# ==============================================================================
# ABA 3: GERENCIAR CANDIDATOS (CADASTRAR E VISUALIZAR)
# ==============================================================================
with tab_candidatos:
    st.subheader("👥 Controle de Candidatos")
    
    with st.expander("➕ Cadastrar Novo Candidato (Modo Admin)"):
        with st.form("admin_form_cand"):
            st.write("Cadastrar um perfil de candidato manualmente:")
            c_nome = st.text_input("Nome Completo")
            c_email = st.text_input("Email (Fictício)")
            c_skills = st.text_area("Habilidades (Ex: Python, Java)")
            c_resumo = st.text_area("Resumo Profissional")
            c_formacao = st.selectbox("Formação", ["Ensino Médio", "Superior", "Pós/Mestrado"])
            
            if st.form_submit_button("Criar Candidato"):
                novo_candidato = {
                    "nome": c_nome,
                    "email": c_email,
                    "skills": c_skills,
                    "resumo": c_resumo,
                    "formacao": c_formacao,
                    "data_atualizacao": datetime.now(),
                    "criado_por": "ADMIN"
                }
                # Usa update com upsert para evitar duplicar nome igual
                db.candidatos.update_one(
                    {"nome": c_nome}, 
                    {"$set": novo_candidato}, 
                    upsert=True
                )
                st.success("Candidato criado/atualizado pelo Admin!")
                st.rerun()

    st.write("### 📋 Todos os Candidatos no Banco")
    todos_cands = list(db.candidatos.find({}, {"_id": 0}))
    if todos_cands:
        st.dataframe(pd.DataFrame(todos_cands), use_container_width=True)
    else:
        st.info("Nenhum candidato encontrado.")