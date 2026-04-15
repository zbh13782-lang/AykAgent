from tools.local.edit_file import edit_file
from tools.local.read_file import read_file
from tools.local.run_bash import run_bash
from tools.local.write_file import write_file
from tools.origin.get_weather import get_weather

LOCAL_TOOLS = [run_bash,read_file,edit_file,write_file]

ORIGIN_TOOLS = [get_weather]

ALL_TOOLS = LOCAL_TOOLS + ORIGIN_TOOLS
