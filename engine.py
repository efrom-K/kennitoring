import psutil
import docker
import datetime
import os

class MonitorEngine:
    def __init__(self):
        # Принудительно задаем путь к хостовому proc, если мы в Docker
        if os.environ.get('PROCFS_PATH'):
            psutil.PROCFS_PATH = os.environ.get('PROCFS_PATH')
            
        try:
            # Используем стандартный сокет, который ты пробросил в volumes
            self.docker_client = docker.from_env()
        except:
            self.docker_client = None

    def get_system_metrics(self):
        vm = psutil.virtual_memory()
        temps = psutil.sensors_temperatures()
        
        # Для NUC6 J3455 обычно используется coretemp или acpitz
        core_temp = 0
        if 'coretemp' in temps:
            core_temp = temps['coretemp'][0].current
        elif 'acpitz' in temps:
            core_temp = temps['acpitz'][0].current
        
        net = {}
        try:
            # Исключаем виртуальные интерфейсы Docker, чтобы не двоить трафик
            for nic, stats in psutil.net_io_counters(pernic=True).items():
                if not nic.startswith(('veth', 'br-', 'docker', 'lo', 'wg')):
                    net[nic] = stats
        except: pass

        return {
            "cpu": psutil.cpu_percent(interval=None),
            "temp": core_temp,
            "ram": vm.percent,
            "ram_used": vm.used / (1024**3),
            "ram_total": vm.total / (1024**3),
            "uptime": int((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds() // 3600),
            # Фильтруем loop-устройства и системные разделы
            "disks": {p.mountpoint: psutil.disk_usage(p.mountpoint) 
                      for p in psutil.disk_partitions() 
                      if 'loop' not in p.device and '/snap/' not in p.mountpoint},
            "net": net
        }

    def get_container_details(self):
        if not self.docker_client: return []
        details = []
        
        # Получаем количество ядер для корректного расчета CPU %
        cpu_count = psutil.cpu_count() or 1
        
        for c in self.docker_client.containers.list():
            try:
                # stream=False берет один снимок метрик
                s = c.stats(stream=False)
                
                # Расчет CPU % (учитываем дельту между двумя измерениями внутри Docker API)
                cpu_delta = s['cpu_stats']['cpu_usage']['total_usage'] - s['precpu_stats']['cpu_usage']['total_usage']
                sys_delta = s['cpu_stats']['system_cpu_usage'] - s['precpu_stats']['system_cpu_usage']
                
                if sys_delta > 0 and cpu_delta > 0:
                    # Умножаем на количество ядер, как это делает docker stats
                    cpu_pct = (cpu_delta / sys_delta) * cpu_count * 100.0
                else:
                    cpu_pct = 0.0

                # Расчет RAM
                ram_usage = s['memory_stats'].get('usage', 0)
                # Вычитаем кеш, чтобы получить честное потребление (как в htop/docker stats)
                cache = s['memory_stats'].get('stats', {}).get('inactive_file', 0)
                ram_mb = (ram_usage - cache) / (1024**2)

                # Вытягиваем порты
                p_map = c.attrs.get('NetworkSettings', {}).get('Ports', {})
                ports = []
                if p_map:
                    for p in p_map:
                        if p_map[p]:
                            ports.append(p_map[p][0]['HostPort'])
                
                port_str = f":{','.join(ports)}" if ports else ""

                details.append({
                    "name": c.name,
                    "status": c.status,
                    "cpu": f"{cpu_pct:.1f}%",
                    "ram": f"{int(ram_mb)}M",
                    "port": port_str
                })
            except Exception:
                continue
                
        return sorted(details, key=lambda x: x['name'])