import time
import streamlit as st
from google import genai
from google.genai import types
import logging

# Configuração de Log
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Voraz Terminal", page_icon="📡")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e05; color: #00ff41; font-family: 'Courier New', monospace; }
    .stChatMessage { background-color: #1a1a1a; border: 1px solid #00ff41; }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 CONEXÃO ESTABELECIDA: V-R-Z")

# --- INICIALIZAÇÃO DO CLIENTE ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Chave API ausente.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Função para carregar o prompt do arquivo
def load_prompt():
    try:
        with open("voraz_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Você é o Voraz, residente da Umbra."

SYSTEM_PROMPT = load_prompt()

# --- DEBUG: LISTAR MODELOS DISPONÍVEIS ---
# Isso vai aparecer no seu log 'Manage App' do Streamlit
try:
    models_list = [m.name for m in client.models.list()]
    logging.info(f"Modelos acessíveis por esta chave: {models_list}")
except Exception as e:
    logging.error(f"Não foi possível listar modelos: {e}")

# --- LÓGICA DO CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

import time
