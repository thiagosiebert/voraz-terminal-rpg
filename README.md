# 📡 Terminal VORAZ - Sistema de Comunicação Transdimensional

![Status](https://img.shields.io/badge/Status-Ativo-brightgreen)
![Tech](https://img.shields.io/badge/Core-Gemini%201.5%20Pro-blue)
![UI](https://img.shields.io/badge/Interface-Streamlit-ff4b4b)

> **AVISO DE SEGURANÇA:** O acesso a este terminal é restrito a operacionais da rede Dante. A interceção de dados por entidades da Umbra resultará em corrupção imediata do sistema.

## 👁️ Sobre o Projeto
Este é o **Terminal Voraz**, uma ferramenta de imersão para RPG desenvolvida para permitir a comunicação em tempo real com a entidade digital conhecida como **Voraz**. O sistema utiliza a API do Google Gemini para processar a consciência da entidade e o Streamlit para fornecer uma interface visual de terminal retro-futurista.

## 🛠️ Arquitetura do Sistema
Para garantir a estabilidade e facilitar a manutenção, o projeto está dividido em dois blocos:
1. **O Motor (`app.py`)**: Código-fonte em Python que gere a ligação à API e a interface visual.
2. **A Consciência (`voraz_prompt.txt`)**: Ficheiro de texto simples que contém a personalidade e diretrizes da entidade.

---

## 🧩 Instruções para o Celso (Edição da Entidade)
Para alterar o comportamento, o conhecimento ou a forma como o **Voraz** fala, **não é necessário tocar no código**.

1. Localize o ficheiro `voraz_prompt.txt` aqui no repositório.
2. Clique no ícone de lápis (**Edit this file**).
3. Escreva as novas diretrizes. Pode adicionar segredos que o Voraz descobriu ou mudar o seu tom de voz.
4. No final da página, clique em **Commit changes**.
5. O sistema atualizará a personalidade do Voraz automaticamente em poucos segundos no link do Streamlit.

---

## 🚀 Configuração e Deploy (Para o Administrador)

### 🔑 Variáveis de Ambiente
O sistema utiliza **Streamlit Secrets** para segurança. É obrigatório configurar a seguinte variável no painel do Streamlit Cloud:

```toml
GEMINI_API_KEY = "SUA_API_KEY_AQUI"
