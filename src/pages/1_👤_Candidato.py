import streamlit as st
import pandas as pd
from datetime import datetime
# Importamos a função de conexão do arquivo db.py
# Como o app roda a partir da pasta src, basta importar 'db'
try:
    from db import get_database
except ImportError:
    # Fallback caso rode de pasta diferente
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from db import get_database

st.set_page_config(page_title="Cadastro de Candidato", page_icon="👤")

st.markdown("# 👤 Cadastro de Currículo")
st.markdown("Preencha seus dados para que as empresas encontrem você.")

# --- Formulário de Cadastro ---
with st.form("form_candidato"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome Completo*")
        email = st.text_input("Email*")
        telefone = st.text_input("Telefone")
        
    with col2:
        cidade = st.text_input("Cidade/Estado")
        formacao = st.selectbox("Formação Acadêmica", 
            ["Ensino Médio", "Cursando Superior", "Superior Completo", "Mestrado/Doutorado"])
        pretensao = st.number_input("Pretensão Salarial (R$)", min_value=0.0, step=100.0)

    st.divider()
    
    # Campos de Texto Longo (Importantes para a IA depois)
    resumo = st.text_area("Resumo Profissional*", 
        help="Fale um pouco sobre você. A IA usará isso para buscar seu perfil.")
    
    skills = st.text_area("Habilidades e Tecnologias*", 
        placeholder="Ex: Python, SQL, Comunicação, Vendas...")
    
    experiencia = st.text_area("Experiência Profissional", 
        placeholder="Descreva suas últimas experiências...")
    
    idiomas = st.text_input("Idiomas", placeholder="Ex: Inglês avançado, Espanhol básico")

    submitted = st.form_submit_button("💾 Salvar Currículo")

    if submitted:
        if not nome or not email or not skills:
            st.warning("⚠️ Preencha os campos obrigatórios (Nome, Email e Habilidades).")
        else:
            # --- Conexão com Banco de Dados ---
            db = get_database()
            
            if db is not None:
                # Cria o objeto (dicionário) para salvar
                novo_candidato = {
                    "nome": nome,
                    "email": email,
                    "telefone": telefone,
                    "cidade": cidade,
                    "formacao": formacao,
                    "pretensao": pretensao,
                    "resumo": resumo,
                    "skills": skills,
                    "experiencia": experiencia,
                    "idiomas": idiomas,
                    "data_cadastro": datetime.now()
                }
                
                try:
                    # Salva na coleção "candidatos"
                    db.candidatos.insert_one(novo_candidato)
                    st.success(f"✅ Sucesso! Currículo de **{nome}** cadastrado no banco!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")
            else:
                st.error("❌ Não foi possível conectar ao banco de dados. Verifique a senha no secrets.toml")