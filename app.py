import streamlit as st
import pandas as pd
import time
import datetime
from collections import deque
from engine import MonitorEngine
import styles
import config

# Настройки страницы
st.set_page_config(page_title="Kennitoring Node", layout="wide", initial_sidebar_state="collapsed")
styles.apply_styles()

# Инициализация синглтона движка и истории
if 'engine' not in st.session_state:
    st.session_state.engine = MonitorEngine()
    # Создаем deques для истории графиков (CPU и RAM параллельно)
    st.session_state.history = {
        'cpu': deque([0]*config.HISTORY_LIMIT, maxlen=config.HISTORY_LIMIT),
        'ram': deque([0]*config.HISTORY_LIMIT, maxlen=config.HISTORY_LIMIT)
    }

# Сбор свежих метрик
metrics = st.session_state.engine.get_system_metrics()
# Обновляем историю в st.session_state (храним 30 точек)
st.session_state.history['cpu'].append(metrics['cpu'])
st.session_state.history['ram'].append(metrics['ram'])

# МИНИМАЛИСТИЧНЫЙ HEADER (в одну строку)
col_header, col_meta = st.columns([4, 1])
with col_header:
    # Заголовок без иконок
    st.title("KENNITORING NODE")
    # Мелкие метаданные под заголовком
    st.caption(f"Active | Hardware: Intel NUC6 J3455 | Uptime: {metrics['uptime']} Hours")
with col_meta:
    # Мелкий Live Update в углу
    st.sidebar.checkbox('Live Update (5s)', value=True)

st.divider()

# ОСНОВНОЙ ПЛОТНЫЙ LAYOUT (2 Колонки)
col_left, col_right = st.columns(2)

with col_left:
    # Левая колонка: Только графики (CPU и RAM симметрично)
    st.subheader("Performance Metrics")
    
    # 1. График CPU % (Area chart для визуальной плотности)
    cpu_df = pd.DataFrame({'CPU %': list(st.session_state.history['cpu'])})
    # Area chart смотрится лучше при низкой загрузке (thock sound effect for data)
    st.area_chart(cpu_df, height=180, use_container_width=True)
    
    # 2. График RAM % (Прямо под CPU, такой же высоты)
    ram_df = pd.DataFrame({'RAM %': list(st.session_state.history['ram'])})
    st.area_chart(ram_df, height=180, use_container_width=True)
    
    # Минималистичная сеть (в виде таблицы)
    st.write("**Physical Network I/O (MB)**")
    net_list = []
    for nic, s in metrics['net'].items():
        # Расчет TX/RX в МБ и добавление в список
        net_list.append({
            "NIC": nic, 
            "↑ TX": round(s.bytes_sent/1024**2, 1), 
            "↓ RX": round(s.bytes_recv/1024**2, 1)
        })
    # Hide index для минимализма
    st.dataframe(pd.DataFrame(net_list), use_container_width=True, hide_index=True)

with col_right:
    # Правая колонка: Хранилище и Докер
    st.subheader("System Infrastructure")
    
    # Секция Дисков
    for dev, usage in metrics['disks'].items():
        st.write(f"Device: `{dev}`")
        # Контрастный прогресс-бар (акцентный зелёный)
        st.progress(usage.percent / 100)
        st.caption(f"{usage.percent}% | {usage.used//1024**3}GB Used / {usage.total//1024**3}GB Total")

    st.divider()
    
    # Секция Контейнеров (самая пафосная часть)
    containers = st.session_state.engine.get_containers()
    st.write(f"**🐳 Active Containers ({len(containers)})**")
    
    # Генерируем HTML-сетку в 2 колонки (для styles.py)
    docker_html = '<div class="docker-grid">'
    for c in containers:
        # Убираем цвет точки, оставляем чистый текст и статус (Зелёный/Серый)
        status_color = config.ACCENT_COLOR if c.status == "running" else "#30363D"
        status_text = f"<span style='color:{status_color}'>running</span>" if c.status == "running" else "stopped"
        # truncated name, чтобы не ломать верстку
        docker_html += f"""<div class="docker-status">
            {c.name[:20]:<20} | {status_text}
        </div>"""
    docker_html += '</div>'
    
    # Внедряем HTML через markdown (unsafe_allow_html — это норма для такого дашборда)
    st.markdown(docker_html, unsafe_allow_html=True)

# Скрипт автообновления
if st.sidebar.get("checkbox"): # Если Live Update включен в сайдбаре
    import time
    time.sleep(config.UPDATE_INTERVAL)
    st.rerun()