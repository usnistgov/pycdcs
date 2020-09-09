# coding: utf-8

# Standard library imports
from pathlib import Path

# https://pandas.pydata.org/
import pandas as pd

from ..aslist import aslist

def get_records(self, template=None, title=None):
    """
    Retrieves user records.

    Args:
        template: (str or pandas.Series, optional) The template or template
            title to limit the search by.
        title: (str, optional) The data record title to limit the search
            by.
    
    Returns:
        pandas.DataFrame: All matching user records.
    """
    # Build params
    params = {}

    # Manage template
    if template is not None:
        #params['templates'] = []
        # Handle template series
        if isinstance(template, pd.Series):
            params['template'] = template.id
            #params['templates'].append({"id":template.id})
        
        # Handle template titles
        else:
            template = self.get_template(title=template)
            params['template'] = template.id
            #params['templates'].append({"id":template.id})
    
    # Manage title
    if title is not None:
        params['title'] = title
    
    # Get response
    rest_url = '/rest/data/'
    response = self.get(rest_url, params=params)
    records = response.json()
    records = pd.DataFrame(records)
    return records

def get_record(self, template=None, title=None):
    """
    Retrieves a single user record.  Given parameters must uniquely
    identify a record.

    Args:
        template: (str or pandas.Series, optional) The template or template
            title to limit the search by.
        title: (str, optional) The data record title to limit the search
            by.
    
    Returns:
        pandas.Series: The matching user record.

    Raises:
        ValueError: If no or multiple matching records found.
    """

    records = self.get_records(template=template, title=title)
    
    # Check that number of records is exactly one.
    if len(records) == 1:
        return records.iloc[0]
    elif len(records) == 0:
        raise ValueError('No matching records found')
    else:
        raise ValueError('Multiple matching records found')

def assign_records(self, workspace, records=None, ids=None, template=None,
                   title=None, verbose=False):
    """
    Assigns one or more records to a workspace.

    Args:
        workspace: (str or pandas.Series) The workspace or workspace title to
            assign the records to.
        records: (pandas.Series or pandas.DataFrame, optional) Pre-selected
            records to assign to the workspace.  Cannot be given with ids,
            template, or title.
        ids: (str or list, optional) The ID(s) of the records to assign to the
            workspace.  Selecting records using ids has the least overhead.
            Cannot be given with records, template, or title.
        template: (str or pandas.Series, optional) The template or template
            title of records to assign to the workspace.  Cannot be given with
            records or ids.
        title: (str, optional) The title of a record to assign to the
            workspace. Cannot be given with records or ids.
        verbose (bool, optional) Setting this to True will print extra
            status messages.  Default value is False.
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
    
    # Assign records to the workspace
    for record_id in aslist(ids):
        rest_url = f'/rest/data/{record_id}/assign/{workspace_id}'
        response = self.patch(rest_url)

        if verbose and response.status_code == 200:
            print(f'record {record_id} assigned to workspace {workspace_id}')

def upload_record(self, template, filename=None, content=None, title=None,
                  workspace=None, duplicatecheck=True, verbose=False):
    """
    Adds a data record to the curator

    Args:
        template: (str or pandas.Series) The template or template title to
            associate with the record.
        filename: (str, optional) Name of an XML file whose contents are to be
            uploaded.  Either filename or content required.
        content: (str or bytes, optional) String content to upload. Either
            filename or content required.
        title: (str, optional) Title to save the record as.  Optional if
            filename is given (title will be taken as filename without ext).
        workspace (str or pandas.Series, optional) If given, the record will be
            assigned to this workspace after successfully being uploaded.
        duplicatecheck: (bool, optional) If True (default), then a ValueError
            will be raised if a record already exists in the database with the
            same template and title.  If False, no check is performed possibly
            allowing for multiple records with the same title to exist in the
            database.
        verbose: (bool, optional) Setting this to True will print extra
            status messages.  Default value is False.
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

def update_record(self, record=None, template=None, title=None, filename=None,
                  content=None, workspace=None, verbose=False):
    """
    Updates the content for a single data record in the curator.

    Args:
        record: (pandas.Series, optional) A previously identified record to
            delete.  As this uniquely defines a record, the template and title
            parameters are ignored if given.
        template: (str or pandas.Series, optional) The template or template
            title associated with the record.  template + title values must
            uniquely identify one record.
        title: (str, optional) Title of the record to delete.  template +
            title values must uniquely identify one record.
        filename: (str or Path, optional) Path to file containing the new
            record content to upload. Either filename or content required.
        content: (str or bytes, optional) New content to upload. Either
            filename or content required.
        workspace (str or pandas.Series, optional) If given, the record will be
            assigned to this workspace after successfully being updated.
        verbose: (bool, optional) Setting this to True will print extra
            status messages.  Default value is False.
    """
    # Load content from file
    if filename is not None:
        if content is not None:
            raise ValueError('filename and content cannot both be given')
        
        with open(filename, 'rb') as xmlfile:
            content = xmlfile.read()
            
        if title is None:
            title = Path(filename).stem
    
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

def delete_record(self, record=None, template=None, title=None, verbose=False):
    """
    Deletes a single data record from the curator.

    Args:
        record: (pandas.Series, optional) A previously identified record to
            delete.  As this uniquely defines a record, the other parameters
            are ignored.
        template: (str or pandas.Series, optional) The template or template
            title associated with the record.  template + title values must
            uniquely identify one record.
        title: (str, optional) Title of the record to delete.  template +
            title values must uniquely identify one record.
        verbose: (bool, optional) Setting this to True will print extra
            status messages.  Default value is False.
    """
    if record is None:
        record = self.get_record(template=template, title=title)

    rest_url = f'/rest/data/{record.id}/'
    response = self.delete(rest_url)
    
    if verbose and response.status_code == 204:
        print(f'record {record.title} ({record.id}) has been deleted.')