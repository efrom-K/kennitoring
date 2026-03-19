import streamlit as st
import config

def apply_styles():
    st.markdown(f"""
    <style>
        /* Глобальный шрифт JetBrains Mono */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        * {{
            font-family: 'JetBrains Mono', monospace !important;
            letter-spacing: -0.5px;
        }}

        /* Минималистичный фон */
        .stApp {{
            background-color: {config.BG_COLOR};
            color: {config.TEXT_COLOR};
        }}
        
        /* Карточки без теней, только тонкая граница */
        div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {{
            background-color: {config.CARD_BG};
            border: 1px solid {config.BORDER_COLOR};
            border-radius: 6px;
            padding: 12px;
            box-shadow: none !important;
        }}

        /* Контрастный прогресс-бар (Черный/Зеленый) */
        .stProgress > div > div > div > div {{
            background-color: {config.ACCENT_COLOR};
            border-radius: 3px;
        }}
        .stProgress > div > div {{
            background-color: {config.BG_COLOR};
        }}

        /* Минималистичная таблица */
        .stDataFrame table {{
            border-collapse: collapse;
        }}
        .stDataFrame td, .stDataFrame th {{
            border-bottom: 1px solid {config.BORDER_COLOR};
            text-align: left !important;
            padding: 8px !important;
        }}

        /* Компактный список контейнеров (2 колонки) */
        .docker-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin-top: 10px;
        }}
        .docker-status {{
            background: {config.BG_COLOR};
            padding: 6px 10px;
            border-radius: 4px;
            border: 1px solid {config.BORDER_COLOR};
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        /* Тонкие линии для графиков (делаем их максимально незаметными) */
        [data-testid="stVegaLiteChart"] summary {{
            color: {config.TEXT_COLOR}33 !important; /* Очень прозрачный текст легенды */
        }}
        
        /* Убираем отступы */
        .block-container {{
            padding-top: 2rem;
        }}
    </style>
    """, unsafe_allow_html=True)