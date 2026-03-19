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
    st.session_state.history = {
        'cpu': deque([0]*30, maxlen=30),
        'ram': deque([0]*30, maxlen=30)
    }

# Метрики
m = st.session_state.engine.get_system_metrics()
st.session_state.history['cpu'].append(m['cpu'])
st.session_state.history['ram'].append(m['ram'])

# Header
st.title("KENNITORING NODE")
st.caption(f"UPTIME: {m['uptime']}H | TEMP: {int(m['temp'])}°C | STATS: ACTIVE")
st.divider()

col_l, col_r = st.columns([1.2, 1])

def draw_chart(data, title, color="#FFFFFF"):
    df = pd.DataFrame(list(data), columns=['val']).reset_index()
    st.vega_lite_chart(df, {
        'mark': {'type': 'area', 'color': color, 'fillOpacity': 0.1, 'line': True},
        'encoding': {
            'x': {'field': 'index', 'type': 'quantitative', 'axis': None, 'scale': {'domain': [0, 29]}},
            'y': {'field': 'val', 'type': 'quantitative', 'scale': {'domain': [0, 100]}, 'title': title, 'axis': {'grid': False}}
        },
        'config': {'background': 'transparent', 'view': {'stroke': 'transparent'}},
        'height': 150
    }, use_container_width=True)

with col_l:
    st.subheader("Performance")
    # CPU
    c1, c2 = st.columns([1, 4])
    c1.metric("CPU", f"{m['cpu']}%")
    with c2: draw_chart(st.session_state.history['cpu'], "CPU %")
    
    # RAM
    r1, r2 = st.columns([1, 4])
    r1.metric("RAM", f"{m['ram']}%")
    with r2: draw_chart(st.session_state.history['ram'], "RAM %", color=config.ACCENT_COLOR)
    
    # htop MEM bar
    bar_len = 30
    filled = int((m['ram'] / 100) * bar_len)
    st.caption(f"MEM [ {'|'*filled}{'.'*(bar_len-filled)} ] {m['ram_used']:.2f}G / {m['ram_total']:.2f}G")

    st.write("**Network Activity**")
    if m['net']:
        net_df = pd.DataFrame([{"NIC": n, "TX": f"{s.bytes_sent/1024**2:.1f}M", "RX": f"{s.bytes_recv/1024**2:.1f}M"} for n, s in m['net'].items()])
        st.dataframe(net_df, use_container_width=True, hide_index=True)
    else:
        st.error("Network interfaces not found. Check permissions.")

with col_r:
    st.subheader("Infrastructure")
    for dev, usage in m['disks'].items():
        st.caption(f"Disk: {dev}")
        st.progress(usage.percent / 100)
    
    st.divider()
    
    # КОНТЕЙНЕРЫ С ПОТРЕБЛЕНИЕМ И ПОРТАМИ
    c_list = st.session_state.engine.get_container_details()
    st.write(f"**Containers ({len(c_list)})**")
    
    html = '<div class="docker-grid">'
    for c in c_list:
        status_color = config.ACCENT_COLOR if c['status'] == 'running' else "#555"
        html += f'''
        <div class="docker-row">
            <div class="c-name">{c['name']} <span class="c-port">{c['port']}</span></div>
            <div class="c-stats">
                <span style="color:{status_color}">●</span> {c['cpu']} | {c['ram']}
            </div>
        </div>
        '''
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# Сайдбар
with st.sidebar:
    live_update = st.checkbox('Live Update', value=True)
    if st.button("Reset Stats"):
        st.session_state.history = {'cpu': deque([0]*30, maxlen=30), 'ram': deque([0]*30, maxlen=30)}
        st.rerun()

if live_update:
    time.sleep(config.UPDATE_INTERVAL)
    st.rerun()