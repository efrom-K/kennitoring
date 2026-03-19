import psutil
import docker
import datetime
from collections import deque
import config

class MonitorEngine:
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
        except:
            self.docker_client = None

    def get_system_metrics(self):
        # CPU & RAM
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        uptime = int((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds() // 3600)
        
        # Диски (Фильтрация дублей)
        disks = {}
        for p in psutil.disk_partitions():
            if 'loop' not in p.device and p.device not in disks:
                try:
                    disks[p.device] = psutil.disk_usage(p.mountpoint)
                except: continue
                
        # Сеть
        net = {}
        for nic, stats in psutil.net_io_counters(pernic=True).items():
            if not nic.startswith(config.IGNORE_NET_PREFIXES) and (stats.bytes_sent > 0 or stats.bytes_recv > 0):
                net[nic] = stats
                
        return {
            "cpu": cpu, "ram": ram, "uptime": uptime,
            "disks": disks, "net": net
        }

    def get_containers(self):
        if not self.docker_client:
            return []
        return self.docker_client.containers.list()