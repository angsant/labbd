import streamlit as st
from datetime import datetime

# --- Importação da Conexão ---
try:
    from db import get_database
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from db import get_database

st.set_page_config(page_title="Meu Currículo", page_icon="👤")

# --- 🔒 Verificação de Segurança (Apenas Candidatos) ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Você precisa fazer login para acessar essa página.")
    st.stop()

if st.session_state["user_role"] != "candidato":
    st.error("🚫 Acesso negado. Apenas perfis de 'Candidato' podem cadastrar currículos.")
    st.stop()

# --- Interface ---
st.markdown(f"# 👤 Currículo de {st.session_state['user_name']}")
st.markdown("Mantenha seus dados atualizados para aplicar às vagas.")

# --- Busca dados existentes (Para preencher o formulário) ---
db = get_database()
dados_existentes = {}

if db is not None:
    # Tenta achar o currículo pelo nome do usuário logado
    dados_existentes = db.candidatos.find_one({"nome": st.session_state["user_name"]}) or {}

# --- Formulário Estrito (Campos Solicitados) ---
with st.form("form_candidato"):
    st.subheader("Dados Pessoais & Formação")
    
    # Campo 1: Nome (Vem automático do login, mas permitimos edição para o currículo)
    nome = st.text_input("Nome Completo", value=dados_existentes.get("nome", st.session_state["user_name"]))
    
    # Campo 2: Formação
    opcoes_formacao = ["Ensino Médio", "Cursando Superior", "Superior Completo", "Pós-Graduação", "Mestrado/Doutorado"]
    idx_formacao = 0
    if "formacao" in dados_existentes and dados_existentes["formacao"] in opcoes_formacao:
        idx_formacao = opcoes_formacao.index(dados_existentes["formacao"])
        
    formacao = st.selectbox("Formação Acadêmica", opcoes_formacao, index=idx_formacao)
    
    # Campo 3: Idiomas
    idiomas = st.text_input("Idiomas", 
                           value=dados_existentes.get("idiomas", ""),
                           placeholder="Ex: Inglês Intermediário, Espanhol Básico")

    st.divider()
    st.subheader("Perfil Profissional")

    # Campo 4: Resumo
    resumo = st.text_area("Resumo Profissional", 
                         value=dados_existentes.get("resumo", ""),
                         help="Um breve texto sobre quem você é e seus objetivos.")

    # Campo 5: Experiência
    experiencia = st.text_area("Experiência Profissional", 
                              value=dados_existentes.get("experiencia", ""),
                              placeholder="Empresas onde trabalhou, cargos e períodos.")

    # Campo 6: Habilidades (Skills)
    skills = st.text_area("Habilidades e Tecnologias", 
                         value=dados_existentes.get("skills", ""),
                         placeholder="Ex: Python, Excel, Vendas, Liderança...")

    submitted = st.form_submit_button("💾 Salvar / Atualizar Currículo")

    if submitted:
        if not nome or not skills or not resumo:
            st.warning("⚠️ Preencha pelo menos Nome, Resumo e Habilidades.")
        else:
            if db is not None:
                # Objeto com EXATAMENTE os campos pedidos
                perfil_atualizado = {
                    "nome": nome,
                    "formacao": formacao,
                    "idiomas": idiomas,
                    "resumo": resumo,
                    "experiencia": experiencia,
                    "skills": skills,
                    "data_atualizacao": datetime.now(),
                    # Mantemos o vínculo com o usuário do sistema
                    "username_vinculo": st.session_state.get("user_name") 
                }
                
                try:
                    # UPDATE_ONE com UPSERT=True
                    # Se achar o nome, atualiza. Se não achar, cria novo.
                    db.candidatos.update_one(
                        {"nome": nome}, 
                        {"$set": perfil_atualizado}, 
                        upsert=True
                    )
                    st.success("✅ Currículo salvo com sucesso! Agora você pode aplicar para as vagas na tela inicial.")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.error("Erro de conexão com o banco.")