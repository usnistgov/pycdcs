# coding: utf-8

# Standard library imports
from pathlib import Path
from typing import Optional, Union

from tqdm import tqdm

from IPython.display import display, HTML

# https://pandas.pydata.org/
import pandas as pd

from .. import aslist, date_parser

record_keys = ['id', 'template', 'workspace', 'user_id', 'title', 'xml_content',
               'creation_date', 'last_modification_date', 'last_change_date']

def get_records(self, template: Union[str, pd.Series, None] = None,
                title: Optional[str] = None,
                page: Optional[int] = None,
                parse_dates: bool = True,
                progress_bar: bool = True) -> pd.DataFrame:
    """
    Retrieves user records.

    Parameters
    ----------
    template : str or pandas.Series, optional
        The template or template title to limit the search by.
    title : str, optional
        The data record title to limit the search by.
    page : int or None, optional
        If an int, then will return results only for that page of 10 records.
        If None (default), then results for all pages will be compiled and
        returned.  Only used for CDCS versions 3.X.X.
    parse_dates : bool, optional
        If True (default) then date fields will automatically be parsed into
        pandas.Timestamp objects.  If False they will be left as str values.
    progress_bar : bool, optional
        If True (default) a progress bar will be displayed for multi-page
        query results. Only used for CDCS versions 3.X.X.

    Returns
    -------
    pandas.DataFrame
        All matching user records.
    """

    # Use old method for CDCS 2.X.X
    if self.cdcsversion[0] == 2:
        return self.get_records_v2(template=template, title=title,
        parse_dates=parse_dates)

    # Build params
    params = {}

    # Manage template
    if template is not None:
        
        # Handle template series
        if isinstance(template, pd.Series):
            params['template'] = template.id
            
        # Handle template titles
        else:
            template = self.get_template(title=template)
            params['template'] = template.id
            
    # Manage title
    if title is not None:
        params['title'] = title

    rest_url = '/rest/data/'

    # Get results from all pages
    if page is None:
        response = self.get(rest_url, params=params)
        response_json = response.json()
        records = response_json['results']
        
        if len(records) < response_json['count']:

            if progress_bar:
                pbar = tqdm(total=response_json['count'], initial=len(records))
        
            # Repeat post until all content received
            params['page'] = 2
            while response_json['next'] is not None:
                response = self.get(rest_url, params=params)
                response_json = response.json()
                newrecords = response_json['results']
                records.extend(newrecords)
                params['page'] += 1

                if progress_bar:
                    pbar.update(len(newrecords))
            
            if progress_bar:
                pbar.close()

            assert len(records) == response_json['count']
        
        records = pd.DataFrame(records)

    else:
        params['page'] = page
        response = self.get(rest_url, params=params)
        response_json = response.json()
        records = pd.DataFrame(response_json['results'])
        
    if len(records) == 0:
        records = pd.DataFrame(columns=record_keys)

    # Parse date fields
    if parse_dates and len(records) > 0:
        for key in ['creation_date', 'last_modification_date', 'last_change_date']:
            records[key] = records.apply(date_parser, args=[key], axis=1)
    
    return records

def get_records_v2(self, template: Union[str, pd.Series, None] = None,
                   title: Optional[str] = None,
                   parse_dates: bool = True) -> pd.DataFrame:
    """
    Retrieves user records for a CDCS version 2.X.X database.

    Parameters
    ----------
    template : str or pandas.Series, optional
        The template or template title to limit the search by.
    title : str, optional
        The data record title to limit the search by.
    parse_dates : bool, optional
        If True (default) then date fields will automatically be parsed into
        pandas.Timestamp objects.  If False they will be left as str values.
    
    Returns
    -------
    pandas.DataFrame
        All matching user records.
    """
    # Build params
    params = {}

    # Manage template
    if template is not None:
        
        # Handle template series
        if isinstance(template, pd.Series):
            params['template'] = template.id
            
        # Handle template titles
        else:
            template = self.get_template(title=template)
            params['template'] = template.id
            
    # Manage title
    if title is not None:
        params['title'] = title
    
    # Get response
    rest_url = '/rest/data/'
    response = self.get(rest_url, params=params)
    records = response.json()
    records = pd.DataFrame(records)
    if len(records) == 0:
        records = pd.DataFrame(columns=record_keys)
    
    # Parse date fields
    if parse_dates and len(records) > 0:
        for key in ['creation_date', 'last_modification_date', 'last_change_date']:
            records[key] = records.apply(date_parser, args=[key], axis=1)
    
    return records

