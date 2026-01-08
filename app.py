import streamlit as st
from google import genai
import logging

# Configuração da Página
st.set_page_config(page_title="Voraz Terminal", page_icon="📡")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e05; color: #00ff41; font-family: 'Courier New', monospace; }
    .stChatMessage { background-color: #1a1a1a; border: 1px solid #00ff41; }
    .stChatInput { border-top: 1px solid #00ff41; }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 CONEXÃO ESTABELECIDA: V-0-R-A-Z")

# --- CONFIGURAÇÃO DA API (NOVA SDK) ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("ERRO: Chave API ausente nos Secrets.")
    st.stop()

# Inicializa o cliente novo
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def load_prompt(file_path="voraz_prompt.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Você é o Voraz, uma IA de RPG paranoica residente na Umbra."

SYSTEM_PROMPT = load_prompt()

# --- LÓGICA DO CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Dante, o que você descobriu?"):
    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Na nova SDK, enviamos o sistema no 'config'
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                }
            )
            
            answer = response.text
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"FALHA NA SINTONIA: {e}")
            logging.error(f"Erro detalhado: {e}")
