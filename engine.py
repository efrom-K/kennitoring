import psutil
import docker
import datetime
import os

class MonitorEngine:
    def __init__(self):
        if os.environ.get('PROCFS_PATH'):
            psutil.PROCFS_PATH = os.environ.get('PROCFS_PATH')
        try:
            self.docker_client = docker.from_env()
        except:
            self.docker_client = None

    def get_system_metrics(self):
        vm = psutil.virtual_memory()
        temps = psutil.sensors_temperatures()
        
        core_temp = 0
        if 'coretemp' in temps:
            core_temp = temps['coretemp'][0].current
        elif 'acpitz' in temps:
            core_temp = temps['acpitz'][0].current
        
        net = {}
        try:
            for nic, stats in psutil.net_io_counters(pernic=True).items():
                if not nic.startswith(('veth', 'br-', 'docker', 'lo', 'wg')):
                    net[nic] = stats
        except: pass

        return {
            # interval=0.1 дает свежее значение CPU при каждом вызове
            "cpu": psutil.cpu_percent(interval=0.1),
            "temp": core_temp,
            "ram": vm.percent,
            "ram_used": vm.used / (1024**3),
            "ram_total": vm.total / (1024**3),
            "uptime": int((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds() // 3600),
            "disks": {p.mountpoint: psutil.disk_usage(p.mountpoint) 
                      for p in psutil.disk_partitions() 
                      if 'loop' not in p.device and '/snap/' not in p.mountpoint},
            "net": net
        }

    def get_container_details(self):
        if not self.docker_client: return []
        details = []
        cpu_count = psutil.cpu_count() or 1
        
        for c in self.docker_client.containers.list():
            try:
                s = c.stats(stream=False)
                
                cpu_delta = s['cpu_stats']['cpu_usage']['total_usage'] - s['precpu_stats']['cpu_usage']['total_usage']
                sys_delta = s['cpu_stats']['system_cpu_usage'] - s['precpu_stats']['system_cpu_usage']
                
                cpu_pct = (cpu_delta / sys_delta) * cpu_count * 100.0 if sys_delta > 0 else 0.0
                
                ram_usage = s['memory_stats'].get('usage', 0)
                cache = s['memory_stats'].get('stats', {}).get('inactive_file', 0)
                ram_mb = (ram_usage - cache) / (1024**2)

                p_map = c.attrs.get('NetworkSettings', {}).get('Ports', {})
                ports = [p_map[p][0]['HostPort'] for p in p_map if p_map[p]]
                port_str = f":{','.join(ports)}" if ports else ""

                details.append({
                    "name": c.name,
                    "status": c.status,
                    "cpu": f"{cpu_pct:.1f}%",
                    "ram": f"{int(ram_mb)}M",
                    "port": port_str
                })
            except: continue
                
        return sorted(details, key=lambda x: x['name'])