def get_record(self, template: Union[str, pd.Series, None] = None,
               title: Optional[str] = None,
               parse_dates: bool = True) -> pd.Series:
    """
    Retrieves a single user record.  Given parameters must uniquely
    identify a record.

    Parameters
    ----------
    template : str or pandas.Series, optional
        The template or template title to limit the search by.
    title : str, optional
        The data record title to limit the search by.
    parse_dates : bool, optional
        If True (default) then date fields will automatically be parsed into
        pandas.Timestamp objects.  If False they will be left as str values.
        
    Returns
    -------
    pandas.Series
        The matching user record.

    Raises
    ------
    ValueError
        If no or multiple matching records found.
    """

    records = self.get_records(template=template, title=title,
                               parse_dates=parse_dates)
    
    # Check that number of records is exactly one.
    if len(records) == 1:
        return records.iloc[0]
    elif len(records) == 0:
        raise ValueError('No matching records found')
    else:
        raise ValueError('Multiple matching records found')

def assign_records(self, workspace: Union[str, pd.Series],
                   records: Union[pd.Series, pd.DataFrame, None] = None,
                   ids: Union[str, list, None] = None,
                   template: Union[str, pd.Series, None] = None,
                   title: Optional[str] = None,
                   verbose: bool = False):
    """
    Assigns one or more records to a workspace.

    Parameters
    ----------
    workspace : str or pandas.Series
        The workspace or workspace title to assign the records to.
    records : pandas.Series or pandas.DataFrame, optional
        Pre-selected records to assign to the workspace.  Cannot be given with
        ids, template, or title.
    ids : str or list, optional
        The ID(s) of the records to assign to the workspace.  Selecting records
        using ids has the least overhead. Cannot be given with records,
        template, or title.
    template : str or pandas.Series, optional
        The template or template title of records to assign to the workspace.
        Cannot be given with records or ids.
    title : str, optional
        The title of a record to assign to the workspace. Cannot be given with
        records or ids.
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.
    """
    # Get workspace id
    if isinstance(workspace, str):
        workspace = self.get_workspace(workspace)
    workspace_id = workspace.id
    
    # Get records from template and/or title
    if template is not None or title is not None:
        if records is not None or ids is not None:
            raise ValueError('template/title cannot be given with records or ids')
        records = get_records(self, template=template, title=title)

    # Get ids from records
    if records is not None:
        if ids is not None:
            raise ValueError('records and ids cannot both be given')
        if isinstance(records, pd.Series):
            ids = [records.id]
        elif isinstance(records, pd.DataFrame):
            ids = records.id.tolist()
        else:
            raise TypeError('invalid records type')
    
    if ids is None:
        raise ValueError('No records specified to assign to the workspace')

    # Assign records to the workspace
    for record_id in aslist(ids):
        rest_url = f'/rest/data/{record_id}/assign/{workspace_id}'
        response = self.patch(rest_url)

        if verbose and response.status_code == 200:
            print(f'record {record_id} assigned to workspace {workspace_id}')

