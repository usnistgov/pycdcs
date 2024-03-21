from typing import Union
import contextlib

import pandas as pd

@property
def auto_set_pid(self) -> bool:
    """bool: Value of the auto_set_pid value"""
    rest_url = '/pid/rest/settings'
    response = self.get(rest_url)
    return response.json()['auto_set_pid']

@auto_set_pid.setter
def auto_set_pid(self, value):
    rest_url = '/pid/rest/settings/'
    data = {'auto_set_pid': value}
    response = self.patch(rest_url, data=data)

@contextlib.contextmanager
def auto_set_pid_off(self, work: bool = True):
    """
    Context manager that turns the auto_set_pid off within the context block,
    then turns it back on when the block is exited.  If you have records with
    PID URLs, auto_set_pid should be on to resolve the PIDs, but it should be
    off when uploading/updating records.  This context manager helps ensure
    that the appropriate setting changes are performed and supports the bulk
    uploading/updating of records.

    Parameters
    ----------
    work : bool, optional
        The default value of True will turn the auto_set_pid setting off and
        on as described above.  Setting work to False will make the context
        manager not work, i.e. do nothing.  This is simply a convenience for
        higher level functions to avoid performing unnecessary REST calls
        associated with changing the auto_set_pid if the records being added
        do not contain PID values or if the setting is being manually
        controlled elsewhere.  
    """
    if not isinstance(work, bool):
        raise TypeError('work must be a bool')
   
    if work:
        self.auto_set_pid = False
    try:
        yield
    finally:
        if work:
            self.auto_set_pid = True

def get_pid_xpaths(self, template: Union[str, pd.Series, None] = None) -> pd.DataFrame:
    """
    Retrieves the pid xpath values assigned to the templates.

    Parameters
    ----------
    template : str or pandas.Series, optional
        The template or template title to limit the search by.
    
    Returns
    -------
    pandas.DataFrame
        All matching user records.
    """
    # Fetch id of template if needed
    if template is not None:
        if isinstance(template, str):
            template = self.get_template(title=template)
        if not isinstance(template, pd.Series):
            raise TypeError('template must be a template title or pandas.Series')
    
    # Get response
    rest_url = '/pid/rest/settings/xpath/'
    response = self.get(rest_url)
    xpaths = response.json()
    xpaths = pd.DataFrame(xpaths)
    if len(xpaths) == 0:
        xpaths = pd.DataFrame(columns=['id', 'xpath', 'template'])
    
    if template is not None:
        xpaths = xpaths[xpaths.template == template.id]
        
    return xpaths

def get_pid_xpath(self, template: Union[str, pd.Series, None] = None) -> pd.Series:
    """
    Retrieves the pid xpath value assigned to a single template.

    Parameters
    ----------
    template : str or pandas.Series, optional
        The template or template title to limit the search by.
    
    Returns
    -------
    pandas.Series
        The matching user record.

    Raises
    ------
    ValueError
        If no or multiple matching xpath found.
    """

    xpaths = self.get_pid_xpaths(template=template)
    
    # Check that number of records is exactly one.
    if len(xpaths) == 1:
        return xpaths.iloc[0]
    elif len(xpaths) == 0:
        raise ValueError('No matching pid xpaths found')
    else:
        raise ValueError('Multiple matching pid xpaths found')
        
def upload_pid_xpath(self, template: Union[str, pd.Series], xpath: str):
    """
    Assigns a pid xpath to a template.

    Parameters
    ----------
    template : str or pandas.Series
        The template or template title.
    xpath : str
        The xpath to use for the pid field for the template.

    Raises
    ------
    ValueError
        If the template already has an pid xpath assigned to it.
    """
    # Fetch id of template
    if isinstance(template, str):
        template = self.get_template(title=template)
    if not isinstance(template, pd.Series):
        raise TypeError('template must be a template title or pandas.Series')

    # Check that template does not have an pid xpath assigned to it
    xpath_df = self.get_pid_xpaths(template=template)
    if len(xpath_df) > 0:
        raise ValueError(f'template {template.title} already has a pid xpath assigned to it.')

    # Set data based on arguments
    data = {}
    data['template'] = template.id
    data['xpath'] = xpath

    rest_url = '/pid/rest/settings/xpath/'
    response = self.post(rest_url, data=data)

def update_pid_xpath(self, template: Union[str, pd.Series], xpath: str):
    """
    Changes the pid xpath assigned to a template.

    Parameters
    ----------
    template : str or pandas.Series
        The template or template title.
    xpath : str
        The xpath to use for the pid field for the template.

    Raises
    ------
    ValueError
        If the template already has an pid xpath assigned to it.
    """
    # Fetch id of template
    #if isinstance(template, str):
    #    template = self.get_template(title=template)
    #if not isinstance(template, pd.Series):
    #    raise TypeError('template must be a template title or pandas.Series')

    # Check that template has an pid xpath assigned to it
    xpath_series = self.get_pid_xpath(template=template)

    # Set data based on arguments
    data = {}
    #data['template'] = template.id
    data['xpath'] = xpath

    rest_url = f'/pid/rest/settings/xpath/{xpath_series.id}/'
    response = self.patch(rest_url, data=data)

def delete_pid_xpath(self, template: Union[str, pd.Series]):
    """
    Deletes the pid xpath assigned to a template.

    Parameters
    ----------
    template : str or pandas.Series
        The template or template title.

    Raises
    ------
    ValueError
        If the template already has an pid xpath assigned to it.
    """
    # Fetch id of template
    #if isinstance(template, str):
    #    template = self.get_template(title=template)
    #if not isinstance(template, pd.Series):
    #    raise TypeError('template must be a template title or pandas.Series')

    # Check that template has an pid xpath assigned to it
    xpath_series = self.get_pid_xpath(template=template)

    rest_url = f'/pid/rest/settings/xpath/{xpath_series.id}/'
    response = self.delete(rest_url)