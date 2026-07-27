from importlib.metadata import version
__version__ = version('cdcs')

from .date_parser import date_parser
from .aslist import aslist, iaslist
from .RestClient import RestClient
from .CDCS import CDCS

__all__ = ['__version__', 'date_parser', 'aslist', 'iaslist', 'RestClient', 'CDCS']
