from .dut_shell import DutShell
from .ll_shell import LLShell
from .ll_mem_map_if import LLMemMapIf
from pathlib import Path

name = "riot_pal"
PHILIP_MEM_MAP_PATH = str(Path(__file__).parents[0]) + '/mem_map/philip_mem_map.csv'
