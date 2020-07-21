# coding: utf-8

# https://pandas.pydata.org/
import pandas as pd

def iaslist(term):
    """
    Iterate over items in term as if term was a list. Treats a str
    term as a single item.
    
    Args:
        term: (any) Term to iterate over.
    
    Yields:
        Items in the list representation of term.
    """
    if isinstance(term, (str, bytes, pd.Series)):
        yield term
    else:
        try:
            for t in term:
                yield t
        except:
            yield term
            
def aslist(term):
    """
    Create list representation of term. Treats a str term as a single
    item.
    
    Args:
        term: (any) Term to convert into a list, if needed.
        
    Returns:    
        list: All items in term as a list.
    """
    return [t for t in iaslist(term)]

