import streamlit as st
from pymongo import MongoClient
import certifi

@st.cache_resource
def get_database():
    try:
        # Pega a string de conexão
        uri = st.secrets["mongo"]["uri"]
        
        # --- A MUDANÇA ESTÁ AQUI ---
        # Adicionamos tlsAllowInvalidCertificates=True para ignorar erros de SSL do Windows
        client = MongoClient(uri, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
        
        # Teste de conexão
        client.admin.command('ping')
        
        return client.portal_vagas
        
    except Exception as e:
        st.error(f"Erro ao conectar ao MongoDB: {e}")
        return None