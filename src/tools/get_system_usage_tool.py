import needle
import time

@needle.tool
def get_system_usage():
    "Get the current CPU and RAM usage on this machine."

    meminfo = {}
    with open("/proc/meminfo") as f:
        for line in f:
            parts = line.split()
            meminfo[parts[0].rstrip(":")] = int(parts[1])
    total_ram = meminfo["MemTotal"]
    available_ram = meminfo["MemAvailable"]
    used_ram = total_ram - available_ram

    def _read_cpu():
        with open("/proc/stat") as f:
            return [int(x) for x in f.readline().split()[1:]]
    t1 = _read_cpu()
    time.sleep(0.5)
    t2 = _read_cpu()
    idle_diff = t2[3] - t1[3]
    total_diff = sum(a - b for a, b in zip(t2, t1))

    return {
        "ram_total_mb": round(total_ram / 1024, 1),
        "ram_used_mb": round(used_ram / 1024, 1),
        "ram_available_mb": round(available_ram / 1024, 1),
        "ram_usage_percent": round(used_ram / total_ram * 100, 1),
        "cpu_core_count": len(t1),
        "cpu_usage_percent": round((1 - idle_diff / total_diff) * 100, 1),
        "__labels__": {
            "ram_total_mb": "RAM Total",
            "ram_used_mb": "RAM Used",
            "ram_available_mb": "RAM Available",
            "ram_usage_percent": "RAM Usage",
            "cpu_core_count": "CPU Cores",
            "cpu_usage_percent": "CPU Usage",
        },
    }