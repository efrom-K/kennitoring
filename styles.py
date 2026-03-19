import streamlit as st
import config

def apply_styles():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        * {{ font-family: 'JetBrains Mono', monospace !important; }}
        .stApp {{ background-color: {config.BG_COLOR}; color: {config.TEXT_COLOR}; }}
        
        /* Сетка контейнеров */
        .docker-grid {{ 
            display: grid; grid-template-columns: 1fr; gap: 5px; 
            margin-top: 10px;
        }}
        
        .docker-row {{ 
            display: flex; justify-content: space-between; align-items: center;
            border: 1px solid {config.BORDER_COLOR}; 
            padding: 4px 12px; font-size: 0.85rem; background: #0D1117;
        }}
        
        .c-name {{ font-weight: bold; color: #888; flex-grow: 1; }}
        .c-stats {{ color: {config.ACCENT_COLOR}; font-size: 0.75rem; margin-left: 15px; white-space: nowrap; }}
        .c-port {{ color: #555; font-size: 0.75rem; margin-left: 10px; }}

        header, footer {{ visibility: hidden; }}
        .block-container {{ padding-top: 1rem; }}
    </style>
    """, unsafe_allow_html=True)