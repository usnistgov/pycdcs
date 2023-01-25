# coding: utf-8

# Standard library imports
from pathlib import Path
from typing import Optional, Union

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
    
def disable_template_manager(self,
                             title: Optional[str] = None,
                             template_manager: Optional[pd.Series] = None,
                             verbose: bool = False):
    """
    Disables a template manager (all versions of a template).
    
    Parameters
    ----------
    title : str, optional
        The template title.
    template_manager : pandas.Series, optional
        Template manager information for the template.  This can be given instead
        of title to avoid querying for the template manager.
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.
    """
    
    if title is not None:
        # Check that title and template_manager are not both given
        if template_manager is not None:
            raise ValueError('title and template_manager cannot both be given')

        # Fetch template manager
        template_manager = self.get_template_managers(title).loc[0]

    # Check that template_manager is given if title is not
    elif template_manager is None:
        raise ValueError('title or template_manager must be given')
        
    if template_manager.is_disabled:
        raise ValueError('template manager already disabled')

    manager_id = template_manager["id"]
    self.patch(f'/rest/template-version-manager/{manager_id}/disable/')
    
    if verbose:
        print(f'template manager with id {manager_id} disabled')

def restore_template_manager(self,
                             title: Optional[str] = None,
                             template_manager: Optional[pd.Series] = None,
                             verbose: bool = False):
    """
    Restores a disabled template manager.
    
    Parameters
    ----------
    title : str, optional
        The template title.
    template_manager : pandas.Series, optional
        Template manager information for the template.  This can be given instead
        of title to avoid querying for the template manager.
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.
    """
    
    if title is not None:
        # Check that title and template_manager are not both given
        if template_manager is not None:
            raise ValueError('title and template_manager cannot both be given')

        # Fetch template manager
        template_manager = self.get_template_managers(title).loc[0]

    # Check that template_manager is given if title is not
    elif template_manager is None:
        raise ValueError('title or template_manager must be given')

    if not template_manager.is_disabled:
        raise ValueError('template manager already active')

    manager_id = template_manager["id"]
    self.patch(f'/rest/template-version-manager/{manager_id}/restore/')

    if verbose:
        print(f'template manager with id {manager_id} restored')

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

def upload_template(self,
                    filename: Optional[str] = None,
                    content: Union[str, bytes, None] = None,
                    title: Optional[str] = None,
                    useronly: bool = False,
                    verbose: bool = False):
    """
    Uploads a new template schema to the curator.  Use update_template if a
    template already exists with the wanted title.

    Parameters
    ----------
    filename : str, optional
        Name of the XSD schema file to upload for the template.  Optional if title
        is given (filename will be taken as "title".xsd).
    content : str or bytes, optional
        String contents of an XSD schema file to upload for the template.  Optional
        if filename is given as a full path to the XSD file.
    title : str, optional
        Title to save the template as.  Optional if filename is given (title will
        be taken as filename without ext).
    useronly : bool, optional
        If True, the template will be associated only with the user. If False (default),
        it will be made a global template.
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.

    Raises
    ------
    ValueError
        If an improper or incomplete combination of filename, content, and
        title parameters are given, or if a template with the same title already exists.
    TypeError
        If content is not str or bytes.
    """
    
    # Check if filename has been given
    if filename is not None:
        
        # Load content if needed
        if content is None:
            with open(filename, 'rb') as xmlfile:
                content = xmlfile.read()
        
        # Set title if needed
        if title is None:
            title = Path(filename).stem
        
        # Remove directory path from filename
        filename = Path(filename).name
    
    elif title is not None:
        filename = title + '.xsd'
        
    else:
        raise ValueError('filename or title must be given')
        
    if content is None:
        raise ValueError('filename or content must be given')
    
    if title in self.template_titles:
        raise ValueError(f'template {title} already exists')

    # Encode str as bytes if needed
    if isinstance(content, str):
        try:
            e = content.index('?>')
        except:
            encoding = 'UTF-8'
        else:
            try:
                s = content[:e].index('encoding') + 8
            except:
                encoding = 'UTF-8'
            else:
                s = content[s:e].index('"')+s+1
                e = content[s:e].index('"') + s
                encoding = content[s:e]
        content = content.encode(encoding)

    elif not isinstance(content, bytes):
        raise TypeError('content must be str or bytes')
    
    # Set data dict
    data = {
        'title': title, 
        'filename': filename, 
        'content': content
    }
    # Set rest url based on useronly
    if useronly:
        rest_url = '/rest/template/user/'
    else:
        rest_url = '/rest/template/global/'

    # Send request
    response = self.post(rest_url, data=data)
    
    if verbose and response.status_code == 201:
        template_id = response.json()['id']
        print(f'template {title} ({template_id}) successfully uploaded.')

