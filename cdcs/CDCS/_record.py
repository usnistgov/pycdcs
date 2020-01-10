
# Standard library imports
from pathlib import Path

# https://pandas.pydata.org/
import pandas as pd

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
        params['templates'] = []
        # Handle template series
        if isinstance(template, pd.Series):
            params['templates'].append({"id":template.id})
        
        # Handle template titles
        else:
            template = self.get_template(title=template)
            params['templates'].append({"id":template.id})
    
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

def upload_record(self, template, filename=None, content=None, title=None,
                    duplicatecheck=True):
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
        duplicatecheck: (bool, optional) If True (default), then a ValueError
            will be raised if a record already exists in the database with the
            same template and title.  If False, no check is performed possibly
            allowing for multiple records with the same title to exist in the
            database.
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
    
    if response.status_code == 201:
        record_id = response.json()['id']
        print(f'record {title} ({record_id}) successfully uploaded.')

def update_record(self, record=None, template=None, title=None, filename=None,
                  content=None):
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
        filename: (str or Path, optional) Path to file containing the new
            record content to upload. Either filename or content required.
        content: (str or bytes, optional) New content to upload. Either
            filename or content required.
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
    
    if response.status_code == 200:
        print(f'record {record.title} ({record.id}) has been updated.')


def delete_record(self, record=None, template=None, title=None):
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
    """
    if record is None:
        record = self.get_record(template=template, title=title)

    rest_url = f'/rest/data/{record.id}/'
    response = self.delete(rest_url)
    
    if response.status_code == 204:
        print(f'record {record.title} ({record.id}) has been deleted.')