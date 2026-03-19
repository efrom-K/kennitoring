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
        cpu = psutil.cpu_percent()
        
        # Температура
        temps = psutil.sensors_temperatures()
        core_temp = 0
        if 'coretemp' in temps: core_temp = temps['coretemp'][0].current
        elif 'acpitz' in temps: core_temp = temps['acpitz'][0].current
        
        # RAM
        vm = psutil.virtual_memory()
        
        # Uptime & Disks
        uptime = int((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds() // 3600)
        disks = {p.device: psutil.disk_usage(p.mountpoint) for p in psutil.disk_partitions() if 'loop' not in p.device}
                
        # Network (Добавили try/except, чтобы интерфейсы не пропадали при ошибке чтения)
        net = {}
        try:
            for nic, stats in psutil.net_io_counters(pernic=True).items():
                if not nic.startswith(('veth', 'br-', 'docker', 'lo')):
                    net[nic] = stats
        except: pass
                
        return {
            "cpu": cpu, "temp": core_temp,
            "ram": vm.percent, "ram_used": vm.used/(1024**3), "ram_total": vm.total/(1024**3),
            "uptime": uptime, "disks": disks, "net": net
        }

    def get_container_details(self):
        """Возвращает детальную инфу по каждому контейнеру"""
        if not self.docker_client: return []
        containers_data = []
        for c in self.docker_client.containers.list():
            try:
                # Получаем статистику (stream=False чтобы не вешать поток)
                stats = c.stats(stream=False)
                
                # Считаем CPU %
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                cpu_usage = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
                
                # Считаем RAM (в MB)
                ram_usage = stats['memory_stats'].get('usage', 0) / (1024**2)
                
                # Порты
                ports = c.attrs['NetworkSettings']['Ports']
                port_list = []
                for p in ports:
                    if ports[p]: port_list.append(ports[p][0]['HostPort'])
                port_str = f":{','.join(port_list)}" if port_list else ""

                containers_data.append({
                    "name": c.name,
                    "status": c.status,
                    "cpu": f"{cpu_usage:.1f}%",
                    "ram": f"{int(ram_usage)}M",
                    "port": port_str
                })
            except: continue
        return sorted(containers_data, key=lambda x: x['name'])