import streamlit as st
import pandas as pd
import plotly.express as px # Opcional, mas deixa os gráficos bonitos

# Tenta importar a conexão do banco
try:
    from db import get_database
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from db import get_database

st.set_page_config(page_title="Painel Administrativo", page_icon="⚙️", layout="wide")

st.markdown("# ⚙️ Painel de Controle (Admin)")
st.markdown("Visão geral de todos os dados do sistema.")

# --- Verificação de Segurança (Simples) ---
# Só mostra os dados se estiver logado como admin (ou se você quiser testar livremente, comente essas linhas)
if st.session_state.get("user_role") != "admin":
    st.warning("🔒 Esta página é restrita para Administradores.")
    st.info("Faça login no menu lateral com o usuário: **admin** e senha: **123**")
    st.stop() # Para a execução aqui se não for admin

# --- Conexão com Banco ---
db = get_database()

if db is None:
    st.error("Erro ao conectar ao banco de dados.")
else:
    # Busca todos os dados
    vagas = list(db.vagas.find({}, {"_id": 0}))
    candidatos = list(db.candidatos.find({}, {"_id": 0}))

    # --- KPIs (Indicadores) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vagas", len(vagas))
    col2.metric("Candidatos Cadastrados", len(candidatos))
    col3.metric("Status do Sistema", "Online 🟢")

    st.divider()

    # --- Abas de Gerenciamento ---
    tab1, tab2, tab3 = st.tabs(["📊 Gráficos", "🏢 Todas as Vagas", "👥 Todos os Candidatos"])

    with tab1:
        st.subheader("Distribuição dos Dados")
        
        if len(vagas) > 0:
            c1, c2 = st.columns(2)
            
            # Gráfico de Vagas por Modelo (Remoto/Híbrido/Presencial)
            df_vagas = pd.DataFrame(vagas)
            if "tipo" in df_vagas.columns:
                contagem_tipo = df_vagas["tipo"].value_counts()
                st.bar_chart(contagem_tipo)
                st.caption("Vagas por Modelo de Trabalho")
            
        else:
            st.info("Faltam dados para gerar gráficos.")

    with tab2:
        st.subheader("📋 Banco de Vagas Completo")
        if len(vagas) > 0:
            df_vagas = pd.DataFrame(vagas)
            # Reordenando colunas para facilitar leitura
            cols = ["titulo", "empresa", "local", "salario", "senioridade"]
            # Garante que as colunas existem antes de filtrar
            cols_existentes = [c for c in cols if c in df_vagas.columns]
            st.dataframe(df_vagas[cols_existentes], use_container_width=True)
        else:
            st.warning("Nenhuma vaga encontrada.")

    with tab3:
        st.subheader("📋 Banco de Talentos Completo")
        if len(candidatos) > 0:
            df_candidatos = pd.DataFrame(candidatos)
            cols = ["nome", "email", "formacao", "pretensao", "skills"]
            cols_existentes = [c for c in cols if c in df_candidatos.columns]
            st.dataframe(df_candidatos[cols_existentes], use_container_width=True)
        else:
            st.warning("Nenhum candidato encontrado.")