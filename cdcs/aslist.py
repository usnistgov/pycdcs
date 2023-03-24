# coding: utf-8

# Standard library imports
from typing import Any, Generator

# https://pandas.pydata.org/
import pandas as pd

def iaslist(term: Any) -> Generator[Any, None, None]:
    """
    Iterate over items in term as if term was a list. Treats a str
    term as a single item.
    
    Parameters
    ----------
    term : any
        Term to iterate over.
    
    Yields
    ------
    any
        Items in the list representation of term.
    """
    if isinstance(term, (str, bytes, pd.Series)):
        yield term
    else:
        try:
            for t in term:
                yield t
        except TypeError:
            yield term

def aslist(term: Any) -> list:
    """
    Create list representation of term. Treats a str term as a single
    item.
    
    Parameters
    ----------
    term : any
        Term to convert into a list, if needed.
        
    Returns
    -------
    list
        All items in term as a list.
    """
    return [t for t in iaslist(term)]
