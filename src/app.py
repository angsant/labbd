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
    return db.usuarios.find_one({"username": username, "senha": senha})

def criar_usuario(nome, username, senha, role):
    db = get_database()
    if db is None:
        return False
    if db.usuarios.find_one({"username": username}):
        st.sidebar.error("⚠️ Este usuário já existe!")
        return False
    novo_usuario = {
        "nome": nome,
        "username": username,
        "senha": senha, 
        "role": role,
        "data_criacao": datetime.now()
    }
    db.usuarios.insert_one(novo_usuario)
    return True

# --- Função para Salvar Aplicação ---
def salvar_aplicacao(vaga, usuario_candidato):
    db = get_database()
    if db is None:
        return False
    
    # Verifica se já aplicou para esta mesma vaga
    # Usamos o título e a empresa como chave única da vaga neste exemplo
    ja_aplicou = db.aplicacoes.find_one({
        "vaga_titulo": vaga["titulo"],
        "empresa_vaga": vaga["empresa"],
        "candidato_username": usuario_candidato
    })
    
    if ja_aplicou:
        return "duplicado"

    nova_aplicacao = {
        "vaga_titulo": vaga["titulo"],
        "empresa_vaga": vaga["empresa"],
        "candidato_username": usuario_candidato, # Quem aplicou
        "data_aplicacao": datetime.now()
    }
    db.aplicacoes.insert_one(nova_aplicacao)
    return "sucesso"

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

# --- Barra Lateral ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2910/2910791.png", width=100)
    st.title("Acesso ao Portal")
    
    if not st.session_state["logged_in"]:
        tab_login, tab_cadastro = st.tabs(["🔑 Login", "📝 Criar Conta"])
        
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
            
            # Admin de emergência
            db = get_database()
            if db is not None:
                if db.usuarios.count_documents({}) == 0:
                    st.divider()
                    if st.button("🆘 Criar Admin Padrão"):
                        criar_usuario("Administrador Sistema", "admin", "123", "admin")
                        st.success("Admin criado! (admin/123)")
                        time.sleep(1)
                        st.rerun()

        with tab_cadastro:
            st.markdown("### Novo Cadastro")
            new_nome = st.text_input("Nome Completo")
            new_user = st.text_input("Usuário (Login)")
            new_pwd = st.text_input("Senha", type="password")
            new_role = st.selectbox("Perfil", ["candidato", "empregador"])
            if st.button("Cadastrar-se"):
                if new_user and new_pwd and new_nome:
                    if criar_usuario(new_nome, new_user, new_pwd, new_role):
                        st.success("Conta criada! Faça login na outra aba.")
                else:
                    st.warning("Preencha todos os campos.")

    else:
        st.write(f"Olá, **{st.session_state['user_name']}**")
        st.write(f"Perfil: *{st.session_state['user_role'].capitalize()}*")
        st.divider()
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

# --- Área Principal ---
st.title("💼 Vagas em Aberto")
st.markdown("Confira as oportunidades mais recentes do mercado.")
st.divider()

db = get_database()
vagas_lista = []
if db is not None:
    try:
        vagas_lista = list(db.vagas.find({}, {"_id": 0}).sort("data_criacao", -1))
    except Exception:
        pass

col1, col2 = st.columns([2, 1])

with col1:
    if len(vagas_lista) == 0:
        st.info("Nenhuma vaga cadastrada no momento.")
    else:
        for i, vaga in enumerate(vagas_lista):
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
                    
                    if st.session_state["logged_in"] and st.session_state["user_role"] == "candidato":
                        # Chave única para o botão
                        key_btn = f"btn_aplicar_{i}"
                        if st.button("Aplicar Agora", key=key_btn):
                             resultado = salvar_aplicacao(vaga, st.session_state["user_name"])
                             if resultado == "sucesso":
                                 st.toast(f"Sucesso! Você aplicou para {vaga.get('empresa')}!", icon="✅")
                             elif resultado == "duplicado":
                                 st.toast("Você já aplicou para esta vaga antes.", icon="⚠️")
                             else:
                                 st.error("Erro ao aplicar.")
                    else:
                        st.button("Login p/ Aplicar", key=f"btn_l_{i}", disabled=True)

with col2:
    st.info("💡 **Dica:** Utilize nosso Assistente de Busca para encontrar a vaga ideal.")
    st.markdown("### 🗺️ Mapa de Oportunidades")
    
    COORDENADAS_CIDADES = {
        "sao paulo": [-23.5505, -46.6333], "sp": [-23.5505, -46.6333],
        "rio de janeiro": [-22.9068, -43.1729], "rj": [-22.9068, -43.1729],
        "belo horizonte": [-19.9167, -43.9345], "mg": [-19.9167, -43.9345],
        "curitiba": [-25.4284, -49.2733], "porto alegre": [-30.0346, -51.2177],
        "brasilia": [-15.7975, -47.8919], "df": [-15.7975, -47.8919],
        "salvador": [-12.9777, -38.5016], "recife": [-8.0476, -34.8770],
        "fortaleza": [-3.7172, -38.5434], "florianopolis": [-27.5954, -48.5480]
    }

    pontos_mapa = []
    for vaga in vagas_lista:
        local_texto = vaga.get("local", "").lower()
        local_texto = local_texto.replace("ã", "a").replace("á", "a").replace("â", "a").replace("é", "e").replace("í", "i").replace("ç", "c")
        
        for cidade, coords in COORDENADAS_CIDADES.items():
            if cidade in local_texto:
                pontos_mapa.append({"lat": coords[0], "lon": coords[1]})
                break 
    
    if len(pontos_mapa) > 0:
        df_mapa = pd.DataFrame(pontos_mapa)
        st.map(df_mapa, zoom=3)
    else:
        st.caption("Nenhuma vaga com localização presencial mapeada.")
        st.map(pd.DataFrame({'lat': [-15.7975], 'lon': [-47.8919]}), zoom=3)