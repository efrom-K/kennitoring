import streamlit as st
import pandas as pd
import time
from collections import deque
from engine import MonitorEngine
import styles
import config

st.set_page_config(page_title="Kennitoring", layout="wide", initial_sidebar_state="collapsed")
styles.apply_styles()

if 'engine' not in st.session_state:
    st.session_state.engine = MonitorEngine()

m = st.session_state.engine.get_system_metrics()

# Функция для отрисовки шкалы в стиле htop
def render_bar(label, percent, info="", width=30):
    filled = int((percent / 100) * width)
    bar = f"{'|' * filled}{'.' * (width - filled)}"
    return f"**{label}** `[ {bar} ]` **{percent}%** {info}"

# Header
st.title("KENNITORING NODE")
st.caption(f"HW: INTEL NUC6 J3455 | UPTIME: {m['uptime']}H | TEMP: {int(m['temp'])}°C")
st.divider()

col_l, col_r = st.columns([1, 1])

with col_l:
    st.subheader("System Resources")
    
    # CPU Bar
    st.write(render_bar("CPU", m['cpu']), unsafe_allow_html=True)
    
    # RAM Bar
    ram_info = f"({m['ram_used']:.2f}G / {m['ram_total']:.2f}G)"
    st.write(render_bar("MEM", m['ram'], ram_info), unsafe_allow_html=True)
    
    st.write("**Network I/O**")
    if m['net']:
        net_data = [{"NIC": n, "TX": f"{s.bytes_sent/1024**2:.1f}M", "RX": f"{s.bytes_recv/1024**2:.1f}M"} for n, s in m['net'].items()]
        st.dataframe(pd.DataFrame(net_data), use_container_width=True, hide_index=True)

with col_r:
    st.subheader("Infrastructure")
    for dev, usage in m['disks'].items():
        st.write(render_bar(f"DSK {dev[:4]}", usage.percent), unsafe_allow_html=True)
    
    st.divider()
    
    c_list = st.session_state.engine.get_container_details()
    st.write(f"**Containers ({len(c_list)})**")
    
    # Формируем контейнеры БЕЗ сложных вложений, чтобы не ломался рендеринг
    for c in c_list:
        status_clr = config.ACCENT_COLOR if c['status'] == 'running' else "#555"
        p_info = f" {c['port']}" if c['port'] else ""
        
        # Используем одну строку Markdown с HTML-вставкой только для цвета точки
        container_line = f"<span style='color:{status_clr}'>●</span> **{c['name']}**`{p_info}` | {c['cpu']} | {c['ram']}"
        st.write(container_line, unsafe_allow_html=True)

if st.sidebar.checkbox('Live Update', value=True):
    time.sleep(config.UPDATE_INTERVAL)
    st.rerun()