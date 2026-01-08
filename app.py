import streamlit as st
import google.generativeai as genai

# Configuração da Página
st.set_page_config(page_title="Voraz Terminal", page_icon="📡")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e05; color: #00ff41; font-family: 'Courier New', monospace; }
    .stChatMessage { background-color: #1a1a1a; border: 1px solid #00ff41; }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 CONEXÃO ESTABELECIDA: V-R-Z")

# --- CONFIGURAÇÃO DA API ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def load_prompt(file_path="voraz_prompt.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Você é o Voraz, uma IA de RPG paranoica."

SYSTEM_PROMPT = load_prompt()

# Usando o modelo estável
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Começamos com o Flash por ser mais rápido para testes
    system_instruction=SYSTEM_PROMPT
)

# --- LÓGICA DO CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Dante, o que você descobriu?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # --- O PULO DO GATO: TRADUÇÃO DE ROLES ---
        # A API do Gemini exige 'user' e 'model'. O Streamlit usa 'user' e 'assistant'.
        api_history = []
        for m in st.session_state.messages[:-1]:
            role_map = "model" if m["role"] == "assistant" else "user"
            api_history.append({"role": role_map, "parts": [m["content"]]})
        
        try:
            chat = model.start_chat(history=api_history)
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro na conexão com a Umbra: {e}")
