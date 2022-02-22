# coding: utf-8

# Standard library imports
from typing import Optional

# https://pandas.pydata.org/
import pandas as pd

def get_template_managers(self, title: Optional[str] = None,
                          is_disabled: bool = False,
                          useronly: bool = False) -> pd.DataFrame:
    """
    Get template managers from a curator

    Parameters
    ----------
    title : str, optional
        The template title to limit the search by.
    is_disabled : bool, optional
        If True, then disabled templates will be returned.  If False (default),
        then active templates will be returned.
    useronly : bool, optional
        If True, only a user's templates are returned. If False (default),
        then all global templates are returned.

    Returns
    -------
    pandas.DataFrame
        All template managers.

    Raises
    ------
    TypeError
        If useronly is not bool.
    """
    # Set url based on useronly value
    if useronly is False:
        rest_url = '/rest/template-version-manager/global/'
    elif useronly is True:
        rest_url = '/rest/template-version-manager/user/'
    else:
        raise TypeError('useronly must be bool')

    # Set params dict based on arguments
    params = {}
    if title is not None:
        params['title'] = title
    if is_disabled is True:
        params['is_disabled'] = is_disabled
    
    # Get response
    response = self.get(rest_url, params=params)
    template_managers = pd.DataFrame(response.json())
    
    return template_managers
    
def get_templates(self, title: Optional[str] = None,
                  is_disabled: bool = False,
                  current: bool = True,
                  useronly: bool = False) -> pd.DataFrame:
    """
    Get all templates from a curator.

    Parameters
    ----------
    title : str, optional
        The template title to limit the search by.
    is_disabled : bool, optional
        If True, then disabled templates will be returned.  If False (default),
        then active templates will be returned.
    current : bool, optional
        If True (default), only current template versions will be returned.
    useronly : bool, optional
        If True, only a user's templates are returned. If False (default),
        then all global templates are returned.

    Returns
    -------
    pandas.DataFrame
        All current templates.
    """

    # Get template managers
    template_managers = self.get_template_managers(title=title,
                                                   is_disabled=is_disabled,
                                                   useronly=useronly)      
    if len(template_managers) > 0:
        # Get all current templates
        if current is True:
            templates = []
            for current_id in template_managers.current:

                # Set url and get response
                rest_url = f'/rest/template/{current_id}/'
                response = self.get(rest_url)
                templates.append(response.json())
            templates = pd.DataFrame(templates)

            # Add title to content
            templates['title'] = template_managers.title

        # Get all templates
        elif current is False:
            templates = []
            for template_manager in template_managers.itertuples():
                for version_id in template_manager.versions:

                    # Set url and get response
                    rest_url = f'/rest/template/{version_id}/'
                    response = self.get(rest_url)

                    # Add title to content
                    content = response.json()
                    content['title'] = template_manager.title
                    templates.append(content)

            templates = pd.DataFrame(templates)

        else:
            raise TypeError('current must be bool')
    else:
        templates = pd.DataFrame([])
            
    return templates

def get_template(self, title: Optional[str] = None,
                 is_disabled: bool = False,
                 current: bool = True,
                 useronly: bool = False) -> pd.Series:
    """
    Gets a single template from a curator.

    Parameters
    ----------
    title : str, optional
        The template title to limit the search by.
    is_disabled : bool, optional
        If True, then disabled templates will be returned.  If False (default),
        then active templates will be returned.
    current : bool, optional
        If True (default), only current template versions will be returned.
    useronly : bool, optional
        If True, only a user's templates are returned. If False (default), then
        all global templates are returned.

    Returns
    -------
    pandas.Series
        The matching template.

    Raises
    ------
    ValueError
        If no template named title found.
    """

    # Get templates 
    templates = self.get_templates(title=title, is_disabled=is_disabled,
                                    current=current, useronly=useronly)

    # Check that number of templates is exactly one.
    if len(templates) == 1:
        return templates.iloc[0]
    elif len(templates) == 0:
        raise ValueError('No matching template found')
    else:
        raise ValueError('Multiple matching templates found')

@property
def template_titles(self) -> list:
    """list: All template titles"""
    return self.get_template_managers().title.tolist()