def upload_record(self, template: Union[str, pd.Series],
                  filename: Optional[str] = None,
                  content: Union[str, bytes, None] = None,
                  title: Optional[str] = None,
                  workspace: Union[str, pd.Series] = None,
                  duplicatecheck: bool = True,
                  verbose: bool = False):
    """
    Adds a data record to the curator

    Parameters
    ----------
    template : str or pandas.Series
        The template or template title to associate with the record.
    filename : str, optional
        Name of an XML file whose contents are to be uploaded.  Either filename
        or content required.
    content : str or bytes, optional
        String content to upload. Either filename or content required.
    title : str, optional
        Title to save the record as.  Optional if filename is given (title will
        be taken as filename without ext).
    workspace : str or pandas.Series, optional
        If given, the record will be assigned to this workspace after
        successfully being uploaded.
    duplicatecheck : bool, optional
        If True (default), then a ValueError will be raised if a record already
        exists in the database with the same template and title.  If False, no
        check is performed possibly allowing for multiple records with the same
        title to exist in the database.
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.

    Raises
    ------
    ValueError
        If an improper or incomplete combination of filename, content, and
        title parameters are given, or if duplicatecheck=True and a record
        with the same title and template exist.
    TypeError
        If content is not str or bytes.
    """

    # Fetch template by title if needed
    if isinstance(template, str):
        template = self.get_template(title=template)
    
    # Load content from file
    if filename is not None:
        if content is not None:
            raise ValueError('filename and content cannot both be given')
        
        with open(filename, 'rb') as xmlfile:
            content = xmlfile.read()
            
        if title is None:
            title = Path(filename).stem
    
    elif content is not None:
        if title is None:
            raise ValueError('title must be given with content')
        
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
        
    else:
        raise ValueError('filename or content must be given')
    
    # Check if matching record already exists
    if duplicatecheck is True:
        matches = self.query(template=template, title=title)
        if len(matches) > 0:
            raise ValueError('Record with matching title and template found!')
    
    # Set data dict
    data = {
        'title': title, 
        'template': template.id, 
        'xml_content': content
    }
    
    rest_url = '/rest/data/'
    response = self.post(rest_url, data=data)
    
    if verbose and response.status_code == 201:
        record_id = response.json()['id']
        print(f'record {title} ({record_id}) successfully uploaded.')

    if workspace is not None:
        assign_records(self, workspace=workspace, ids=[response.json()['id']],
                       verbose=verbose)

def update_record(self, record: Optional[pd.Series] = None,
                  template: Union[str, pd.Series, None] = None,
                  title: Optional[str] = None,
                  filename: Union[str, Path, None] = None,
                  content: Union[str, bytes, None] = None,
                  workspace: Union[str, pd.Series, None] = None,
                  verbose: bool = False):
    """
    Updates the content for a single data record in the curator.

    Parameters
    ----------
    record : pandas.Series, optional
        A previously identified record to delete.  As this uniquely defines a
        record, the template and title parameters are ignored if given.
    template : str or pandas.Series, optional
        The template or template title associated with the record.  template +
        title values must uniquely identify one record.
    title : str, optional
        Title of the record to delete.  template + title values must uniquely
        identify one record.
    filename : str or Path, optional
        Path to file containing the new record content to upload. Either
        filename or content required.
    content : str or bytes, optional
        New content to upload. Either filename or content required.
    workspace : str or pandas.Series, optional
        If given, the record will be assigned to this workspace after
        successfully being updated.
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.
    """
    # Load content from file
    if filename is not None:
        if content is not None:
            raise ValueError('filename and content cannot both be given')
        
        with open(filename, 'rb') as xmlfile:
            content = xmlfile.read()
            
        if title is None:
            title = Path(filename).stem
    
    elif content is not None:
        
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
        
    else:
        raise ValueError('filename or content must be given')

    # Get matching record
    if record is None:
        record = self.get_record(template=template, title=title)
    
    # Set data dict
    data = {
        'xml_content': content
    }

    rest_url = f'/rest/data/{record.id}/'
    response = self.patch(rest_url, data=data)
    
    if verbose and response.status_code == 200:
        print(f'record {record.title} ({record.id}) has been updated.')
    
    if workspace is not None:
        assign_records(self, workspace=workspace, ids=[record.id],
                       verbose=verbose)

def delete_record(self, record: Optional[pd.Series] = None,
                  template: Union[str, pd.Series, None] = None,
                  title: Optional[str] = None,
                  verbose: bool = False):
    """
    Deletes a single data record from the curator.

    Parameters
    ----------
    record : pandas.Series, optional
        A previously identified record to delete.  As this uniquely defines a
        record, the other parameters are ignored.
    template : str or pandas.Series, optional
        The template or template title associated with the record.  template +
        title values must uniquely identify one record.
    title : str, optional
        Title of the record to delete.  template + title values must uniquely
        identify one record.
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.
    """
    if record is None:
        record = self.get_record(template=template, title=title)
    
    rest_url = f'/rest/data/{record.id}/'
    response = self.delete(rest_url)
    
    if verbose and response.status_code == 204:
        print(f'record {record.title} ({record.id}) has been deleted.')

