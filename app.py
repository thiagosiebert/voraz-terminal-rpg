import streamlit as st
from google import genai
from google.genai import types
import logging
import time
import random
import re

# --- CONFIGURAÇÃO DE LOG E PÁGINA ---
logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="VRZ TERMINAL v5.2", page_icon="⚪", layout="centered")

# --- ESTILO CSS: PROTOCOLO MU/TH/UR (ESTÉTICA ALIEN/FALLOUT) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Michroma&family=VT323&display=swap');

    :root {
        --dante-color: #33ff33;
        --vrz-color: #b3e5fc; /* Tom metálico da gota de mercúrio */
        --bg-color: #050801;
    }

    .stApp { background-color: var(--bg-color); color: var(--dante-color); animation: flicker 0.1s infinite; }
    
    /* Remove containers do Streamlit para o "Terminal Puro" */
    [data-testid="stChatMessage"] { background-color: transparent !important; border: none !important; margin-bottom: 5px !important; }
    [data-testid="stChatMessageContent"] { padding-top: 0 !important; }
    [data-testid="stChatMessageAvatar"] { display: none !important; } /* Esconde avatares nativos */

    /* Definição de Fontes */
    .prefix-font { font-family: 'Michroma', sans-serif; font-size: 0.9rem; letter-spacing: 2px; font-weight: bold; margin-top: 15px; }
    .message-font { font-family: 'VT323', monospace; font-size: 1.5rem; line-height: 1.2; }
    
    /* Brilho de Fósforo (Glow) */
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

st.markdown('<div class="vrz-header">VRZ // TRANS-UMBRA INTERFACE v5.2</div>', unsafe_allow_html=True)

# --- CARREGAMENTO DO CONTEXTO (BASE DE CONHECIMENTO) ---
def load_vrz_context():
    """
    Carrega os arquivos de Lore do repositório.
    Certifique-se de que 'prompt_memoriasv2.txt' é o nome do arquivo atualizado no Git.
    """
    files = ["prompt_diretivas.txt", "prompt_memoriasv2.txt", "prompt_cosmologia.txt"]
    context = ""
    for f_name in files:
        try:
            with open(f_name, "r", encoding="utf-8") as f:
                context += f"\n\n--- SEÇÃO: {f_name.upper()} ---\n" + f.read()
        except Exception as e:
            logging.warning(f"Erro ao carregar {f_name}: {e}")
    return context

# Inicialização global
SYSTEM_PROMPT = load_vrz_context()
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- EXIBIÇÃO DO HISTÓRICO ---
for message in st.session_state.messages:
    # Filtra para exibir apenas mensagens de usuário e assistente (ignora logs de ferramentas se houver)
    if message.get("role") == "user":
        st.markdown(f'<div class="prefix-font dante-msg">🐺 DANTE ></div><div class="message-font dante-msg">{message["content"]}</div>', unsafe_allow_html=True)
    elif message.get("role") == "assistant":
        st.markdown(f'<div class="prefix-font vrz-msg">⚪ VRZ ></div><div class="message-font vrz-msg">{message["content"]}</div>', unsafe_allow_html=True)

# --- INPUT E LÓGICA DO VRZ ---
if prompt := st.chat_input("DANTE > "):
    
    # 1. Extração de Sincronia (\n) via Regex
    match = re.match(r'\\(\d+)\s*(.*)', prompt)
    if match:
        n_sucessos = match.group(1)
        clean_prompt = match.group(2)
        instrucao_sucesso = f"[SISTEMA: SINCRONIA NÍVEL {n_sucessos}. LIBERE DADOS DESTA CATEGORIA.]"
    else:
        n_sucessos = "0"
        clean_prompt = prompt
        instrucao_sucesso = "[SISTEMA: SINCRONIA ZERO. SEJA PRÁTICO, BREVE (MÁX 300 CHARS) E COOPERATIVO.]"

    # 2. Registra e exibe mensagem do Dante (visual limpo)
    st.session_state.messages.append({"role": "user", "content": clean_prompt})
    st.markdown(f'<div class="prefix-font dante-msg">🐺 DANTE ></div><div class="message-font dante-msg">{clean_prompt}</div>', unsafe_allow_html=True)

    # 3. Bloco de Resposta do VRZ
    # Usamos st.empty() para evitar conflito com layouts nativos do Streamlit
    placeholder_prefix = st.empty()
    placeholder_msg = st.empty()
    
    placeholder_prefix.markdown('<div class="prefix-font vrz-msg">⚪ VRZ ></div>', unsafe_allow_html=True)
    placeholder_msg.markdown('<div class="message-font vrz-msg">`ACESSANDO REDE EXTERNA...`</div>', unsafe_allow_html=True)
    
    try:
        # Formatação do histórico para a API
        history = []
        for m in st.session_state.messages[:-1]:
            # Garante que apenas mensagens com conteúdo de texto sejam enviadas no histórico
            if m.get("content"):
                role = "model" if m["role"] == "assistant" else "user"
                history.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

        # --- CONFIGURAÇÃO 5.2: FERRAMENTAS E TEMPERATURA ---
        # Habilitamos o Google Search dentro da configuração
        tools = [types.Tool(google_search=types.GoogleSearch())]
        
        config_vrz = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,  # Reduzido para 0.7 para respostas mais diretas e práticas
            top_p=0.95,
            tools=tools,      # Habilita a busca na internet
            candidate_count=1
        )

        full_query = f"{instrucao_sucesso}\n\nPERGUNTA DO DANTE: {clean_prompt}"
        
        # Criação do Chat mantendo o modelo gemini-2.5-flash
        chat = client.chats.create(
            model="gemini-2.5-flash", 
            config=config_vrz, 
            history=history
        )
        
        response = chat.send_message(full_query)
        full_response = response.text
        
        # --- EFEITO DE DIGITAÇÃO ---
        typed_text = ""
        # Verifica se há texto na resposta (a busca pode retornar dados brutos às vezes)
        if full_response:
            for char in full_response:
                typed_text += char
                placeholder_msg.markdown(f'<div class="message-font vrz-msg">{typed_text}█</div>', unsafe_allow_html=True)
                
                # Velocidade ajustada: mais rápida (0.02-0.05) para refletir a nova personalidade "Prática"
                delay = random.uniform(0.02, 0.05) 
                
                if char in [".", "!", "?", ":"]:
                    delay += 0.3
                elif char == ",":
                    delay += 0.1
                    
                time.sleep(delay)
            
            # Finaliza a mensagem removendo o cursor
            placeholder_msg.markdown(f'<div class="message-font vrz-msg">{full_response}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            # Fallback seguro caso a ferramenta retorne algo que não gerou texto
            fallback_text = "`[DADOS EXTERNOS INTEGRADOS. SISTEMA ATUALIZADO.]`"
            placeholder_msg.markdown(f'<div class="message-font vrz-msg">{fallback_text}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": fallback_text})

    except Exception as e:
        st.error(f"SYSTEM FAILURE: {e}")