def update_template(self,
                    filename: Optional[str] = None,
                    content: Union[str, bytes, None] = None,
                    title: Optional[str] = None,
                    template_manager: Optional[pd.Series] = None,
                    #validate: bool = False,
                    #migrate: bool = False,
                    set_current: bool = True,
                    disable_old: bool = False,
                    verbose: bool = False):
    """
    Uploads a new version of a template schema to the curator.

    Parameters
    ----------
    filename : str, optional
        Name of the XSD schema file to upload for the template.  Optional if title
        is given (filename will be taken as "title".xsd).
    content : str or bytes, optional
        String contents of an XSD schema file to upload for the template.  Optional
        if filename is given as a full path to the XSD file.
    title : str, optional
        Title to save the template as.  Optional if filename is given (title will
        be taken as filename without ext).
    template_manager : pandas.Series, optional
        Can be given instead of title if the template_manager info has already been
        retrieved from the database.
    validate : bool, optional 
        NOT IMPLEMENTED YET! If True, all records in the current active version of the template will be validated against
        the newly uploaded version to determine if migration is possible. Default value is False.
    migrate : bool, optional
        NOT IMPLEMENTED YET! If True, will attempt to migrate all records in the current active version to the newly
        uploaded version.  Default value is False.
    set_current : bool, optional
        If True (default), will set the uploaded version of the template to be the current
        active version.
    disable_old : bool, optional
        If True, all active old versions of the template will be disabled. Default value is False.
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.

    Raises
    ------
    ValueError
        If an improper or incomplete combination of filename, content, and
        title parameters are given, or if a template with the same title already exists.
    TypeError
        If content is not str or bytes.
    """
    
    # Check if filename has been given
    if filename is not None:
        
        # Load content if needed
        if content is None:
            with open(filename, 'rb') as xmlfile:
                content = xmlfile.read()
        
        # Set title if needed
        if title is None:
            if template_manager is None:
                title = Path(filename).stem
            else:
                title = template_manager.title
        
        # Remove directory path from filename
        filename = Path(filename).name
    
    elif title is not None:
        filename = title + '.xsd'
        
    else:
        raise ValueError('filename or title must be given')
        
    if content is None:
        raise ValueError('filename or content must be given')
    
    # Get template manager
    if template_manager is None:
        template_managers = self.get_template_managers(title=title)
        if len(template_managers) == 1:
            template_manager = template_managers.iloc[0]
        else:
            raise ValueError(f'template {title} does not exist')
    
    # Encode str as bytes if needed
    if isinstance(content, str):
        try:
            e = content.index('?>')
        except:
            encoding = 'UTF-8'
        else:
            try:
                s = content[:e].index('encoding') + 8
            except:
                encoding = 'UTF-8'
            else:
                s = content[s:e].index('"')+s+1
                e = content[s:e].index('"') + s
                encoding = content[s:e]
        content = content.encode(encoding)

    elif not isinstance(content, bytes):
        raise TypeError('content must be str or bytes')
    
    # Set data dict
    data = {
        'filename': filename, 
        'content': content
    }
    # Set rest url based on useronly
    rest_url = f'/rest/template-version-manager/{template_manager["id"]}/version/'

    # Send request
    response = self.post(rest_url, data=data)
    
    template_id = response.json()['id']
    if verbose and response.status_code == 201:
        print(f'template {title} ({template_id}) successfully uploaded.')
    
    # Set new version as the current template
    if set_current:
        self.set_current_template(template_id=template_id, verbose=verbose)
    
    # Disable all old versions of the template
    if disable_old:
        for version in template_manager.versions:
            
            # Skip already disabled versions
            if version in template_manager.disabled_versions:
                continue
                
            # Skip "current" version if new version was not set as current
            if version == template_manager.current and not set_current:
                continue
            
            # Disable the old version
            self.disable_template(template_id=version, verbose=verbose)

