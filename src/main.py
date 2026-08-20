import time
import needle

@needle.tool
def ping(times: int):
    "run a ping and return pong for an amount of times"

    return {"result": ("pong " * times)}

@needle.tool
def get_weather(city: str):
    "Get the current weather for a city."
    return {"city": city, "temp_c": 27, "sky": "clear"}

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
    }

agent = needle.Needle(tools=[ping, get_weather, get_system_usage])

prompt = ""
while prompt != "exit":
    prompt = input(">")
    if prompt != "exit":
        result = agent.run(prompt)
        print("Reasoning:", result["reasoning"])
        print("Results:", result["results"])
    else:
        print("bye!")

