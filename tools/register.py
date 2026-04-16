from tools.builtins.edit_file import edit_file
from tools.builtins.read_file import read_file
from tools.builtins.run_bash import run_bash
from tools.builtins.web_search import web_search
from tools.builtins.write_file import write_file
from tools.origin.get_weather import get_weather

builtin_tools = [run_bash,read_file,edit_file,write_file,web_search]

ORIGIN_TOOLS = [get_weather]

ALL_TOOLS = builtin_tools + ORIGIN_TOOLS
