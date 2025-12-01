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

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Você precisa fazer login para acessar essa página.")
    st.stop()

if st.session_state["user_role"] != "empregador":
    st.error("🚫 Acesso negado. Apenas perfis de 'Empregador' podem gerenciar vagas.")
    st.stop()

st.markdown(f"# 🏢 Painel do Empregador")
st.markdown(f"Bem-vindo, **{st.session_state['user_name']}**.")

tab1, tab2 = st.tabs(["➕ Nova Vaga", "📋 Minhas Vagas & Candidatos"])

with tab1:
    st.markdown("### Cadastrar Nova Oportunidade")
    
    with st.form("form_vaga"):
        titulo = st.text_input("Título da Vaga*", placeholder="Ex: Desenvolvedor Full Stack Jr")
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
                        "criado_por": st.session_state["user_name"] 
                    }
                    try:
                        db.vagas.insert_one(nova_vaga)
                        st.success(f"Vaga **{titulo}** publicada com sucesso!")
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

with tab2:
    st.markdown("### Suas Vagas Publicadas")
    
    if st.button("🔄 Atualizar Painel"):
        st.rerun()
        
    db = get_database()
    if db is not None:
        usuario_atual = st.session_state["user_name"]
        
        filtro = {
            "$or": [
                {"criado_por": usuario_atual},
                {"empresa": usuario_atual}
            ]
        }
        minhas_vagas = list(db.vagas.find(filtro, {"_id": 0}).sort("data_criacao", -1))
        
        if len(minhas_vagas) > 0:
            st.info(f"Você tem {len(minhas_vagas)} vagas ativas.")
            
            for i, vaga in enumerate(minhas_vagas):
                with st.container(border=True):
                    col_info, col_status = st.columns([3, 1])
                    
                    with col_info:
                        st.subheader(vaga.get('titulo', 'Sem Título'))
                        st.markdown(f"📍 **Local:** {vaga.get('local')} | 💰 **Salário:** {vaga.get('salario')}")
                        st.caption(f"Publicado em: {vaga.get('data_criacao', datetime.now()).strftime('%d/%m/%Y')}")
                        st.markdown(f"**Descrição:**\n {vaga.get('descricao')}")
                        st.markdown(f"**Requisitos:**\n {vaga.get('requisitos')}")
                    
                    candidaturas = list(db.aplicacoes.find({
                        "vaga_titulo": vaga.get('titulo'),
                        "empresa_vaga": vaga.get('empresa')
                    }))
                    qtd_candidatos = len(candidaturas)

                    with col_status:
                        st.metric("Candidatos", qtd_candidatos)

                    if qtd_candidatos > 0:
                        with st.expander(f"👥 Ver {qtd_candidatos} Currículo(s) Recebido(s)"):
                            for cand in candidaturas:
                                nome_candidato = cand.get("candidato_username")
                                
                                perfil = db.candidatos.find_one({"username_vinculo": nome_candidato})
                                if not perfil:
                                    perfil = db.candidatos.find_one({"nome": nome_candidato})
                                
                                st.markdown("---")
                                if perfil:
                                    c1, c2 = st.columns([3, 1])
                                    with c1:
                                        st.markdown(f"**👤 {perfil.get('nome')}**")
                                        st.write(f"🎓 {perfil.get('formacao')} | 🗣️ {perfil.get('idiomas')}")
                                        st.write(f"🛠️ **Skills:** {perfil.get('skills')}")
                                        st.caption(f"📝 **Resumo:** {perfil.get('resumo')}")
                                    with c2:
                                        data_app = cand.get('data_aplicacao')
                                        if isinstance(data_app, datetime):
                                            st.caption(f"Aplicou: {data_app.strftime('%d/%m')}")
                                else:
                                    st.write(f"Usuário: {nome_candidato} (Perfil não preenchido)")
                    else:
                        st.caption("🚫 Nenhum candidato aplicou para esta vaga ainda.")

        else:
            st.warning("Você ainda não publicou nenhuma vaga.")
            st.write("Use a aba 'Nova Vaga' para começar.")