# coding: utf-8
# Read version from VERSION file
try:
    from importlib import resources
except:
    from pathlib import Path
    with open(Path(Path(__file__).resolve().parent, 'VERSION')) as version_file:
        __version__ = version_file.read().strip()
else:
    __version__ = resources.read_text('cdcs', 'VERSION').strip()


# Local imports
from .date_parser import date_parser
from .aslist import aslist, iaslist
from .RestClient import RestClient
from .CDCS import CDCS