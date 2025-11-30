import streamlit as st
import pandas as pd
import time
# Tenta importar a conexão do banco
try:
    from db import get_database
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from db import get_database

# --- Configuração da Página ---
st.set_page_config(
    page_title="Portal de Vagas",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Autenticação (Simples) ---
# Em um projeto real, esses usuários viriam do banco de dados com senha criptografada.
USUARIOS_MOCK = {
    "admin": {"senha": "123", "role": "admin", "nome": "Administrador Sistema"},
    "empresa": {"senha": "123", "role": "empregador", "nome": "Recrutador Tech"},
    "candidato": {"senha": "123", "role": "candidato", "nome": "João da Silva"},
}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None

def login_user(username, password):
    if username in USUARIOS_MOCK and USUARIOS_MOCK[username]["senha"] == password:
        st.session_state["logged_in"] = True
        st.session_state["user_role"] = USUARIOS_MOCK[username]["role"]
        st.session_state["user_name"] = USUARIOS_MOCK[username]["nome"]
        st.success(f"Bem-vindo, {st.session_state['user_name']}!")
        time.sleep(1)
        st.rerun()
    else:
        st.error("Usuário ou senha incorretos")

def logout_user():
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None
    st.rerun()

# --- Barra Lateral ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2910/2910791.png", width=100)
    st.title("Menu Principal")
    
    if not st.session_state["logged_in"]:
        st.subheader("Login")
        user = st.text_input("Usuário")
        pwd = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            login_user(user, pwd)
        st.info("Teste com: admin/123, empresa/123 ou candidato/123")
    else:
        st.write(f"Olá, **{st.session_state['user_name']}**")
        st.write(f"Perfil: *{st.session_state['user_role'].capitalize()}*")
        
        st.divider()
        st.write("📍 **Navegação:**")
        
        if st.session_state["user_role"] == "candidato":
            st.page_link("pages/1_👤_Candidato.py", label="Meu Currículo", icon="📄")
        elif st.session_state["user_role"] == "empregador":
            st.page_link("pages/2_🏢_Empregador.py", label="Gerenciar Vagas", icon="📢")
        elif st.session_state["user_role"] == "admin":
            st.page_link("pages/3_⚙️_Admin.py", label="Painel Admin", icon="📊")
            
        st.page_link("pages/4_🤖_Assistente_IA.py", label="Assistente IA", icon="🤖")
        
        st.divider()
        if st.button("Sair"):
            logout_user()

# --- Área Principal ---
st.title("💼 Vagas em Aberto")
st.markdown("Confira as oportunidades mais recentes do mercado.")
st.divider()

# --- Busca de Vagas no Banco ---
db = get_database()
vagas_lista = []

if db is not None:
    # Busca todas as vagas ordenadas por data (mais recentes primeiro)
    vagas_lista = list(db.vagas.find({}, {"_id": 0}).sort("data_criacao", -1))

col1, col2 = st.columns([2, 1])

with col1:
    if len(vagas_lista) == 0:
        st.info("Nenhuma vaga cadastrada no momento.")
    else:
        for vaga in vagas_lista:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.subheader(vaga.get("titulo", "Sem Título"))
                    st.caption(f"🏢 {vaga.get('empresa', 'Empresa')} | 📍 {vaga.get('local', 'Remoto')}")
                    # Mostra só os primeiros 100 caracteres da descrição
                    desc = vaga.get('descricao', '')
                    st.write(desc[:150] + "..." if len(desc) > 150 else desc)
                    st.markdown(f"**Requisitos:** {vaga.get('requisitos', 'Não informado')}")
                with c2:
                    st.write(f"💰 {vaga.get('salario', 'A combinar')}")
                    st.write(f"🏷️ {vaga.get('tipo', '-')}")
                    
                    if st.session_state["logged_in"] and st.session_state["user_role"] == "candidato":
                        if st.button("Aplicar", key=f"btn_{vaga['titulo']}"):
                             st.toast(f"Aplicação enviada para {vaga['empresa']}!", icon="✅")
                    else:
                        st.button("Login p/ Aplicar", key=f"btn_l_{vaga['titulo']}", disabled=True)

with col2:
    st.info("💡 **Dica:** Utilize nosso Assistente de IA para encontrar a vaga ideal.")
    # Mapa placeholder (Futuro: Usar latitude/longitude reais)
    st.write("🗺️ **Mapa de Vagas** (Demo)")
    st.map(pd.DataFrame({'lat': [-23.5505], 'lon': [-46.6333]}))