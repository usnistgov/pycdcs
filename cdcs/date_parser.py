# coding: utf-8

# https://pandas.pydata.org/
import pandas as pd

def date_parser(series: pd.Series,
                key: str) -> pd.Timestamp:
    """
    Parses iso date fields into Python objects. Can be used as a DataFrame
    apply function.

    Parameters
    ----------
    series : pandas.Series
        A series containing a date field represented in iso string format.
    key : str
        The name of the series field containing the iso string date.

    Returns
    -------
    pandas.Timestamp
        The date as an object
    """
    return pd.Timestamp(series[key])