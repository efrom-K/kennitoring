import streamlit as st
import config

def apply_styles():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');
        * {{ font-family: 'JetBrains Mono', monospace !important; }}
        .stApp {{ background-color: {config.BG_COLOR}; color: {config.TEXT_COLOR}; }}
        
        /* Сетка контейнеров */
        .docker-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
        .docker-status {{ 
            border: 1px solid {config.BORDER_COLOR}; 
            padding: 5px 10px; 
            font-size: 0.8rem; 
            background: #0D1117;
        }}
        
        /* htop-style progress bar для RAM */
        .stCaption {{ font-size: 0.75rem; color: #888; }}
        
        /* Убираем лишнее */
        header {{ visibility: hidden; }}
        .block-container {{ padding-top: 1rem; }}
        
        /* Метрики контрастнее */
        [data-testid="stMetricValue"] {{ font-size: 1.8rem !important; color: {config.TEXT_COLOR}; }}
    </style>
    """, unsafe_allow_html=True)