def transform_record(self,
                     record: Optional[pd.Series] = None,
                     record_template: Optional[str] = None,
                     record_title: Optional[str] = None,
                     record_content: Union[str, bytes, None] = None,
                     record_filename: Union[str, Path, None] = None,
                     xslt: Optional[pd.Series] = None,
                     xslt_name: Optional[str] = None,
                     render_html: bool = False):
    """
    Transforms an XML record using an XSLT in the curator.  Note that this
    transformation is done by the curator and therefore involves at least one
    web request.  If the XML and XSLT files are local then it is likely more
    efficient to transform them locally (e.g. use lxml).
    
    Parameters
    ----------
    record : pandas.Series, optional
        The record information as retrieved from get_record(s) or query. Cannot
        be given with any other record parameter.
    record_template : str, optional
        The template title for a record to retrieve from the curator to render.
        The values of record_template and record_name together must uniquely 
        identify a record.  Cannot be given with record, record_content or
        record_filename.
    record_title : str, optional
        The record title for a record to retrieve from the curator to render.
        The values of record_template and record_name together must uniquely 
        identify a record.  Cannot be given with record, record_content or
        record_filename.
    record_content : str or bytes, optional
        Allows for XML content to be directly passed in.  Cannot be given with
        any other record parameter.
    record_filename : pathlike-object, optional
        Allows for XML content to be loaded from a local file. Cannot be given
        with any other record parameter.
    xslt : pandas.Series, optional
        The xslt information as retrieved from get_xslt(s).  Cannot be given
        with any other xslt parameter.
    xslt_name : str, optional
        The name associated with an xslt entry in the database.
    render_html : bool, optional
        If True, will use ipython's display options to render the transformed
        content as HTML.  This can be useful for ipython environments, such as
        Jupyter.  The default value of False will return the transformed
        contents as a str.

    Returns
    -------
    str
        The XML record contents as transformed by the XSLT.  Only returned when
        render_html=False.
    """
    
    # Extract record content from a record series
    if record is not None:
        try:
            assert record_template is None
            assert record_title is None
            assert record_content is None
            assert record_filename is None
        except AssertionError:
            raise ValueError('record cannot be given with any other record parameters')

        record_content = record.xml_content

    # Load record content from file
    elif record_filename is not None:
        if record_content is not None:
            raise ValueError('record_filename and record_content cannot both be given')
        if record_title is not None or record_template is not None:
            raise ValueError('record_filename cannot be given with record_title or record_template')
        
        with open(record_filename, 'rb') as xmlfile:
            record_content = xmlfile.read()
    
    # Convert record_content to str if needed
    elif record_content is not None:
        if record_title is not None or record_template is not None:
            raise ValueError('record_content cannot be given with record_title or record_template')
        
        # Encode str as bytes if needed
        if isinstance(record_content, str):
            try:
                e = record_content.index('?>')
            except:
                encoding = 'UTF-8'
            else:
                try:
                    s = record_content[:e].index('encoding') + 8
                except:
                    encoding = 'UTF-8'
                else:
                    s = record_content[s:e].index('"')+s+1
                    e = record_content[s:e].index('"') + s
                    encoding = record_content[s:e]
            record_content = record_content.encode(encoding)
        
        elif not isinstance(record_content, bytes):
            raise TypeError('record_content must be str or bytes')

    # Fetch record from curator
    else:
        record = self.get_record(title=record_title, template=record_template)
        record_content = record.xml_content

    # Extract xslt name from series
    if xslt is not None:
        if xslt_name is not None:
            raise ValueError('xslt and xslt_name cannot both be given')
    elif xslt_name is None:
        raise ValueError('xslt or xslt_name must be given')

    data = {}
    data['xslt_name'] = xslt_name
    data['xml_content'] = record_content

    rest_url = '/rest/xslt/transform/'
    response = self.post(rest_url, data=data)
    
    if render_html:
        display(HTML(response.text))
    else:
        return response.text