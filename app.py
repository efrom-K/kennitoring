import streamlit as st
import pandas as pd
import time
from collections import deque
from engine import MonitorEngine
import styles
import config

# Настройка страницы
st.set_page_config(page_title="Kennitoring", layout="wide", initial_sidebar_state="collapsed")
styles.apply_styles()

if 'engine' not in st.session_state:
    st.session_state.engine = MonitorEngine()
    # Заполняем нулями, чтобы график сразу был "полным" на 30 точек
    st.session_state.history = {
        'cpu': deque([0]*config.HISTORY_LIMIT, maxlen=config.HISTORY_LIMIT),
        'ram': deque([0]*config.HISTORY_LIMIT, maxlen=config.HISTORY_LIMIT)
    }

# Собираем данные
m = st.session_state.engine.get_system_metrics()
st.session_state.history['cpu'].append(m['cpu'])
st.session_state.history['ram'].append(m['ram'])

# Header
st.title("KENNITORING NODE")
st.caption(f"HW: INTEL NUC6 J3455 | UPTIME: {m['uptime']}H | TEMP: {int(m['temp'])}°C")
st.divider()

col_l, col_r = st.columns(2)

def draw_fixed_chart(data, title, color="#1f77b4"):
    """График с фиксированным окном, который течет влево"""
    # Создаем DF с фиксированными индексами 0-29
    df = pd.DataFrame(list(data), columns=['val']).reset_index()
    
    st.vega_lite_chart(df, {
        'mark': {'type': 'area', 'color': color, 'fillOpacity': 0.1, 'line': {'color': color}},
        'encoding': {
            'x': {
                'field': 'index', 
                'type': 'quantitative', 
                'axis': None, 
                # Это заставляет график не сжиматься, а держать масштаб
                'scale': {'domain': [0, config.HISTORY_LIMIT - 1]} 
            },
            'y': {
                'field': 'val', 
                'type': 'quantitative', 
                'scale': {'domain': [0, 100]}, 
                'title': title,
                'axis': {'grid': False, 'tickCount': 5}
            }
        },
        'config': {'background': 'transparent', 'view': {'stroke': 'transparent'}},
        'height': 150
    }, use_container_width=True)

with col_l:
    st.subheader("Performance")
    
    # CPU
    c1, c2 = st.columns([1, 4])
    c1.metric("CPU", f"{m['cpu']}%")
    with c2: draw_fixed_chart(st.session_state.history['cpu'], "Load %", color="#FFFFFF")
    
    # RAM
    r1, r2 = st.columns([1, 4])
    r1.metric("RAM", f"{m['ram']}%")
    with r2: draw_fixed_chart(st.session_state.history['ram'], "Usage %", color=config.ACCENT_COLOR)
    
    # htop MEM bar (fix)
    bar_len = 25
    filled = int((m['ram'] / 100) * bar_len)
    bar = "|" * filled + "." * (bar_len - filled)
    st.caption(f"MEM [ {bar} ] {m['ram_used']:.2f}G / {m['ram_total']:.2f}G")

with col_r:
    st.subheader("Infrastructure")
    for dev, usage in m['disks'].items():
        st.write(f"Disk: `{dev}`")
        st.progress(usage.percent / 100)
        st.caption(f"{usage.percent}% | {usage.used//1024**3}G / {usage.total//1024**3}G")

    st.divider()
    
    # ИСПРАВЛЕННЫЙ ВЫВОД КОНТЕЙНЕРОВ
    containers = st.session_state.engine.get_containers()
    st.write(f"**Containers ({len(containers)})**")
    
    grid_html = '<div class="docker-grid">'
    for c in containers:
        c_color = config.ACCENT_COLOR if c.status == "running" else "#666"
        # Собираем строку HTML
        grid_html += f'<div class="docker-status">{c.name[:18]} | <span style="color:{c_color}">{c.status}</span></div>'
    grid_html += '</div>'
    
    # ВАЖНО: используем markdown с флагом для HTML
    st.markdown(grid_html, unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.title("SETTINGS")
    live_update = st.checkbox('Live Update', value=True)
    if st.button("Reset Stats"):
        st.rerun()

if live_update:
    time.sleep(config.UPDATE_INTERVAL)
    st.rerun()