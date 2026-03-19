import streamlit as st

def apply_styles():
    st.markdown(f"""
    <style>
        /* Общий фон и контейнер */
        .stApp {{
            background-color: #0E1117;
        }}
        
        /* Стилизация карточек */
        div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {{
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 10px;
            padding: 15px;
        }}

        /* Кастомный прогресс-бар */
        .stProgress > div > div > div > div {{
            background-color: #4CAF50;
            border-radius: 5px;
        }}

        /* Моноширинный шрифт для контейнеров */
        .docker-status {{
            font-family: 'JetBrains Mono', 'Roboto Mono', monospace;
            background: #0d1117;
            padding: 4px 8px;
            border-radius: 4px;
            border: 1px solid #30363d;
        }}
        
        /* Убираем лишние отступы сверху */
        .block-container {{
            padding-top: 2rem;
        }}
    </style>
    """, unsafe_allow_html=True)