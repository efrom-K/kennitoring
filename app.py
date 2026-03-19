import streamlit as st
import pandas as pd
import time
import datetime
from collections import deque
from engine import MonitorEngine
import styles
import config

st.set_page_config(page_title="Kennitoring", layout="wide", initial_sidebar_state="collapsed")
styles.apply_styles()

# Инициализация
if 'engine' not in st.session_state:
    st.session_state.engine = MonitorEngine()
    # Храним историю как список словарей с таймстемпом
    st.session_state.history = {
        'cpu': deque(maxlen=config.HISTORY_LIMIT),
        'ram': deque(maxlen=config.HISTORY_LIMIT)
    }

# Настройки в сайдбаре
with st.sidebar:
    st.title("SETTINGS")
    live_update = st.checkbox('Enable Live Update', value=True)
    if st.button("Reset Stats"):
        st.session_state.history['cpu'].clear()
        st.session_state.history['ram'].clear()
        st.rerun()

# Сбор данных
m = st.session_state.engine.get_system_metrics()
now = datetime.datetime.now()

# Добавляем данные в историю (Timestamp решает проблему лагов)
st.session_state.history['cpu'].append({"time": now, "val": m['cpu']})
st.session_state.history['ram'].append({"time": now, "val": m['ram']})

# Заголовок
st.title("KENNITORING NODE")
st.caption(f"HW: INTEL NUC6 J3455 | UPTIME: {m['uptime']}H | STATUS: ONLINE")
st.divider()

col_left, col_right = st.columns(2)

def draw_chart(data, color="#1f77b4"):
    """Отрисовка графика с привязкой ко времени"""
    df = pd.DataFrame(list(data))
    if df.empty: return
    
    st.vega_lite_chart(df, {
        'mark': {'type': 'area', 'color': color, 'fillOpacity': 0.15, 'line': True},
        'encoding': {
            'x': {'field': 'time', 'type': 'temporal', 'axis': None},
            'y': {'field': 'val', 'type': 'quantitative', 'scale': {'domain': [0, 100]}, 'axis': {'grid': False}}
        },
        'config': {'background': 'transparent', 'view': {'stroke': 'transparent'}},
        'height': 140
    }, use_container_width=True)

with col_left:
    st.subheader("Performance")
    
    # CPU & Temp
    c1, c2, c3 = st.columns([1, 1, 3])
    c1.metric("CPU", f"{m['cpu']}%")
    t_color = "normal" if m['temp'] < 65 else "inverse"
    c2.metric("TEMP", f"{int(m['temp'])}°C", delta_color=t_color)
    with c3: draw_chart(st.session_state.history['cpu'], color="#FFFFFF")
    
    st.divider()
    
    # RAM
    r1, r2, r3 = st.columns([1, 1, 3])
    r1.metric("RAM", f"{m['ram']}%")
    r2.write("") # placeholder
    with r3: draw_chart(st.session_state.history['ram'], color=config.ACCENT_COLOR)
    
    # RAM Bar в стиле htop
    bar_len = 30
    filled = int((m['ram'] / 100) * bar_len)
    bar = "|" * filled + "." * (bar_len - filled)
    st.caption(f"MEM [ {bar} ] {m['ram_used']:.2f}G / {m['ram_total']:.2f}G")

    st.write("**Network Activity**")
    net_data = [{"NIC": n, "TX": f"{s.bytes_sent/1024**2:.1f}MB", "RX": f"{s.bytes_recv/1024**2:.1f}MB"} 
                for n, s in m['net'].items()]
    st.dataframe(pd.DataFrame(net_data), use_container_width=True, hide_index=True)

with col_right:
    st.subheader("Infrastructure")
    for dev, usage in m['disks'].items():
        st.write(f"Disk: `{dev}`")
        st.progress(usage.percent / 100)
        st.caption(f"{usage.percent}% | {usage.used//1024**3}GB / {usage.total//1024**3}GB")

    st.divider()
    
    containers = st.session_state.engine.get_containers()
    st.write(f"**Containers ({len(containers)})**")
    
    grid_html = '<div class="docker-grid">'
    for c in containers:
        c_color = config.ACCENT_COLOR if c.status == "running" else "#666"
        grid_html += f'''
            <div class="docker-status">
                {c.name[:18]} | <span style="color:{c_color}">{c.status}</span>
            </div>
        '''
    st.markdown(grid_html + '</div>', unsafe_allow_html=True)

# Автообновление
if live_update:
    time.sleep(config.UPDATE_INTERVAL)
    st.rerun()