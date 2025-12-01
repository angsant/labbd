import streamlit as st
from pymongo import MongoClient
import certifi

@st.cache_resource
def get_database():
    try:
        uri = st.secrets["mongo"]["uri"]
        
        client = MongoClient(uri, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
        
        client.admin.command('ping')
        
        return client.portal_vagas
        
    except Exception as e:
        st.error(f"Erro ao conectar ao MongoDB: {e}")
        return None