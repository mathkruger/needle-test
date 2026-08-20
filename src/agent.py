import needle
from tools.ping_tool import ping
from tools.get_system_usage_tool import get_system_usage
from tools.time_tool import get_time_tool

def init_agent() -> needle.Needle:
    return needle.Needle(tools=[ping, get_system_usage, get_time_tool])