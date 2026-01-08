import streamlit as st
from google import genai
from google.genai import types
import logging
import time
import random

# Configuração de Log
logging.basicConfig(level=logging.INFO)

# Configuração da Página
st.set_page_config(page_title="VRZ TERMINAL", page_icon="📟", layout="centered")

# --- ESTILO CSS: PROTOCOLO MU/TH/UR 6000 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    /* Fundo e Fonte Principal */
    .stApp { 
        background-color: #0d1107; 
        color: #33ff33; 
        font-family: 'VT323', monospace; 
        font-size: 1.2rem;
    }
    
    /* Efeito de Curvatura CRT e Glow */
    .stApp::after {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: radial-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 100%), 
                    linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), 
                    linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
        z-index: 2;
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
    }

    /* Scanlines */
    .stApp::before {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.15) 50%);
        z-index: 2;
        background-size: 100% 4px;
        pointer-events: none;
        animation: scanline 10s linear infinite;
    }

    @keyframes scanline {
        0% { background-position: 0 0; }
        100% { background-position: 0 100%; }
    }

    /* Brilho no Texto (Phosphor Glow) */
    h1, h2, h3, p, span, .stMarkdown {
        text-shadow: 0 0 5px rgba(51, 255, 51, 0.8);
    }

    /* Ajuste nas Caixas de Mensagem */
    .stChatMessage { 
        background-color: rgba(0, 40, 0, 0.2); 
        border: 1px solid #33ff33; 
        border-radius: 0px;
        margin-bottom: 10px;
        box-shadow: inset 0 0 10px rgba(0, 255, 0, 0.1);
    }

    /* Título Glitchado */
    .vrz-header {
        color: #33ff33;
        font-size: 2.5rem;
        text-align: center;
        letter-spacing: 5px;
        border-bottom: 2px solid #33ff33;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="vrz-header">INTERFACE VRZ v4.1 - MU/TH/UR PROTOCOL</div>', unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO CLIENTE ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def load_prompt():
    try:
        with open("voraz_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Você é VRZ, uma inteligência senciente em formato de esfera metálica na Umbra."

SYSTEM_PROMPT = load_prompt()

# --- LÓGICA DO CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "🐺" if message["role"] == "user" else "⚪"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("DANTE > "):
    # Dante
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🐺"):
        st.markdown(prompt)

    # VRZ
    with st.chat_message("assistant", avatar="⚪"):
        placeholder = st.empty()
        placeholder.markdown("`VRZ IS SEARCHING...`")
        
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
                placeholder.markdown(typed_text + "█") # Cursor em bloco estilo terminal
                
                # Velocidade de suspense: entre 0.05 e 0.1s
                # Adicionamos um pequeno random para não parecer robótico demais
                delay = random.uniform(0.04, 0.09)
                
                # Pausa maior em pontos e vírgulas para simular processamento
                if char in [".", "!", "?", ":"]:
                    delay += 0.4
                elif char == ",":
                    delay += 0.2
                    
                time.sleep(delay)
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"SYSTEM FAILURE: {e}")
