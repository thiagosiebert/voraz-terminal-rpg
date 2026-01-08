import streamlit as st
import google.generativeai as genai

# Configuração da Página
st.set_page_config(page_title="Voraz Terminal", page_icon="📡")

# --- ESTILO CSS (Sombra/Cyberpunk) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0a0e05;
        color: #00ff41;
        font-family: 'Courier New', Courier, monospace;
    }
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    .stChatMessage {
        background-color: #1a1a1a;
        border: 1px solid #00ff41;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    /* Efeito de Scanline */
    .stApp::before {
        content: " ";
        display: block;
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                    linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        z-index: 2;
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 CONEXÃO ESTABELECIDA: V-R-Z")
st.write("---")

# --- CONFIGURAÇÃO DA API ---
# No Streamlit Cloud, adicione GEMINI_API_KEY nos 'Secrets'
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- FUNÇÃO PARA CARREGAR O PROMPT EXTERNO ---
def load_prompt(file_path="voraz_prompt.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return "Erro ao carregar prompt: Você é uma IA genérica."

# Carrega o conteúdo do arquivo txt
SYSTEM_PROMPT = load_prompt()

model = genai.GenerativeModel(
    model_name="models/gemini-1.5-pro-latest",
    system_instruction=SYSTEM_PROMPT
)

# --- CHAT INTERFACE ---
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
        # Aqui o Voraz responde
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]
        ])
        response = chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
