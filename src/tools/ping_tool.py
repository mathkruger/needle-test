import needle

@needle.tool
def ping(times: int):
    "run a ping and return pong for an amount of times"

    return {
        "result": ("pong " * times),
        "__labels__": {"result": "Response"},
    }