def disable_template(self,
                     title: Optional[str] = None,
                     version: Optional[int] = None,
                     template_manager: Optional[pd.Series] = None,
                     template_id: Optional[str] = None,
                     verbose: bool = False):
    """
    Disables a non-current version of a template.
    
    Parameters
    ----------
    title : str, optional
        The template title.
    version : int, optional
        The version of the template to disable.  Required unless template_id is
        given.  Note that version numbers start at 1.
    template_manager : pandas.Series, optional
        Template manager information for the template.  This can be given instead
        of title to avoid querying for the template manager.
    template_id : str, optional
        The database id for the template to disable.  If given, then no other
        parameters are allowed (or needed).
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.
    """
    
    # Check if template_id is given with any other parameters
    if template_id is not None:
        if template_manager is not None:
            raise ValueError('template_id and template_manager cannot both be given')
        if title is not None:
            raise ValueError('template_id and title cannot both be given')
        if version is not None:
            raise ValueError('template_id and version cannot both be given')
    
    else:
        if title is not None:
            # Check that title and template_manager are not both given
            if template_manager is not None:
                raise ValueError('title and template_manager cannot both be given')
            
            # Fetch template manager
            template_manager = self.get_template_managers(title).loc[0]

        # Check that template_manager is given if title is not
        elif template_manager is None:
            raise ValueError('title, template_manager or template_id must be given')
        
        # Check value of version
        if version is None:
            raise ValueError('version is required with title or template_manager')
        elif version < 1 or version > len(template_manager.versions):
            raise IndexError('version number out of range')

        # Get template id
        template_id = template_manager.versions[version-1]

        if template_id == template_manager.current:
            raise ValueError('cannot disable the current template version')
            
        if template_id in template_manager.disabled_versions:
            raise ValueError('template version already disabled')

    self.patch(f'/rest/template/version/{template_id}/disable/')
    
    if verbose:
        print(f'template with id {template_id} disabled')
    
def restore_template(self,
                     title: Optional[str] = None,
                     version: Optional[int] = None,
                     template_manager: Optional[pd.Series] = None,
                     template_id: Optional[str] = None,
                     verbose: bool = False):
    """
    Restores a disabled version of a template.
    
    Parameters
    ----------
    title : str, optional
        The template title.
    version : int, optional
        The version of the template to restore.  Required unless template_id is
        given.  Note that version numbers start at 1.
    template_manager : pandas.Series, optional
        Template manager information for the template.  This can be given instead
        of title to avoid querying for the template manager.
    template_id : str, optional
        The database id for the template to restore.  If given, then no other
        parameters are allowed (or needed).
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.
    """
    
    # Check if template_id is given with any other parameters
    if template_id is not None:
        if template_manager is not None:
            raise ValueError('template_id and template_manager cannot both be given')
        if title is not None:
            raise ValueError('template_id and title cannot both be given')
        if version is not None:
            raise ValueError('template_id and version cannot both be given')
    
    else:
        if title is not None:
            # Check that title and template_manager are not both given
            if template_manager is not None:
                raise ValueError('title and template_manager cannot both be given')
            
            # Fetch template manager
            template_manager = self.get_template_managers(title).loc[0]

        # Check that template_manager is given if title is not
        elif template_manager is None:
            raise ValueError('title, template_manager or template_id must be given')
        
        # Check value of version
        if version is None:
            raise ValueError('version is required with title or template_manager')
        elif version < 1 or version > len(template_manager.versions):
            raise IndexError('version number out of range')

        # Get template id
        template_id = template_manager.versions[version-1]

        if template_id not in template_manager.disabled_versions:
            raise ValueError('template version already active')

    self.patch(f'/rest/template/version/{template_id}/restore/')

    if verbose:
        print(f'template with id {template_id} restored')

def set_current_template(self,
                         title: Optional[str] = None,
                         version: Optional[int] = None,
                         template_manager: Optional[pd.Series] = None,
                         template_id: Optional[str] = None,
                         verbose: bool = False):
    """
    Sets an active version of a template as the current version.
    
    Parameters
    ----------
    title : str, optional
        The template title.
    version : int, optional
        The version of the template to make current.  Required unless template_id is
        given.  Note that version numbers start at 1.
    template_manager : pandas.Series, optional
        Template manager information for the template.  This can be given instead
        of title to avoid querying for the template manager.
    template_id : str, optional
        The database id for the template to set as current.  If given, then no other
        parameters are allowed (or needed).
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.
    """
    
    # Check if template_id is given with any other parameters
    if template_id is not None:
        if template_manager is not None:
            raise ValueError('template_id and template_manager cannot both be given')
        if title is not None:
            raise ValueError('template_id and title cannot both be given')
        if version is not None:
            raise ValueError('template_id and version cannot both be given')
    
    else:
        if title is not None:
            # Check that title and template_manager are not both given
            if template_manager is not None:
                raise ValueError('title and template_manager cannot both be given')
            
            # Fetch template manager
            template_manager = self.get_template_managers(title).loc[0]

        # Check that template_manager is given if title is not
        elif template_manager is None:
            raise ValueError('title, template_manager or template_id must be given')
        
        # Check value of version
        if version is None:
            raise ValueError('version is required with title or template_manager')
        elif version < 1 or version > len(template_manager.versions):
            raise IndexError('version number out of range')

        # Get template id
        template_id = template_manager.versions[version-1]

        if template_id == template_manager.current:
            raise ValueError('template version is already current')
            
        if template_id in template_manager.disabled_versions:
            raise ValueError('template version is disabled')

    self.patch(f'/rest/template/version/{template_id}/current/')

    if verbose:
        print(f'template with id {template_id} set as current version')