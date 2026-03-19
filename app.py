import streamlit as st
import pandas as pd
import time
from collections import deque
from engine import MonitorEngine
import styles
import config

st.set_page_config(page_title="Kennitoring", layout="wide", initial_sidebar_state="collapsed")
styles.apply_styles()

# Sidebar & State
with st.sidebar:
    st.title("SETTINGS")
    live_update = st.checkbox('Live Update', value=True)
    if st.button("Reset History"):
        st.session_state.history = {'cpu': deque([0]*30, maxlen=30), 'ram': deque([0]*30, maxlen=30)}

if 'engine' not in st.session_state:
    st.session_state.engine = MonitorEngine()
    st.session_state.history = {'cpu': deque([0]*30, maxlen=30), 'ram': deque([0]*30, maxlen=30)}

# Data collection
m = st.session_state.engine.get_system_metrics()
st.session_state.history['cpu'].append(m['cpu'])
st.session_state.history['ram'].append(m['ram'])

# Header
st.title("KENNITORING NODE")
st.caption(f"HW: INTEL NUC6 J3455 | UPTIME: {m['uptime']}h | LIVE: {'ON' if live_update else 'OFF'}")
st.divider()

col1, col2 = st.columns(2)

def draw_perf_chart(data, title, y_label):
    """Рисует график с фиксированной осью 0-100 как в htop"""
    df = pd.DataFrame({y_label: list(data)}).reset_index()
    st.vega_lite_chart(df, {
        'mark': {'type': 'area', 'color': '#1f77b4', 'fillOpacity': 0.3, 'line': {'color': '#1f77b4'}},
        'encoding': {
            'x': {'field': 'index', 'type': 'quantitative', 'axis': None},
            'y': {'field': y_label, 'type': 'quantitative', 'scale': {'domain': [0, 100]}, 'title': title}
        },
        'config': {'background': 'transparent', 'view': {'stroke': 'transparent'}},
        'height': 150
    }, use_container_width=True)

with col1:
    st.subheader("Performance")
    
    # CPU Section
    c_m1, c_m2 = st.columns([1, 3])
    c_m1.metric("CPU", f"{m['cpu']}%")
    with c_m2: draw_perf_chart(st.session_state.history['cpu'], "CPU %", "Load")
    
    # RAM Section
    r_m1, r_m2 = st.columns([1, 3])
    r_m1.metric("RAM", f"{m['ram']}%")
    with r_m2: draw_perf_chart(st.session_state.history['ram'], "RAM %", "Usage")
    st.caption(f"MEM [ {'|'*int(m['ram']/2)}{'.'*(50-int(m['ram']/2))} ] {m['ram_used']:.2f}G / {m['ram_total']:.2f}G")

    st.write("**Network I/O**")
    net_df = pd.DataFrame([{"NIC": n, "TX": f"{s.bytes_sent/1024**2:.1f}M", "RX": f"{s.bytes_recv/1024**2:.1f}M"} for n, s in m['net'].items()])
    st.dataframe(net_df, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Infrastructure")
    for dev, u in m['disks'].items():
        st.write(f"Disk: `{dev}`")
        st.progress(u.percent / 100)
        st.caption(f"{u.percent}% | {u.used//1024**3}G / {u.total//1024**3}G")

    st.divider()
    containers = st.session_state.engine.get_containers()
    st.write(f"**Containers ({len(containers)})**")
    
    grid_html = '<div class="docker-grid">'
    for c in containers:
        status_style = f"color:{config.ACCENT_COLOR}" if c.status == "running" else "color:#666"
        grid_html += f'<div class="docker-status">{c.name[:18]} | <span style="{status_style}">{c.status}</span></div>'
    st.markdown(grid_html + '</div>', unsafe_allow_html=True)

if live_update:
    time.sleep(config.UPDATE_INTERVAL)
    st.rerun()