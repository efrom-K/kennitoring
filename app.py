import streamlit as st
import psutil
import pandas as pd
import datetime

st.set_page_config(page_title="NUC Monitor", layout="wide")

# Уменьшаем отступы сверху, чтобы интерфейс был плотнее
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def get_metrics():
    # Замер скорости диска (интервальный)
    d_io1 = psutil.disk_io_counters()
    # Замер скорости сети
    n_io1 = psutil.net_io_counters(pernic=True)
    
    st.cache_data.clear() # Сброс кеша для обновления
    
    return {
        "cpu_pct": psutil.cpu_percent(),
        "cpu_cores": psutil.cpu_percent(percpu=True),
        "ram": psutil.virtual_memory(),
        "disk_parts": [psutil.disk_usage(p.mountpoint) for p in psutil.disk_partitions() if 'loop' not in p.device],
        "disk_names": [p.device for p in psutil.disk_partitions() if 'loop' not in p.device],
        "net": psutil.net_io_counters(pernic=True),
        "temps": psutil.sensors_temperatures()
    }

metrics = get_metrics()

# Заголовок с системным временем
st.caption(f"System Time: {datetime.datetime.now().strftime('%H:%M:%S')}")

# Основная сетка 2 колонки
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🚀 Система")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**CPU Load**")
        st.line_chart(metrics["cpu_cores"], height=150, use_container_width=True)
    with c2:
        st.write("**RAM Load**")
        # Имитируем график ОЗУ (в реальном приложении нужно копить историю в session_state)
        st.bar_chart([metrics["ram"].percent], height=150, use_container_width=True)

    st.write("**🌐 Сетевая активность (KB/s)**")
    # Выводим сетки в столбик
    for nic, stats in metrics["net"].items():
        if stats.bytes_sent > 0 or stats.bytes_recv > 0:
            st.text(f"{nic:10} ↑ {stats.bytes_sent//1024:6} | ↓ {stats.bytes_recv//1024:6}")

    st.write("**🌡️ Температуры**")
    if metrics["temps"]:
        for name, entries in metrics["temps"].items():
            for entry in entries:
                st.write(f"{name} {entry.label}: **{entry.current}°C**")
    else:
        st.info("Датчики не найдены (WSL/Docker limit)")

with col_right:
    st.subheader("💾 Дисковая подсистема")
    
    # Скорость и загрузка дисков
    for i, name in enumerate(metrics["disk_names"]):
        d_stat = metrics["disk_parts"][i]
        col_d1, col_d2 = st.columns([2, 1])
        with col_d1:
            st.write(f"**{name}**")
            st.progress(d_stat.percent / 100)
        with col_d2:
            st.write(f"{d_stat.percent}%")
            st.caption(f"{d_stat.used // 1024**3}G / {d_stat.total // 1024**3}G")
    
    st.divider()
    st.write("**🐳 Контейнеры (Docker)**")
    # Краткий список для компактности
    import docker
    try:
        client = docker.from_env()
        for c in client.containers.list():
            st.code(f"{c.name[:20]:20} [{c.status}]", language="bash")
    except:
        st.error("Docker сокет недоступен")

# Автообновление (экспериментально для Streamlit)
if st.checkbox('Auto-refresh (5s)'):
    import time
    time.sleep(5)
    st.rerun()