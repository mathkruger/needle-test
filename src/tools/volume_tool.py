import needle
import subprocess
from typing import Annotated
from needle import Field

@needle.tool
def set_volume(level: Annotated[int, Field(ge=0, le=100)]):
    "Set the computer audio volume to a specific level (0-100)."

    try:
        subprocess.run(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"],
            check=True,
            capture_output=True,
        )
        return {
            "level": level,
            "status": "ok",
            "__labels__": {"level": "Volume", "status": "Status"},
        }
    except FileNotFoundError:
        return {"error": "pactl not found. Install PulseAudio: sudo apt install pulseaudio"}
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to set volume: {e.stderr.decode().strip()}"}
