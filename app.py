import streamlit as st
import pandas as pd
import time
import datetime
from collections import deque
from engine import MonitorEngine
import styles
import config

# 1. Настройки страницы (Должны быть первой командой Streamlit)
st.set_page_config(
    page_title="Kennitoring Node", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. Применяем кастомный дизайн-код (JetBrains Mono, High Contrast)
styles.apply_styles()

# 3. Инициализация боковой панели (Sidebar)
with st.sidebar:
    st.title("Settings")
    # Правильный способ работы с состоянием чекбокса
    live_update = st.checkbox('Live Update (5s)', value=True)
    st.divider()
    if st.button("Clear History"):
        st.session_state.history = {
            'cpu': deque([0]*config.HISTORY_LIMIT, maxlen=config.HISTORY_LIMIT),
            'ram': deque([0]*config.HISTORY_LIMIT, maxlen=config.HISTORY_LIMIT)
        }
        st.rerun()

# 4. Инициализация движка и истории в session_state
if 'engine' not in st.session_state:
    st.session_state.engine = MonitorEngine()
    st.session_state.history = {
        'cpu': deque([0]*config.HISTORY_LIMIT, maxlen=config.HISTORY_LIMIT),
        'ram': deque([0]*config.HISTORY_LIMIT, maxlen=config.HISTORY_LIMIT)
    }

# 5. Сбор метрик через Engine
metrics = st.session_state.engine.get_system_metrics()
st.session_state.history['cpu'].append(metrics['cpu'])
st.session_state.history['ram'].append(metrics['ram'])

# 6. HEADER (Минимализм)
col_header, col_meta = st.columns([4, 1])
with col_header:
    st.title("KENNITORING NODE")
    st.caption(f"STATUS: ACTIVE | HW: INTEL NUC6 J3455 | UPTIME: {metrics['uptime']} HOURS")

st.divider()

# 7. ОСНОВНОЙ ПЛОТНЫЙ LAYOUT
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Performance Metrics")
    
    # График CPU %
    cpu_df = pd.DataFrame({'CPU %': list(st.session_state.history['cpu'])})
    st.area_chart(cpu_df, height=180, use_container_width=True)
    
    # График RAM % (Прямо под CPU)
    ram_df = pd.DataFrame({'RAM %': list(st.session_state.history['ram'])})
    st.area_chart(ram_df, height=180, use_container_width=True)
    
    # Сетевая активность (Физические интерфейсы)
    st.write("**Physical Network I/O (MB)**")
    net_list = []
    for nic, s in metrics['net'].items():
        net_list.append({
            "NIC": nic, 
            "↑ TX": round(s.bytes_sent/1024**2, 1), 
            "↓ RX": round(s.bytes_recv/1024**2, 1)
        })
    st.dataframe(pd.DataFrame(net_list), use_container_width=True, hide_index=True)

with col_right:
    st.subheader("System Infrastructure")
    
    # Хранилище (sda2 и прочее)
    for dev, usage in metrics['disks'].items():
        st.write(f"Device: `{dev}`")
        st.progress(usage.percent / 100)
        st.caption(f"{usage.percent}% | {usage.used//1024**3}GB Used / {usage.total//1024**3}GB Total")

    st.divider()
    
    # Секция Контейнеров (Две колонки через HTML/CSS из styles.py)
    containers = st.session_state.engine.get_containers()
    st.write(f"**Containers ({len(containers)})**")
    
    docker_html = '<div class="docker-grid">'
    for c in containers:
        status_color = config.ACCENT_COLOR if c.status == "running" else "#30363D"
        status_text = f"<span style='color:{status_color}'>running</span>" if c.status == "running" else "stopped"
        docker_html += f"""<div class="docker-status">
            {c.name[:20]:<20} | {status_text}
        </div>"""
    docker_html += '</div>'
    
    st.markdown(docker_html, unsafe_allow_html=True)

# 8. КОРРЕКТНОЕ АВТООБНОВЛЕНИЕ
if live_update:
    time.sleep(config.UPDATE_INTERVAL)
    st.rerun()