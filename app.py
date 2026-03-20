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
    # Увеличиваем до 60 для минутной истории при 1 fps
    st.session_state.history = {
        'cpu': deque([0]*60, maxlen=60),
        'ram': deque([0]*60, maxlen=60)
    }

m = st.session_state.engine.get_system_metrics()
st.session_state.history['cpu'].append(m['cpu'])
st.session_state.history['ram'].append(m['ram'])

# Header
st.title("KENNITORING NODE")
st.caption(f"HW: INTEL NUC6 J3455 | UPTIME: {m['uptime']}H | TEMP: {int(m['temp'])}°C")
st.divider()

col_l, col_r = st.columns([1.2, 1])

def draw_chart(data, title, color="#FFFFFF"):
    df = pd.DataFrame(list(data), columns=['val']).reset_index()
    # Изменил domain на 59, чтобы график не дергался
    st.vega_lite_chart(df, {
        'mark': {'type': 'area', 'color': color, 'fillOpacity': 0.1, 'line': True},
        'encoding': {
            'x': {'field': 'index', 'type': 'quantitative', 'axis': None, 'scale': {'domain': [0, 59]}},
            'y': {'field': 'val', 'type': 'quantitative', 'scale': {'domain': [0, 100]}, 'title': title, 'axis': {'grid': False}}
        },
        'config': {'background': 'transparent', 'view': {'stroke': 'transparent'}},
        'height': 150
    }, width='stretch')

with col_l:
    st.subheader("Performance")
    c1, c2 = st.columns([1, 4])
    c1.metric("CPU", f"{m['cpu']}%")
    with c2: draw_chart(st.session_state.history['cpu'], "CPU %")
    
    r1, r2 = st.columns([1, 4])
    r1.metric("RAM", f"{m['ram']}%")
    with r2: draw_chart(st.session_state.history['ram'], "RAM %", color=config.ACCENT_COLOR)
    
    filled = int((m['ram'] / 100) * 30)
    st.caption(f"MEM [ {'|'*filled}{'.'*(30-filled)} ] {m['ram_used']:.2f}G / {m['ram_total']:.2f}G")

    st.write("**Network Activity**")
    if m['net']:
        net_data = [{"NIC": n, "TX": f"{s.bytes_sent/1024**2:.1f}MB", "RX": f"{s.bytes_recv/1024**2:.1f}MB"} for n, s in m['net'].items()]
        st.dataframe(pd.DataFrame(net_data), use_container_width=True, hide_index=True)

with col_r:
    st.subheader("Infrastructure")
    for dev, usage in m['disks'].items():
        st.caption(f"Disk: {dev}")
        st.progress(usage.percent / 100)
    
    st.divider()
    
    c_list = st.session_state.engine.get_container_details()
    st.write(f"**Containers ({len(c_list)})**")
    
    container_html = '<div class="docker-grid">'
    for c in c_list:
        status_clr = config.ACCENT_COLOR if c['status'] == 'running' else "#555"
        p_info = f"<span style='color: #888; font-size: 0.8em;'> {c['port']}</span>" if c['port'] else ""
        
        row = f'''
        <div style="margin-bottom: 8px; padding: 10px; border: 1px solid #333; border-radius: 6px; background: rgba(255,255,255,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span><b>{c["name"]}</b>{p_info}</span>
                <span style="font-family: monospace;"><span style="color:{status_clr}">●</span> {c["cpu"]} | {c["ram"]}</span>
            </div>
        </div>
        '''
        container_html += row
    
    st.markdown(container_html + '</div>', unsafe_allow_html=True)

if st.sidebar.checkbox('Live Update', value=True):
    time.sleep(config.UPDATE_INTERVAL)
    st.rerun()