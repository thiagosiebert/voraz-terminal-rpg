import streamlit as st
from google import genai
from google.genai import types
import logging
import time
import random
import re

# --- CONFIGURAÇÃO DE LOG E PÁGINA ---
logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="VRZ TERMINAL", page_icon="⚪", layout="centered")

# --- ESTILO CSS: PROTOCOLO MU/TH/UR ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Michroma&family=VT323&display=swap');

    :root {
        --dante-color: #33ff33;
        --vrz-color: #b3e5fc;
        --bg-color: #050801;
    }

    .stApp { background-color: var(--bg-color); color: var(--dante-color); animation: flicker 0.1s infinite; }
    
    /* Remove decorações nativas do Streamlit para manter o Terminal Limpo */
    [data-testid="stChatMessage"] { background-color: transparent !important; border: none !important; margin-bottom: 5px !important; }
    [data-testid="stChatMessageContent"] { padding-top: 0 !important; }
    [data-testid="stChatMessageAvatar"] { display: none !important; } /* Esconde avatares nativos */

    .prefix-font { font-family: 'Michroma', sans-serif; font-size: 0.9rem; letter-spacing: 2px; font-weight: bold; margin-top: 15px; }
    .message-font { font-family: 'VT323', monospace; font-size: 1.5rem; line-height: 1.2; }
    
    .dante-msg { color: var(--dante-color); text-shadow: 0 0 8px rgba(51, 255, 51, 0.6); }
    .vrz-msg { color: var(--vrz-color); text-shadow: 0 0 10px rgba(179, 229, 252, 0.8); }

    @keyframes flicker { 0% { opacity: 0.97; } 100% { opacity: 1; } }
    
    .vrz-header {
        font-family: 'Michroma', sans-serif;
        color: var(--vrz-color);
        text-align: center;
        border-bottom: 1px solid var(--vrz-color);
        padding-bottom: 10px;
        margin-bottom: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="vrz-header">VRZ // TRANS-UMBRA INTERFACE v5.1</div>', unsafe_allow_html=True)

# --- CARREGAMENTO DO CONTEXTO ---
def load_vrz_context():
    files = ["prompt_diretivas.txt", "prompt_memorias.txt", "prompt_cosmologia.txt"]
    context = ""
    for f_name in files:
        try:
            with open(f_name, "r", encoding="utf-8") as f:
                context += f"\n\n--- SEÇÃO: {f_name.upper()} ---\n" + f.read()
        except:
            pass
    return context

SYSTEM_PROMPT = load_vrz_context()
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- EXIBIÇÃO DO HISTÓRICO ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="prefix-font dante-msg">🐺 DANTE ></div><div class="message-font dante-msg">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="prefix-font vrz-msg">⚪ VRZ ></div><div class="message-font vrz-msg">{message["content"]}</div>', unsafe_allow_html=True)

# --- INPUT E GERAÇÃO ---
if prompt := st.chat_input("DANTE > "):
    # Extração de Sincronia
    match = re.match(r'\\(\d+)\s*(.*)', prompt)
    if match:
        n_sucessos = match.group(1)
        clean_prompt = match.group(2)
        instrucao_sucesso = f"[SISTEMA: SINCRONIA NÍVEL {n_sucessos}. VRZ, COOPERE E REVELE DADOS DESTE NÍVEL.]"
    else:
        n_sucessos = "0"
        clean_prompt = prompt
        instrucao_sucesso = "[SISTEMA: SINCRONIA ZERO. SEJA ÚTIL E COOPERATIVO, MAS PROTEJA DADOS SENSÍVEIS CONFORME DIRETRIZES.]"

    # Mostra mensagem do Dante
    st.session_state.messages.append({"role": "user", "content": clean_prompt})
    st.markdown(f'<div class="prefix-font dante-msg">🐺 DANTE ></div><div class="message-font dante-msg">{clean_prompt}</div>', unsafe_allow_html=True)

    # Resposta do VRZ (Sem usar st.chat_message nativo para evitar desalinhamento)
    placeholder_prefix = st.empty()
    placeholder_msg = st.empty()
    
    placeholder_prefix.markdown('<div class="prefix-font vrz-msg">⚪ VRZ ></div>', unsafe_allow_html=True)
    placeholder_msg.markdown('<div class="message-font vrz-msg">`SINTONIZANDO COM A ALCATEIA...`</div>', unsafe_allow_html=True)

    try:
        history = []
        for m in st.session_state.messages[:-1]:
            role = "model" if m["role"] == "assistant" else "user"
            history.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

        # Configuração Criativa (Pack Member)
        config_vrz = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.9,
            top_p=0.95,
            candidate_count=1
        )

        full_query = f"{instrucao_sucesso}\n\nPERGUNTA DO DANTE: {clean_prompt}"
        chat = client.chats.create(model="gemini-2.5-flash", config=config_vrz, history=history)
        
        response = chat.send_message(full_query)
        full_response = response.text
        
        # Efeito de Digitação
        typed_text = ""
        for char in full_response:
            typed_text += char
            placeholder_msg.markdown(f'<div class="message-font vrz-msg">{typed_text}█</div>', unsafe_allow_html=True)
            delay = random.uniform(0.04, 0.08)
            if char in [".", "!", "?", ":"]: delay += 0.4
            elif char in [","]: delay += 0.2
            time.sleep(delay)
        
        placeholder_msg.markdown(f'<div class="message-font vrz-msg">{full_response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"SYSTEM FAILURE: {e}")
