# coding: utf-8
import sys

python3_version = sys.version_info.minor

# For >= 3.9, use importlib.resources.files
if python3_version >= 9:
    from importlib import resources
    __version__ = resources.files('cdcs').joinpath('VERSION').read_text(encoding='UTF-8')

# For intermediate versions, use importlib.resources.read_text
elif python3_version >= 7:
    from importlib import resources
    __version__ = resources.read_text('cdcs', 'VERSION', encoding='UTF-8').strip()

# For 3.6 and below, read file directly
else:
    from pathlib import Path
    with open(Path(Path(__file__).resolve().parent, 'VERSION'), encoding='UTF-8') as version_file:
        __version__ = version_file.read().strip()

# Local imports
from .date_parser import date_parser
from .aslist import aslist, iaslist
from .RestClient import RestClient
from .CDCS import CDCS

__all__ = ['__version__', 'date_parser', 'aslist', 'iaslist', 'RestClient', 'CDCS']