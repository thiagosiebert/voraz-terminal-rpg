import streamlit as st
from google import genai
from google.genai import types
import logging
import time
import random

# Configuração de Log
logging.basicConfig(level=logging.INFO)

# Configuração da Página
st.set_page_config(page_title="Terminal V-R-Z", page_icon="🔮")

# --- ESTILO CSS AVANÇADO (Glitch & Flicker) ---
st.markdown("""
    <style>
    /* Fundo e Fonte Geral */
    .stApp { 
        background-color: #050801; 
        color: #00ff41; 
        font-family: 'Courier New', monospace; 
    }
    
    /* Efeito de Flicker (Tremido de luz) na tela toda */
    @keyframes flicker {
        0% { opacity: 0.98; }
        5% { opacity: 0.95; }
        10% { opacity: 0.9; }
        15% { opacity: 0.95; }
        20% { opacity: 0.98; }
        25% { opacity: 0.95; }
        80% { opacity: 0.98; }
        100% { opacity: 1; }
    }
    .stApp {
        animation: flicker 0.15s infinite;
    }

    /* Efeito Glitch no Título */
    .glitch {
        font-size: 2rem;
        font-weight: bold;
        text-transform: uppercase;
        position: relative;
        text-shadow: 0.05em 0 0 #00fffc, -0.03em -0.04em 0 #fc00ff,
                     0.025em 0.04em 0 #fffc00;
        animation: glitch 725ms infinite;
    }

    @keyframes glitch {
        0% { text-shadow: 0.05em 0 0 #00fffc, -0.03em -0.04em 0 #fc00ff, 0.025em 0.04em 0 #fffc00; }
        15% { text-shadow: 0.05em 0 0 #00fffc, -0.03em -0.04em 0 #fc00ff, 0.025em 0.04em 0 #fffc00; }
        16% { text-shadow: -0.05em -0.025em 0 #00fffc, 0.025em 0.035em 0 #fc00ff, -0.05em -0.05em 0 #fffc00; }
        49% { text-shadow: -0.05em -0.025em 0 #00fffc, 0.025em 0.035em 0 #fc00ff, -0.05em -0.05em 0 #fffc00; }
        50% { text-shadow: 0.03em 0.035em 0 #00fffc, 0.03em 0 0 #fc00ff, 0.05em -0.03em 0 #fffc00; }
        99% { text-shadow: 0.03em 0.035em 0 #00fffc, 0.03em 0 0 #fc00ff, 0.05em -0.03em 0 #fffc00; }
        100% { text-shadow: -0.025em 0 0 #00fffc, -0.025em -0.025em 0 #fc00ff, -0.025em -0.05em 0 #fffc00; }
    }

    /* Estilização das Mensagens */
    .stChatMessage { 
        background-color: rgba(26, 26, 26, 0.8); 
        border: 1px solid #00ff41; 
        border-radius: 0px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="glitch">📡 CONEXÃO TRANSDIMENSIONAL: V-O-R-A-Z</div>', unsafe_allow_html=True)
st.write("---")

# --- INICIALIZAÇÃO DO CLIENTE ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Chave API ausente.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def load_prompt():
    try:
        with open("voraz_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Você é o Voraz, uma esfera de mercúrio senciente residente na Umbra."

SYSTEM_PROMPT = load_prompt()

# --- LÓGICA DO CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico com os novos ícones
for message in st.session_state.messages:
    avatar = "🐺" if message["role"] == "user" else "⚪"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Dante, o que você descobriu?"):
    # Dante (User)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🐺"):
        st.markdown(prompt)

    # Voraz (Assistant)
    with st.chat_message("assistant", avatar="⚪"):
        placeholder = st.empty()
        placeholder.markdown("📡 *Sintonizando frequência na Umbra...*")
        
        # Retry logic
        max_retries = 3
        retry_delay = 1
        
        for i in range(max_retries):
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
                
                # --- EFEITO DE DIGITAÇÃO ---
                typed_text = ""
                for char in full_response:
                    typed_text += char
                    placeholder.markdown(typed_text + "▌")
                    # Ajuste a velocidade aqui (0.01 a 0.05 é o ideal)
                    time.sleep(0.02)
                
                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                break
                
            except Exception as e:
                if "503" in str(e) and i < max_retries - 1:
                    placeholder.markdown(f"⚠️ *Interferência detectada... Tentando reconectar ({i+1})...*")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    placeholder.error(f"📡 SINAL PERDIDO: {e}")
                    break
