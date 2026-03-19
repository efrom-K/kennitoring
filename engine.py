import psutil
import docker
import datetime
import config

class MonitorEngine:
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
        except:
            self.docker_client = None

    def get_system_metrics(self):
        # CPU
        cpu = psutil.cpu_percent()
        
        # RAM (Детально как в htop)
        vm = psutil.virtual_memory()
        ram_percent = vm.percent
        ram_used = vm.used / (1024**3)
        ram_total = vm.total / (1024**3)
        
        # Uptime
        uptime = int((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds() // 3600)
        
        # Storage
        disks = {}
        for p in psutil.disk_partitions():
            if 'loop' not in p.device and p.device not in disks:
                try:
                    disks[p.device] = psutil.disk_usage(p.mountpoint)
                except: continue
                
        # Network
        net = {}
        for nic, stats in psutil.net_io_counters(pernic=True).items():
            if not nic.startswith(config.IGNORE_NET_PREFIXES) and (stats.bytes_sent > 0 or stats.bytes_recv > 0):
                net[nic] = stats
                
        return {
            "cpu": cpu, 
            "ram": ram_percent, 
            "ram_used": ram_used, 
            "ram_total": ram_total,
            "uptime": uptime, 
            "disks": disks, 
            "net": net
        }

    def get_containers(self):
        if not self.docker_client: return []
        return sorted(self.docker_client.containers.list(), key=lambda c: c.name)