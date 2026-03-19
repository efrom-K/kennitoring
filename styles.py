import streamlit as st
import config

def apply_styles():
    st.markdown(f"""
    <style>
        /* Глобальный шрифт JetBrains Mono */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        * {{ font-family: 'JetBrains Mono', monospace !important; }}

        /* Минималистичный фон */
        .stApp {{ background-color: {config.BG_COLOR}; color: {config.TEXT_COLOR}; }}
        
        /* Сетка контейнеров (2 колонки) */
        .docker-grid {{ 
            display: grid; grid-template-columns: 1fr 1fr; gap: 8px; 
            margin-top: 10px; border: 1px solid {config.BORDER_COLOR}; 
            padding: 10px; border-radius: 4px; background: #0D1117;
        }}
        
        .docker-status {{ 
            border: 1px solid {config.BORDER_COLOR}; 
            padding: 5px 10px; font-size: 0.8rem; background: #0D1117;
        }}
        
        /* Скрываем интерфейс Streamlit */
        header {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        .block-container {{ padding-top: 1rem; }}
        
        /* Читаемые метрики */
        [data-testid="stMetricValue"] {{ font-size: 1.8rem !important; }}
    </style>
    """, unsafe_allow_html=True)