import streamlit as st
import pandas as pd
import time
import datetime
from collections import deque
from engine import MonitorEngine
import styles
import config

st.set_page_config(page_title="Kennitoring Node", layout="wide")
styles.apply_styles()

# Синглтон движка и истории
if 'engine' not in st.session_state:
    st.session_state.engine = MonitorEngine()
    st.session_state.history = {
        'cpu': deque([0]*config.HISTORY_LIMIT, maxlen=config.HISTORY_LIMIT),
        'ram': deque([0]*config.HISTORY_LIMIT, maxlen=config.HISTORY_LIMIT)
    }

# Сбор данных
metrics = st.session_state.engine.get_system_metrics()
st.session_state.history['cpu'].append(metrics['cpu'])
st.session_state.history['ram'].append(metrics['ram'])

# HEADER
head_l, head_r = st.columns([4, 1])
with head_l:
    st.title("🛸 Kennitoring Dashboard")
    st.caption(f"Node Status: Active | Hardware: Intel NUC6 J3455")
with head_r:
    st.metric("Uptime", f"{metrics['uptime']} Hours")

st.divider()

# ОСНОВНОЙ ВИД
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Live Performance")
    
    # Графики
    cpu_df = pd.DataFrame({'CPU %': list(st.session_state.history['cpu'])})
    st.line_chart(cpu_df, height=200)
    
    # Сеть
    st.write("**🌐 Physical Network I/O**")
    net_list = []
    for nic, s in metrics['net'].items():
        net_list.append({
            "NIC": nic, 
            "TX (MB)": round(s.bytes_sent/1024**2, 1), 
            "RX (MB)": round(s.bytes_recv/1024**2, 1)
        })
    st.dataframe(pd.DataFrame(net_list), use_container_width=True, hide_index=True)

with col_right:
    st.subheader("💾 Storage & Docker")
    
    # Диски
    for dev, usage in metrics['disks'].items():
        st.write(f"Device: `{dev}`")
        st.progress(usage.percent / 100)
        st.caption(f"Used: {usage.used//1024**3}GB / Total: {usage.total//1024**3}GB ({usage.percent}%)")

    st.divider()
    
    # Контейнеры
    containers = st.session_state.engine.get_containers()
    st.write(f"**🐳 Active Containers ({len(containers)})**")
    for c in containers:
        color = "green" if c.status == "running" else "gray"
        st.markdown(f"""<div class="docker-status">
            <span style="color:{color}">●</span> {c.name[:20]} — <i>{c.status}</i>
        </div>""", unsafe_allow_html=True)

# AUTO-REFRESH
if st.sidebar.checkbox('Enable Live Update', value=True):
    time.sleep(config.UPDATE_INTERVAL)
    st.rerun()