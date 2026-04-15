from tools.local.run_bash import run_bash
from tools.origin.get_weather import get_weather

LOCAL_TOOLS = [run_bash]

ORIGIN_TOOLS = [get_weather]

ALL_TOOLS = LOCAL_TOOLS + ORIGIN_TOOLS
