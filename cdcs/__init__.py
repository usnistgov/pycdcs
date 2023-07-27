# coding: utf-8
# Standard Python libraries
from importlib import resources

# Read version from VERSION file
if hasattr(resources, 'files'):
    __version__ = resources.files('cdcs').joinpath('VERSION').read_text(encoding='UTF-8')
else:
    __version__ = resources.read_text('cdcs', 'VERSION', encoding='UTF-8').strip()

# Local imports
from .date_parser import date_parser
from .aslist import aslist, iaslist
from .RestClient import RestClient
from .CDCS import CDCS

__all__ = ['__version__', 'date_parser', 'aslist', 'iaslist', 'RestClient', 'CDCS']
__all__.sort()
