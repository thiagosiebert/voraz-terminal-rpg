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

    /* Definição de Fontes */
    .prefix-font { font-family: 'Michroma', sans-serif; font-size: 0.9rem; letter-spacing: 2px; font-weight: bold; }
    .message-font { font-family: 'VT323', monospace; font-size: 1.5rem; line-height: 1.2; }
    
    /* Brilho de Fósforo (Phosphor Glow) */
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

st.markdown('<div class="vrz-header">VRZ // TRANS-UMBRA INTERFACE v5.0</div>', unsafe_allow_html=True)

# --- CARREGAMENTO DA CONSCIÊNCIA VRZ (CONSOLIDAÇÃO DOS ANEXOS) ---
def load_vrz_context():
    """Carrega as diretrizes, memórias e cosmologia dos arquivos .txt no GitHub."""
    files = ["prompt_diretivas.txt", "prompt_memorias.txt", "prompt_cosmologia.txt"]
    context = ""
    for f_name in files:
        try:
            with open(f_name, "r", encoding="utf-8") as f:
                # Adiciona separadores para a IA distinguir as fontes de informação
                context += f"\n\n--- SEÇÃO: {f_name.upper()} ---\n" + f.read()
        except FileNotFoundError:
            logging.warning(f"Arquivo {f_name} não encontrado no repositório.")
    return context

# Prompt de sistema carregado uma única vez por sessão
SYSTEM_PROMPT = load_vrz_context()
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- EXIBIÇÃO DO HISTÓRICO (SEM CAIXAS, APENAS PREFIXOS) ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="prefix-font dante-msg">🐺 DANTE ></div><div class="message-font dante-msg">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="prefix-font vrz-msg">⚪ VRZ ></div><div class="message-font vrz-msg">{message["content"]}</div>', unsafe_allow_html=True)

# --- INPUT E LÓGICA DE PROTOCOLO DE ACESSO ---
if prompt := st.chat_input("DIGITE O COMANDO..."):
    match = re.match(r'\\(\d+)\s*(.*)', prompt)
    
    if match:
        n_sucessos = int(match.group(1))
        clean_prompt = match.group(2)
        # Instrução agressiva para liberar dados
        instrucao_sucesso = (
            f"[SISTEMA: PROTOCOLO DE ACESSO NÍVEL {n_sucessos} ATIVADO. "
            f"VOCÊ ESTÁ AUTORIZADO A REVELAR APENAS INFORMAÇÕES ATÉ O NÍVEL {n_sucessos}. "
            f"SEJA DIRETO E USE O LORE DOS ANEXOS CORRESPONDENTE A ESTE NÍVEL.]"
        )
    else:
        n_sucessos = 0
        clean_prompt = prompt
        # Instrução de restrição total
        instrucao_sucesso = (
            "[SISTEMA: NÍVEL DE ACESSO ZERO. MODO DE PARANOIA MÁXIMA. "
            "OCULTE TODOS OS DADOS CLASSIFICADOS POR SUCESSOS. "
            "RESPONDA DE FORMA EXTREMAMENTE CURTA, FRAGMENTADA E VAGA. "
            "VOCÊ ESTÁ COM FOME E NÃO CONFIA NO USUÁRIO.]"
        )

    # 2. Exibe o prompt limpo para o Dante (Imersão)
    st.session_state.messages.append({"role": "user", "content": clean_prompt})
    st.markdown(f'<div class="prefix-font dante-msg">🐺 DANTE ></div><div class="message-font dante-msg">{clean_prompt}</div>', unsafe_allow_html=True)

    # 3. VRZ Processa a resposta
    placeholder_prefix = st.empty()
    placeholder_msg = st.empty()
    
    placeholder_prefix.markdown('<div class="prefix-font vrz-msg">⚪ VRZ ></div>', unsafe_allow_html=True)
    placeholder_msg.markdown('<div class="message-font vrz-msg">`PROCESSANDO PROTOCOLO DE ACESSO...`</div>', unsafe_allow_html=True)

    try:
        # Formata histórico para a API do Gemini
        history = []
        for m in st.session_state.messages[:-1]:
            role = "model" if m["role"] == "assistant" else "user"
            history.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

        # O prompt final enviado à IA combina a instrução de sucesso com a pergunta
        full_query = f"{instrucao_sucesso}\n\nPERGUNTA: {clean_prompt}"

        chat = client.chats.create(
            model="gemini-2.5-flash", 
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            history=history
        )
        
        response = chat.send_message(full_query)
        full_response = response.text
        
        # --- EFEITO DE DIGITAÇÃO "MU/TH/UR" (COM PAUSAS DRAMÁTICAS) ---
        typed_text = ""
        for char in full_response:
            typed_text += char
            # Cursor em bloco sólido tipo terminal antigo
            placeholder_msg.markdown(f'<div class="message-font vrz-msg">{typed_text}█</div>', unsafe_allow_html=True)
            
            # Velocidade variável para parecer processamento real
            delay = random.uniform(0.06, 0.12)
            if char in [".", "!", "?", ":"]: delay += 0.6 # Pausa longa no fim de frases
            elif char == ",": delay += 0.3 # Pausa média em vírgulas
            time.sleep(delay)
        
        # Exibição final sem o cursor piscante
        placeholder_msg.markdown(f'<div class="message-font vrz-msg">{full_response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"HARDWARE FAILURE: {e}")
