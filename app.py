import streamlit as st
from google import genai
from google.genai import types
import logging
import time
import random

# Configuração de Log
logging.basicConfig(level=logging.INFO)

# Configuração da Página
st.set_page_config(page_title="VRZ TERMINAL", page_icon="⚪", layout="centered")

# --- ESTILO CSS: PROTOCOLO MU/TH/UR ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Michroma&family=VT323&display=swap');

    /* Variáveis de Cor */
    :root {
        --dante-color: #33ff33;
        --vrz-color: #b3e5fc; /* Tom metálico/esferizado */
        --bg-color: #050801;
    }

    .stApp { 
        background-color: var(--bg-color); 
        color: var(--dante-color);
    }

    /* Remoção de Containers do Streamlit */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-bottom: 5px !important;
    }
    
    [data-testid="stChatMessageContent"] {
        padding-top: 0 !important;
    }

    /* Fontes Diferenciadas */
    .prefix-font {
        font-family: 'Michroma', sans-serif;
        font-size: 0.9rem;
        letter-spacing: 2px;
        font-weight: bold;
    }

    .message-font {
        font-family: 'VT323', monospace;
        font-size: 1.5rem;
        line-height: 1.2;
    }

    /* Cores Específicas */
    .dante-msg { color: var(--dante-color); text-shadow: 0 0 8px rgba(51, 255, 51, 0.6); }
    .vrz-msg { color: var(--vrz-color); text-shadow: 0 0 10px rgba(179, 229, 252, 0.8); }

    /* Efeitos CRT (Flicker e Scanlines) */
    .stApp::after {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: radial-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.3) 100%),
                    linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%);
        z-index: 10;
        pointer-events: none;
    }

    @keyframes flicker {
        0% { opacity: 0.97; }
        10% { opacity: 0.95; }
        20% { opacity: 0.98; }
        100% { opacity: 1; }
    }
    .stApp { animation: flicker 0.1s infinite; }

    /* Título do Terminal */
    .vrz-header {
        font-family: 'Michroma', sans-serif;
        color: var(--vrz-color);
        text-align: center;
        border-bottom: 1px solid var(--vrz-color);
        padding-bottom: 10px;
        margin-bottom: 40px;
        text-shadow: 0 0 15px var(--vrz-color);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="vrz-header">VRZ // TRANS-UMBRA INTERFACE v4.1</div>', unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- FUNÇÃO DE CARREGAMENTO DINÂMICO ---
def load_vrz_consciousness():
    files = {
        "DIRETIVAS": "prompt_diretivas.txt",
        "MEMORIAS": "prompt_memorias.txt",
        "COSMOLOGIA": "prompt_cosmologia.txt"
    }
    full_context = ""
    for section, filename in files.items():
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                full_context += f"\n\n=== {section} ===\n{content}"
        except Exception as e:
            logging.warning(f"Falha ao carregar {section}: {e}")
    
    return full_context if full_context else "Você é VRZ."

# Carregamos tudo antes de iniciar a interface
SYSTEM_PROMPT = load_vrz_consciousness()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibição das mensagens (Sem caixas)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="prefix-font dante-msg">🐺 DANTE ></div><div class="message-font dante-msg">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="prefix-font vrz-msg">⚪ VRZ ></div><div class="message-font vrz-msg">{message["content"]}</div>', unsafe_allow_html=True)

# Entrada do Dante
if prompt := st.chat_input("DIGITE O COMANDO..."):
    # Dante
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="prefix-font dante-msg">🐺 DANTE ></div><div class="message-font dante-msg">{prompt}</div>', unsafe_allow_html=True)

    # VRZ
    placeholder_prefix = st.empty()
    placeholder_msg = st.empty()
    
    placeholder_prefix.markdown('<div class="prefix-font vrz-msg">⚪ VRZ ></div>', unsafe_allow_html=True)
    placeholder_msg.markdown('<div class="message-font vrz-msg">`SINTONIZANDO ESFERA...`</div>', unsafe_allow_html=True)

    try:
        history = []
        for m in st.session_state.messages[:-1]:
            role = "model" if m["role"] == "assistant" else "user"
            history.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

        chat = client.chats.create(
            model="gemini-2.5-flash", 
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            history=history
        )
        
        response = chat.send_message(prompt)
        full_response = response.text
        
        # --- EFEITO DE DIGITAÇÃO "ALIEN" ---
        typed_text = ""
        for char in full_response:
            typed_text += char
            placeholder_msg.markdown(f'<div class="message-font vrz-msg">{typed_text}█</div>', unsafe_allow_html=True)
            
            # Velocidade de suspense: entre 0.05 e 0.12s
            delay = random.uniform(0.05, 0.12)
            
            if char in [".", "!", "?", ":"]:
                delay += 0.5 # Pausa dramática no fim de frases
            elif char == ",":
                delay += 0.2
                
            time.sleep(delay)
        
        placeholder_msg.markdown(f'<div class="message-font vrz-msg">{full_response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"HARDWARE FAILURE: {e}")
