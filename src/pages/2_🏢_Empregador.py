import streamlit as st
import pandas as pd
from datetime import datetime

# --- Importação da Conexão ---
try:
    from db import get_database
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from db import get_database

st.set_page_config(page_title="Área do Empregador", page_icon="🏢")

# --- 🔒 Verificação de Segurança (Apenas Empregadores) ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Você precisa fazer login para acessar essa página.")
    st.stop()

if st.session_state["user_role"] != "empregador":
    st.error("🚫 Acesso negado. Apenas perfis de 'Empregador' podem gerenciar vagas.")
    st.stop()

st.markdown(f"# 🏢 Gestão de Vagas")
st.markdown(f"Bem-vindo, **{st.session_state['user_name']}**. Gerencie suas oportunidades.")

tab1, tab2 = st.tabs(["Nova Vaga", "Minhas Vagas Publicadas"])

# --- ABA 1: Cadastrar Nova Vaga ---
with tab1:
    st.markdown("### Cadastrar Nova Oportunidade")
    
    with st.form("form_vaga"):
        titulo = st.text_input("Título da Vaga*", placeholder="Ex: Desenvolvedor Full Stack Jr")
        # Preenche automaticamente com o nome do usuário logado
        empresa = st.text_input("Nome da Empresa*", value=st.session_state.get("user_name", ""))
        
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
                        "data_criacao": datetime.now(),
                        # CAMPO CHAVE: Grava quem criou a vaga
                        "criado_por": st.session_state["user_name"] 
                    }
                    try:
                        db.vagas.insert_one(nova_vaga)
                        st.success(f"Vaga **{titulo}** publicada com sucesso!")
                        # Atualiza a página para a vaga aparecer na outra aba
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

# --- ABA 2: Visualizar APENAS as Vagas do Usuário ---
with tab2:
    st.markdown(f"### Vagas criadas por: {st.session_state['user_name']}")
    
    if st.button("🔄 Atualizar Lista"):
        st.rerun()
        
    db = get_database()
    if db is not None:
        # --- FILTRO APLICADO AQUI ---
        # Antes: find({}) -> Trazia tudo
        # Agora: find({"criado_por": ...}) -> Traz só as desse usuário
        usuario_atual = st.session_state["user_name"]
        
        # Filtra pelo campo 'criado_por' OU pelo nome da 'empresa' (para compatibilidade)
        filtro = {
            "$or": [
                {"criado_por": usuario_atual},
                {"empresa": usuario_atual}
            ]
        }
        
        minhas_vagas = list(db.vagas.find(filtro, {"_id": 0}))
        
        if len(minhas_vagas) > 0:
            df_vagas = pd.DataFrame(minhas_vagas)
            
            # Mostra tabela formatada
            st.dataframe(
                df_vagas, 
                column_config={
                    "titulo": "Cargo",
                    "empresa": "Empresa",
                    "local": "Local",
                    "tipo": "Modelo",
                    "data_criacao": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY")
                },
                use_container_width=True,
                hide_index=True
            )
            
            st.info(f"Você tem {len(minhas_vagas)} vaga(s) ativa(s).")
        else:
            st.warning("Você ainda não cadastrou nenhuma vaga.")