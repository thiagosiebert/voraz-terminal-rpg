import streamlit as st
import google.generativeai as genai
import logging

# Configuração de logs para você ver no 'Manage App' do Streamlit
logging.basicConfig(level=logging.INFO)

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

st.title("📡 CONEXÃO ESTABELECIDA: V-R-Z")

# --- CONFIGURAÇÃO DA API ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("ERRO CRÍTICO: Chave API não encontrada nos Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def load_prompt(file_path="voraz_prompt.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Você é o Voraz, uma IA de RPG paranoica residente na Umbra."

SYSTEM_PROMPT = load_prompt()

# --- DIAGNÓSTICO DE MODELO ---
@st.cache_resource
def get_model():
    # Testamos o nome mais limpo possível
    model_name = "gemini-1.5-flash" 
    try:
        # Tenta instanciar o modelo
        m = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_PROMPT
        )
        return m
    except Exception as e:
        logging.error(f"Erro ao carregar {model_name}: {e}")
        # Fallback para o Pro caso o Flash dê erro de 404
        return genai.GenerativeModel(model_name="gemini-1.5-pro", system_instruction=SYSTEM_PROMPT)

model = get_model()

# --- LÓGICA DO CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Dante, o que você descobriu?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Tradução de roles Streamlit -> Gemini
        api_history = []
        for m in st.session_state.messages[:-1]:
            role = "model" if m["role"] == "assistant" else "user"
            api_history.append({"role": role, "parts": [m["content"]]})
        
        try:
            # Inicia o chat com o histórico formatado
            chat_session = model.start_chat(history=api_history)
            response = chat_session.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"ERRO DE CONEXÃO TRANSDIMENSIONAL: {e}")
            logging.error(f"Detalhes do erro: {e}")
