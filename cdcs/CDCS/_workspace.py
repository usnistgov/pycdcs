# coding: utf-8

# Standard library imports
from typing import Optional

# https://pandas.pydata.org/
import pandas as pd

def get_workspaces(self, title:Optional[str]=None) -> pd.DataFrame:
    """
    Retrieves information for the existing workspaces.

    Parameters
    ----------
    title : str, optional
        The workspace title to limit the search by.
    
    Returns
    -------
    pandas.DataFrame
        The matching workspaces.
    """
    rest_url = '/rest/workspace/'
    response = self.get(rest_url)
    workspaces = pd.DataFrame(response.json())

    if title is not None:
        workspaces = workspaces[workspaces.title == title]

    return workspaces

def get_workspace(self, title:Optional[str]=None) -> pd.Series:
    """
    Retrieves a single workspace.  Given parameters must uniquely
    identify a workspace.

    Parameters
    ----------
    title : str, optional
        The workspace title to limit the search by.
    
    Returns
    -------
    pandas.Series
        The matching workspace.

    Raises
    ------
    ValueError
        If no or multiple matching workspaces found.
    """

    workspaces = self.get_workspaces(title=title)
    
    # Check that number of workspaces is exactly one.
    if len(workspaces) == 1:
        return workspaces.iloc[0]
    elif len(workspaces) == 0:
        raise ValueError('No matching workspaces found')
    else:
        raise ValueError('Multiple matching workspaces found')

@property
def global_workspace(self) -> pd.Series:
    """pandas.Series: The global public workspace"""
    return self.get_workspace(title='Global Public Workspace')