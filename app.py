import streamlit as st
import psutil
import pandas as pd
import datetime
import docker
from collections import deque

# Настройки страницы
st.set_page_config(page_title="NUC Monitor", layout="wide", initial_sidebar_state="collapsed")

# Стили для компактности
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    code { white-space: pre !important; }
    </style>
    """, unsafe_allow_html=True)

# Инициализация истории (храним 30 последних замеров)
if 'history' not in st.session_state:
    st.session_state.history = {
        'cpu': deque([0]*30, maxlen=30),
        'ram': deque([0]*30, maxlen=30),
        'time': deque([datetime.datetime.now()]*30, maxlen=30)
    }

@st.cache_resource
def get_docker_client():
    try:
        return docker.from_env()
    except:
        return None

def get_clean_metrics():
    # CPU и RAM
    cpu_val = psutil.cpu_percent()
    ram_val = psutil.virtual_memory().percent
    
    st.session_state.history['cpu'].append(cpu_val)
    st.session_state.history['ram'].append(ram_val)
    st.session_state.history['time'].append(datetime.datetime.now())

    # Фильтрация дисков (убираем дубли и loop)
    disks = {}
    for p in psutil.disk_partitions():
        if 'loop' not in p.device and p.device not in disks:
            try:
                disks[p.device] = psutil.disk_usage(p.mountpoint)
            except: continue

    # Фильтрация сети (только физика)
    net = {}
    ignore_prefixes = ('veth', 'br-', 'docker', 'lo', 'sit')
    for nic, stats in psutil.net_io_counters(pernic=True).items():
        if not nic.startswith(ignore_prefixes) and (stats.bytes_sent > 0 or stats.bytes_recv > 0):
            net[nic] = stats

    return cpu_val, ram_val, disks, net

# Сбор данных
cpu_now, ram_now, disks, net = get_clean_metrics()

# Header
cols = st.columns([4, 1])
cols[0].title(f"🏠 NUC6 Node: {psutil.users()[0].name if psutil.users() else 'Server'}")
cols[1].metric("Uptime", f"{int((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds() // 3600)}h")

left, right = st.columns([1, 1])

with left:
    st.subheader("🚀 Performance")
    
    # График CPU
    cpu_df = pd.DataFrame({'CPU %': list(st.session_state.history['cpu'])})
    st.line_chart(cpu_df, height=150)
    
    # Сетевая таблица (чистая)
    st.write("**🌐 Network (MB Overall)**")
    net_data = []
    for nic, s in net.items():
        net_data.append({
            "Interface": nic,
            "Sent": f"{s.bytes_sent / (1024**2):.1f} MB",
            "Recv": f"{s.bytes_recv / (1024**2):.1f} MB"
        })
    st.table(pd.DataFrame(net_data))

with right:
    st.subheader("💾 Storage & Containers")
    
    for dev, usage in disks.items():
        col_name, col_prog, col_val = st.columns([1, 2, 1])
        col_name.caption(dev)
        col_prog.progress(usage.percent / 100)
        col_val.write(f"**{usage.percent}%**")
    
    st.divider()
    
    # Docker секция
    client = get_docker_client()
    if client:
        st.write(f"**🐳 Containers ({len(client.containers.list())})**")
        for c in client.containers.list():
            # Цвет статуса
            status_color = "green" if c.status == "running" else "red"
            st.markdown(f" `{c.name[:18]:<18}` : {status_color}[{c.status}]")
    else:
        st.error("Docker Socket Error")

# Умное обновление через фрагменты (Streamlit 1.33+)
if st.checkbox('Live Update (5s)', value=True):
    import time
    time.sleep(5)
    st.rerun()