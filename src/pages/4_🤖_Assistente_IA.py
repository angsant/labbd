import streamlit as st
import time

try:
    from db import get_database
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from db import get_database

st.set_page_config(page_title="Busca & Matching", page_icon="🤖")

st.markdown("# 🤖 Sistema de Matching Automático")
st.markdown("Busca baseada em Full Text Search (MongoDB) com ranking de relevância (Score).")

tipo_busca = st.radio("O que você está procurando?", ["🔍 Vagas", "📄 Candidatos"], horizontal=True)

# --- Função de Busca com SCORE do MongoDB ---
def buscar_com_score(termo_busca, tipo):
    db = get_database()
    
    if db is None:
        return "Erro de conexão com o banco."

    # Se a busca estiver vazia, não faz nada
    if not termo_busca:
        return []

    # Configuração da Query do MongoDB Full Text Search
    # $text: procura nos índices criados
    # score: calcula a relevância
    query = {"$text": {"$search": termo_busca}}
    projecao = {"score": {"$meta": "textScore"}} # Pede para retornar o score
    ordenacao = [("score", {"$meta": "textScore"})] # Ordena do maior score para o menor

    if tipo == "🔍 Vagas":
        # projection (projecao) inclui o campo 'score' no resultado
        cursor = db.vagas.find(query, projecao).sort(ordenacao)
        return list(cursor)
                
    else: # Candidatos
        cursor = db.candidatos.find(query, projecao).sort(ordenacao)
        return list(cursor)

# --- Interface ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá! Digite skills ou palavras-chave para ver o matching por relevância."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ex: Python, Vendas, Gerente..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Calculando matching no MongoDB..."):
            
            resultados = buscar_com_score(prompt, tipo_busca)
            
            if isinstance(resultados, str):
                resposta = resultados
            elif len(resultados) > 0:
                resposta = f"Encontrei **{len(resultados)} matches** ordenados por relevância:\n\n"
                
                for item in resultados:
                    # Formata o Score para mostrar 2 casas decimais
                    score = round(item.get('score', 0), 2)
                    
                    if tipo_busca == "🔍 Vagas":
                        resposta += f"### 🏆 Score: {score} | {item.get('titulo')}\n"
                        resposta += f"- **Empresa:** {item.get('empresa')}\n"
                        resposta += f"- **Requisitos:** {item.get('requisitos')}\n\n"
                    else:
                        resposta += f"### 🏆 Score: {score} | {item.get('nome')}\n"
                        resposta += f"- **Skills:** {item.get('skills')}\n"
                        resposta += f"- **Resumo:** {item.get('resumo')}\n\n"
                        
                resposta += "---\n*O Score indica quantas vezes os termos aparecem e sua importância no texto.*"
            else:
                resposta = f"Nenhum match encontrado para '{prompt}' nos índices do banco."

            st.write(resposta)
    
    st.session_state.messages.append({"role": "assistant", "content": resposta})