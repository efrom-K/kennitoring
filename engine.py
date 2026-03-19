import psutil
import docker
import datetime

class MonitorEngine:
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
        except:
            self.docker_client = None

    def get_system_metrics(self):
        # CPU & Temp
        cpu = psutil.cpu_percent()
        
        # Температура (Coretemp для Intel NUC)
        temps = psutil.sensors_temperatures()
        core_temp = 0
        if 'coretemp' in temps:
            core_temp = temps['coretemp'][0].current
        elif 'acpitz' in temps:
            core_temp = temps['acpitz'][0].current
        
        # RAM (Детально)
        vm = psutil.virtual_memory()
        ram_percent = vm.percent
        ram_used = vm.used / (1024**3)
        ram_total = vm.total / (1024**3)
        
        # Uptime & Disks
        uptime = int((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds() // 3600)
        disks = {p.device: psutil.disk_usage(p.mountpoint) 
                 for p in psutil.disk_partitions() 
                 if 'loop' not in p.device and 'snap' not in p.device}
                
        # Network
        net = {nic: stats for nic, stats in psutil.net_io_counters(pernic=True).items()
               if not nic.startswith(('veth', 'br-', 'docker', 'lo'))}
                
        return {
            "cpu": cpu, "temp": core_temp,
            "ram": ram_percent, "ram_used": ram_used, "ram_total": ram_total,
            "uptime": uptime, "disks": disks, "net": net
        }

    def get_containers(self):
        if not self.docker_client: return []
        return sorted(self.docker_client.containers.list(), key=lambda c: c.name)