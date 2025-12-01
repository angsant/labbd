import streamlit as st
import pandas as pd
import time
from datetime import datetime

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

# --- Funções de Autenticação no Banco ---
def verificar_login(username, senha):
    db = get_database()
    if db is None:
        return None
    
    # Busca o usuário no banco
    usuario = db.usuarios.find_one({"username": username, "senha": senha})
    return usuario

def criar_usuario(nome, username, senha, role):
    db = get_database()
    if db is None:
        return False
    
    # Verifica se já existe
    if db.usuarios.find_one({"username": username}):
        st.sidebar.error("⚠️ Este usuário já existe!")
        return False
    
    # Cria novo usuário
    novo_usuario = {
        "nome": nome,
        "username": username,
        "senha": senha, # Em projeto real, usaríamos hash (criptografia)
        "role": role,
        "data_criacao": datetime.now()
    }
    db.usuarios.insert_one(novo_usuario)
    return True

# --- Inicialização da Sessão ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None

def logout_user():
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None
    st.rerun()

# --- Barra Lateral (Login e Cadastro) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2910/2910791.png", width=100)
    st.title("Acesso ao Portal")
    
    if not st.session_state["logged_in"]:
        # Abas para Alternar entre Login e Cadastro
        tab_login, tab_cadastro = st.tabs(["🔑 Login", "📝 Criar Conta"])
        
        # --- ABA DE LOGIN ---
        with tab_login:
            user = st.text_input("Usuário", key="login_user")
            pwd = st.text_input("Senha", type="password", key="login_pwd")
            
            if st.button("Entrar", key="btn_login"):
                usuario_encontrado = verificar_login(user, pwd)
                
                if usuario_encontrado:
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = usuario_encontrado["role"]
                    st.session_state["user_name"] = usuario_encontrado["nome"]
                    st.success(f"Olá, {st.session_state['user_name']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos")
            
            # Botão de emergência para criar o primeiro Admin se o banco estiver vazio
            db = get_database()
            if db is not None and db.usuarios.count_documents({}) == 0:
                if st.button("🆘 Criar Admin Padrão"):
                    criar_usuario("Administrador", "admin", "123", "admin")
                    st.success("Admin criado! (admin/123)")

        # --- ABA DE CADASTRO ---
        with tab_cadastro:
            st.markdown("### Novo Cadastro")
            new_nome = st.text_input("Nome Completo")
            new_user = st.text_input("Usuário (Login)")
            new_pwd = st.text_input("Senha", type="password")
            new_role = st.selectbox("Perfil", ["candidato", "empregador", "admin"])
            
            if st.button("Cadastrar-se"):
                if new_user and new_pwd and new_nome:
                    if criar_usuario(new_nome, new_user, new_pwd, new_role):
                        st.success("Conta criada! Faça login na outra aba.")
                else:
                    st.warning("Preencha todos os campos.")

    else:
        # Se estiver logado
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
            
        st.page_link("pages/4_🤖_Assistente_IA.py", label="Busca Inteligente", icon="🔍")
        
        st.divider()
        if st.button("Sair"):
            logout_user()

# --- Área Principal (Listagem de Vagas) ---
st.title("💼 Vagas em Aberto")
st.markdown("Confira as oportunidades mais recentes do mercado.")
st.divider()

db = get_database()
vagas_lista = []

if db is not None:
    try:
        # Busca vagas ordenadas
        vagas_lista = list(db.vagas.find({}).sort("data_criacao", -1))
    except Exception:
        st.error("Erro ao buscar vagas.")

col1, col2 = st.columns([2, 1])

with col1:
    if len(vagas_lista) == 0:
        st.info("Nenhuma vaga cadastrada no momento.")
    else:
        for idx, vaga in enumerate(vagas_lista):
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.subheader(vaga.get("titulo", "Sem Título"))
                    st.caption(f"🏢 {vaga.get('empresa', 'Empresa')} | 📍 {vaga.get('local', 'Remoto')}")
                    desc = vaga.get('descricao', '')
                    st.write(desc[:150] + "..." if len(desc) > 150 else desc)
                    st.markdown(f"**Requisitos:** {vaga.get('requisitos', 'Não informado')}")
                with c2:
                    st.write(f"💰 {vaga.get('salario', 'A combinar')}")
                    st.write(f"🏷️ {vaga.get('tipo', '-')}")
                    
                    vaga_key = str(vaga.get('_id', idx))

                    if st.session_state["logged_in"] and st.session_state["user_role"] == "candidato":
                        if st.button("Aplicar", key=f"btn_{vaga_key}"):
                             st.toast(f"Aplicação enviada para {vaga.get('empresa')}!", icon="✅")
                    else:
                        #st.button("Login p/ Aplicar", key=f"btn_l_{vaga.get('titulo', 'x')}", disabled=True)
                        st.button("Login p/ Aplicar", key=f"btn_l_{vaga_key}", disabled=True)

with col2:
    st.info("💡 **Dica:** Utilize nosso Assistente de Busca para encontrar a vaga ideal.")
    # Exemplo simples de mapa
    st.write("🗺️ **Mapa de Vagas** (Demo)")
    st.map(pd.DataFrame({'lat': [-23.5505], 'lon': [-46.6333]}))