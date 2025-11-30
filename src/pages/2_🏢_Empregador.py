import streamlit as st
import pandas as pd
from datetime import datetime
try:
    from db import get_database
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from db import get_database

st.set_page_config(page_title="Área do Empregador", page_icon="🏢")

st.markdown("# 🏢 Gestão de Vagas")

tab1, tab2 = st.tabs(["Nova Vaga", "Vagas Cadastradas"])

# --- ABA 1: Cadastrar Nova Vaga ---
with tab1:
    st.markdown("### Cadastrar Nova Oportunidade")
    
    with st.form("form_vaga"):
        titulo = st.text_input("Título da Vaga*", placeholder="Ex: Desenvolvedor Full Stack Jr")
        empresa = st.text_input("Nome da Empresa*", placeholder="Ex: Tech Solutions")
        
        c1, c2 = st.columns(2)
        with c1:
            local = st.text_input("Localização*", placeholder="Ex: Remoto, São Paulo - SP")
            tipo = st.selectbox("Modelo", ["Remoto", "Híbrido", "Presencial"])
        with c2:
            salario = st.text_input("Faixa Salarial", placeholder="Ex: R$ 5.000 - R$ 7.000")
            senioridade = st.selectbox("Nível", ["Estágio", "Júnior", "Pleno", "Sênior", "Especialista"])
        
        descricao = st.text_area("Descrição da Vaga*", height=150)
        requisitos = st.text_area("Requisitos e Tecnologias*", placeholder="Ex: Python, Django, SQL, Inglês Avançado")
        
        # Botão de envio
        submitted = st.form_submit_button("📢 Publicar Vaga")
        
        if submitted:
            if not titulo or not empresa or not descricao:
                st.warning("Preencha os campos obrigatórios!")
            else:
                db = get_database()
                if db is not None:
                    nova_vaga = {
                        "titulo": titulo,
                        "empresa": empresa,
                        "local": local,
                        "tipo": tipo,
                        "salario": salario,
                        "senioridade": senioridade,
                        "descricao": descricao,
                        "requisitos": requisitos,
                        "data_criacao": datetime.now()
                    }
                    try:
                        db.vagas.insert_one(nova_vaga)
                        st.success(f"Vaga **{titulo}** publicada com sucesso!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

# --- ABA 2: Visualizar Vagas do Banco ---
with tab2:
    st.markdown("### Vagas Ativas no Banco de Dados")
    
    # Botão para atualizar a lista
    if st.button("🔄 Atualizar Lista"):
        st.rerun()
        
    db = get_database()
    if db is not None:
        # Busca todas as vagas no MongoDB
        vagas = list(db.vagas.find({}, {"_id": 0})) # Traz tudo menos o ID interno
        
        if len(vagas) > 0:
            df_vagas = pd.DataFrame(vagas)
            # Mostra uma tabela interativa
            st.dataframe(
                df_vagas, 
                column_config={
                    "titulo": "Cargo",
                    "empresa": "Empresa",
                    "salario": "Salário",
                    "data_criacao": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhuma vaga cadastrada ainda.")